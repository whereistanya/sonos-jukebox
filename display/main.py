#!/usr/bin/env python
"""
Control UI for a Sonos. Can forward/rewind/play/pause.
"""

import logging
import signal

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
# TODO(tanya): return a device and don't jump through hoops
  zone = sonos.Device(player.zone(SONOS))
  # Use a local display if one is available.
  screen = None
  screen = display.Display(320, 240, zone)
  screen.start()

main()
