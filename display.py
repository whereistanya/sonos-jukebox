#!/usr/bin/python2.7

import os
from threading import Thread

HAVE_PYGAME = True

# If pygame's not installed, that shouldn't stop the binary from running.
try:
	import pygame
except ImportError:
	HAVE_PYGAME = False

# If there's a display attached, display stuff on it.
class Display:
  def __init__(self, xsize, ysize):

    # Needed to talk to the raspberry pi's PiTFT display.
    os.putenv('SDL_FBDEV', '/dev/fb1')
    os.putenv('SDL_MOUSEDRV', 'TSLIB')
    os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

    self.xsize = xsize
    self.ysize = ysize
    pygame.init()
    pygame.mouse.set_visible(False)
    self.screen = pygame.display.set_mode((self.xsize, self.ysize))
    self.font = pygame.font.SysFont("verdana", 24)
    self.message = None
    self.clock = pygame.time.Clock()

  def start(self):
    """Spawn a thread to keep refreshing the display."""
    d = Thread(name='display', target=self.run)
    d.setDaemon(True)
    d.start()

  def set_message(self, message):
    """Update the message on the screen."""
    self.message = self.font.render(message, True, (255, 255, 255))

  def run(self):
    """Run forever and keep refreshing the screen."""
    while True:
      self.fill()
      pygame.display.flip()
      self.clock.tick(60)

  def fill(self):
    """Paint the screen with a background colour and message."""
    self.screen.fill((0, 102, 0))
    if self.message:
      x = (self.xsize - self.message.get_width()) / 2
      y = (self.ysize - self.message.get_height()) / 2
      self.screen.blit(self.message, (x, y))

