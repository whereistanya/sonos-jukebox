#!/usr/bin/python2.7

"""Functions for interacting with a screen.

If this is used for a PiTFT attached to a raspberry pi, it'll be perfect. Run on
a desktop, it'll just make a tiny window. Oh well.
"""
import logging
import os
from signal import alarm, signal, SIGALRM, SIGKILL

# pip install pygame
# sudo easy_install -U distribute
# I had mysterious egg errors until I also did
# pip install setuptools

import pygame


WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 102, 0)
PURPLE = (139, 55, 150)

class Alarm(Exception):
  """A deadline for things that get wedged."""
  pass

def alarm_handler(signum, frame):
  raise Alarm

class Button(object):
  """A button to display on the screen."""

  def __init__(self, text, x, y, width, height, color, action):
    """Coordinates describe top left corner of button.

    Args:
      text: (str) The button text.
      x, y, width, height: (int) REgular co-ordinates in pixels
      color: (int, int, int) RGB value for the colour.
      action: (str) The name of some action to take when the button is clicked.
    """
    self.text = text
    self.action = action
    self.x = x
    self.y = y
    self.width = width
    self.height = height
    self.color = color

  def contains(self, x, y):
    """Returns whether the co-ordinates are inside this button.

    Args:
      x, y: (int) Pixel co-ordinates.
    Returns:
      (bool) Whether the co-ordinates are inside the button.
    """
    if x < self.x or x > (self.x + self.width):
      return False
    if y < self.y or y > (self.y + self.height):
      return False
    return True

  def get(self):
    """Return rectangle description for use in pygame.draw.

    Returns:
      (int, int, int, int): x, y, width, height tuple.
    """
    return (self.x, self.y, self.width, self.height)

  def text_pos(self, text):
    """Return the starting coordinates for blitting text.

    Args:
      text: (pygame.Surface)
    Returns
      (int, int): Co-ordinates tuple.
    """

    text_x = self.x + (self.width - text.get_width()) / 2
    text_y = self.y + (self.height - text.get_height()) / 2

    return (text_x, text_y)

  def set_text(self, text):
    """Python doesn't like setters but I do."""
    self.text = text


class Display(object):
  """If there's a display attached, display stuff on it."""

  def __init__(self, xsize, ysize, device):
    """Prepare a screen to display information about the sonos.

    Args:
      xsize, ysize: (int) dimensions of screen in pixels
      device: (sonos.Device) the sonos to display information for
    """

    # Needed to talk to the raspberry pi's PiTFT display.
    # Comment them out to run on a random linux box.
    os.putenv('SDL_FBDEV', '/dev/fb1')
    os.putenv('SDL_MOUSEDRV', 'TSLIB')
    os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')
    os.putenv('SDL_VIDEODRIVER', 'fbcon')

    self.xsize = xsize
    self.ysize = ysize
    self.device = device
    pygame.init()

    # set_mode hangs if something else is using the display and needs a ^C to
    # continue. Time out after two seconds. This is kind of a hack :-/
    signal(SIGALRM, alarm_handler)
    alarm(2)
    try:
      logging.warning("Attempting to initialise the display. Waiting up to two seconds.")
      self.screen = pygame.display.set_mode((self.xsize, self.ysize))
      alarm(0)
    except Alarm:
      raise KeyboardInterrupt

    pygame.mouse.set_visible(True)
    self.font20 = pygame.font.SysFont("verdana", 20)
    self.font12 = pygame.font.SysFont("verdana", 12)
    self.clock = pygame.time.Clock()

    self.buttons = {}
    self.buttons["back"] = Button("back", 10, 180, 60, 50, BLUE, "previous")
    self.buttons["toggle"] = Button("pause", 130, 180, 60, 50, RED, "toggle")
    self.buttons["skip"] = Button("skip", 250, 180, 60, 50, BLUE, "next")

  def run(self):
    """Run forever and keep refreshing the screen."""
    while True:
      self.fill()
      self.check_events()
      pygame.display.flip()
      self.clock.tick(10) # 10 times per second

  def fill(self):
    """Paint the screen with a background colour, buttons and messages."""
    self.screen.fill(PURPLE)
    track = self.device.get_current()
    if track:
      title = self.font20.render(track['title'], True, WHITE)
      album = self.font12.render(track['album'], True, WHITE)
      artist = self.font12.render(track['artist'], True, WHITE)
    else:
      title = self.font20.render("Sonos Jukebox", True, WHITE)
      album = self.font20.render("Nothing is playing", True, WHITE)
      artist = self.font20.render('')

    # We print the state, and also change the pause/unpause button's text based
    # on whether it's currently playing.
    state = self.device.get_state()
    if not state:
      state = ""
    elif state == "PLAYING":
      self.buttons["toggle"].set_text("pause")
    if state == "PAUSED_PLAYBACK":
      state = "PAUSED"
      self.buttons["toggle"].set_text("play")
    if state == "STOPPED":
      self.buttons["toggle"].set_text("")

    state_message = self.font20.render(state, True, (255, 255, 255))

    title_x = max((self.xsize - title.get_width()) / 2, 0)
    album_x = max((self.xsize - album.get_width()) / 2, 0)
    artist_x = max((self.xsize - artist.get_width()) / 2, 0)
    state_x = (self.xsize - state_message.get_width()) / 2
    self.screen.blit(title, (title_x, 40))
    self.screen.blit(album, (album_x, 80))
    self.screen.blit(artist, (artist_x, 100))
    self.screen.blit(state_message, (state_x, 120))

    for button in self.buttons.values():
      pygame.draw.rect(self.screen, button.color, button.get())
      name = self.font12.render(button.text, True, WHITE)
      self.screen.blit(name, button.text_pos(name))


  def check_events(self):
    """Notice touchscreen presses."""
    for event in pygame.event.get():
      if event.type == pygame.MOUSEBUTTONDOWN:
        x = pygame.mouse.get_pos()[0]
        y = pygame.mouse.get_pos()[1]
        for button in self.buttons.values():
          if button.contains(x, y):
            logging.info("Clicked button %s" % button.text)
            self.button_action(button.action)

  def button_action(self, action):
    """Take some action when a UI button was clicked.

    Args:
      action: (string) What to do.
    """
    if action == "next":
      self.device.next()
    elif action == "previous":
      self.device.previous()
    elif action == "toggle":
      self.device.toggle()
    else:
      logging.warning("Don't know how to do action %s.", action)
