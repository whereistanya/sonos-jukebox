#!/usr/bin/python2.7
"""
Operate your Sonos with Amazon Dash buttons.

Listen for ARP traffic from your Amazon Dash buttons. Serve a directory of
MP3s over HTTP, so you can choose and play them. The directory name is
currently hard coded in main().
"""


import logging
import os
import sys
import time
import urllib
import scapy.all as scapy
from threading import Thread

import buttons
import localwebserver
import my_ip
import sonos

class Sniffer(Thread):
  """Sniffs for arp traffic and takes actions based on what it gets."""

  def __init__(self, local_uri, player):
    """Start sniffing the network.

    Args:
      local_uri: (str) URL of the server with the MP3s. e.g., http://host:port/
      player: (sonos.Player) An initialised sonos.Player, which knows about
              your devices.
    """
    self.webserver = local_uri
    self.player = player
    self.last_seen = {}  # For de-duping button clicks.

  def run_forever(self):
    """Sniff network traffic. Call arp_cb() against any arp packets."""
    scapy.sniff(prn=self.arp_cb, filter="arp", store=0, count=0)


  def arp_cb(self, packet):
    """Check whether this is a button we know and handle it."""
    if not packet.haslayer(scapy.ARP):
      return
    if packet[scapy.ARP].op != 1: # who-has (request)
      return
    mac = packet[scapy.ARP].hwsrc

    try:
      button_name = buttons.MACS[mac]
      logging.warning("found button %s at mac address %s", button_name, mac)
      self.handle_button(button_name)
    except KeyError:
      return   # It was some device we don't care about


  def handle_button(self, button):
    """Parse and execute the button's command."""
    last_run = self.last_seen[button] if button in self.last_seen else 0
    diff = time.time() - last_run

    if diff <= 1:
      logging.warning("duplicate: %s, %d, %d", button, last_run, diff)
      return

    try:
      cmd = buttons.COMMANDS[button]
    except KeyError:
      logging.warning("No instructions found for button %s.", button)
      return
    self.last_seen[button] = time.time()

    try:
      function, music, zone = cmd
    except ValueError, ex:
      logging.warning("Couldn't parse instructions from %s: %s", cmd, ex)
      return

    if function == "play_local":
      # Look at all the files in the specified directory and add their URIs.
      mp3s = []
      files = os.listdir(music)
      for filename in files:
        if filename.endswith(".mp3"):
          mp3s.append(os.path.join(self.webserver, music,
                                   urllib.pathname2url(filename)))

      self.player.play(mp3s, zone)
    elif function == "play_radio":
      self.player.play_radio(music, zone)
    else:
      logging.warning("Don't know how to %s.", cmd)


def main():
  """Start a webserver to serve MP3s, then sniff for arp traffic."""
  port = 8080
  ipaddr = my_ip.lookup()
  player = sonos.Player()

  music_dir = "mp3s"
  # Move to the mp3 directory to serve files from it.
  try:
    os.chdir(music_dir)
  except OSError, ex:
    print "Couldn't chdir to %s directory: %s" % (music_dir, ex)
    sys.exit(1)

  webserver = localwebserver.HttpServer(port)
  webserver.start()

  uri = "http://%s:%s/" % (ipaddr, port)

  print "Serving MP3s at %s." % uri

  sniffer = Sniffer(uri, player)
  sniffer.run_forever()

main()
