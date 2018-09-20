#!/usr/bin/env python

"""
Have your Sonos say words. Converts the text to mp3, spins up a webserver to
serve the mp3, sends the mp3 url to the Sonos, shuts down again.

The local webserver (very briefly) serves everything in the directory the script
is running in, so don't run this from your super secret data directory or
whatever.

You'll need to change the SONOS_NAME global variable and maybe also the port if
you're using 8081 for something.
"""

import os
import sys
import time
import urllib

# Need to pip install gtts and soco.
from gtts import gTTS
from soco import SoCo

sys.path.append("../lib")
import localwebserver
import my_ip
import sonos

SONOS_NAME = "Living Room"
PORT = 8081

def main():

  ipaddr = my_ip.lookup()
  player = sonos.Player()
  device = player.zone(SONOS_NAME)
  if not device:
    print ("Can't find a device called %s", zone)
    sys.exit(1)

  webserver = localwebserver.HttpServer(PORT)
  webserver.start()

  uri = "http://%s:%s/" % (ipaddr, PORT)

  if len(sys.argv) > 1:
    text = str(sys.argv[1:])
  else:
    text = "I am a talking computer"

  filename = "words.mp3"
  tts = gTTS(text=text, lang='en')
  tts.save(filename)

  url = os.path.join(uri, urllib.pathname2url(filename))
  device.play([url,])
  # Give the sonos a moment to grab the mp3 before killing the webserver.
  time.sleep(1)

main()
