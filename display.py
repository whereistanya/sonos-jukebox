#!/usr/bin/python2.7

"""Functions for interacting with a screen.

If this is used for a PiTFT attached to a raspberry pi, it'll be perfect. Run on
a desktop, it'll just make a tiny window. Oh well.
"""

import os
from signal import alarm, signal, SIGALRM, SIGKILL
from threading import Thread

HAVE_PYGAME = True

# pip install pygame
# sudo easy_install -U distribute
# pip install pygameui
# I had mysterious egg errors until I also did
# pip install setuptools

# If pygame's not installed, that shouldn't stop the binary from running.
try:
  import pygame
  import pygameui
except ImportError:
  HAVE_PYGAME = False


class Alarm(Exception):
  """A deadline for things that get wedged."""
  pass

def alarm_handler(signum, frame):
  raise Alarm

class Display(object):
  """If there's a display attached, display stuff on it."""

  def __init__(self, xsize, ysize, player, sonos_name):
    """Prepare a screen to display information about the sonos.

    Args:
      xsize, ysize: (int) dimensions of screen in pixels
      player: (sonos.Player) sonos controller
      sonos_name: (str) the sonos to display information for
    """

    # Needed to talk to the raspberry pi's PiTFT display.
    os.putenv('SDL_FBDEV', '/dev/fb1')
    os.putenv('SDL_MOUSEDRV', 'TSLIB')
    os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

    self.xsize = xsize
    self.ysize = ysize
    self.sonos_name = sonos_name
    pygame.init()
    pygame.mouse.set_visible(False)

    # set_mode hangs if something else is using the display and needs a ^C to
    # continue. Time out after two seconds. This is kind of a hack :-/
    signal(SIGALRM, alarm_handler)
    alarm(2)
    try:
      print "Attempting to initialise the display. Waiting up to two seconds."
      self.screen = pygame.display.set_mode((self.xsize, self.ysize))
      alarm(0)
    except Alarm:
      raise KeyboardInterrupt

    self.font20 = pygame.font.SysFont("verdana", 20)
    self.font12 = pygame.font.SysFont("verdana", 12)
    self.clock = pygame.time.Clock()

    self.player = player

  def start(self):
    """Spawn a thread to keep refreshing the display."""
    d = Thread(name='display', target=self.run)
    d.setDaemon(True)
    d.start()

  def run(self):
    """Run forever and keep refreshing the screen."""
    while True:
      self.fill()
      pygame.display.flip()
      self.clock.tick(1) # once a second

  def fill(self):
    """Paint the screen with a background colour and message."""
    self.screen.fill((0, 102, 0))  # a nice green
    track = self.player.get_current(self.sonos_name)
    if track:
      title = self.font20.render(track['title'], True, (255, 255, 255))
      album = self.font12.render(track['album'], True, (255, 255, 255))
    else:
      title = self.font20.render("Sonos Jukebox", True, (255, 255, 255))
      album = self.font20.render("Nothing is playing", True, (255, 255, 255))
    state = self.player.get_state(self.sonos_name)
    if not state:
      state = ""
    state_message = self.font20.render(state, True, (255, 255, 255))

    title_x = (self.xsize - title.get_width()) / 2
    album_x = (self.xsize - album.get_width()) / 2
    state_x = (self.xsize - state_message.get_width()) / 2
    self.screen.blit(title, (title_x, 100))
    self.screen.blit(album, (album_x, 150))
    self.screen.blit(state_message, (state_x, 200))

