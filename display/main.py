#!/usr/bin/env python
"""
Control UI for a Sonos. Can forward/rewind/play/pause.
"""

import logging
import signal
import sys
sys.path.append("/home/pi/sonos-jukebox/lib")


import display
import sonos

SONOS = "Living Room"

def handler(signum, frame):
  """Why is systemd sending sighups? I DON'T KNOW."""
  logging.warning("Got a {} signal. Doing nothing".format(signum))

signal.signal(signal.SIGHUP, handler)

def main():
  """Run the display."""
  player = sonos.Player()
  zone = player.zone(SONOS)
  screen = display.Display(320, 240, zone)
  screen.run()

main()
