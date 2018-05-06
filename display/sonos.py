#!/usr/bin/python2.7
"""Handle interactions with the Sonos devices on the network."""

import logging
from threading import Thread
import time

import soco

class PlayerException(Exception):
  """We can't play sonos for any reason."""
  pass

# TODO(tanya): inherit from sonos.Soco.whatever and ditch half these functions.
class Device(object):
  """A single sonos device."""
  def __init__(self, zone):
    self.zone = zone
    self.last_called = 0  # don't hit the sonos too frequently
    self.current_track = "UNKNOWN_TRACK"
    self.current_state = "UNKNOWN_STATE"

  def toggle(self):
    """Pause or unpause the zone."""
    state = self.get_state()
    if state == "PLAYING":
      logging.warning("Zone %s has state %s. Pausing.", self.zone, state)
      self.pause()
    else:
      logging.warning("Zone %s has state %s. Playing.", self.zone, state)
      self.unpause()

  def pause(self):
    """Pause the currently playing music in the zone."""
    self.zone.pause()

  def unpause(self):
    """Unpause the music in the zone."""
    self.zone.play()

  def next(self):
    """Jump to the next track."""
    self.zone.next()

  def previous(self):
    """Go back one track."""
    self.zone.previous()

  def play(self, urls):
    """Play a bunch of MP3s from their URLs.

      Args:
        urls: ([string, ...]) URLs to send to the Sonos
    """
    self.zone.clear_queue()
    for url in urls:
      logging.warning("Adding %s", url)
      self.zone.add_uri_to_queue(url)

    queue = self.zone.get_queue()
    logging.warning("Queue is now: %s.", queue)
    self.zone.play_from_queue(0)

  def maybe_refresh_state(self):
    """Pull latest information from the sonos, if we haven't recently."""
    now = time.time()
    if now - self.last_called < 1:
      return

    try:
      self.current_track = self.zone.get_current_track_info()
      info = self.zone.get_current_transport_info()
      self.current_state = info['current_transport_state']
    except ConnectionError:
      logging.warning("Connection error refreshing current track and state.")

  def get_current(self):
    """Return current playing track as a dict.

    Returns:
      ({'string': 'string'}) a dict of track information including album,
                             artist, title, etc.
    """
    self.maybe_refresh_state()
    return self.current_track

  def get_state(self):
    """Return current playing state (playing, paused).

    Returns:
      (string): play state
    """
    self.maybe_refresh_state()
    return self.current_state


class Player(Thread):
  """Finds the available Sonos devices and plays music on them."""

  def __init__(self):
    """Find local players."""
    super(Player, self).__init__()
    self.zones = {}
    zones = soco.discover()
    if zones is None:
      raise PlayerException("Can't find any Sonos players.")
    for zone in zones:
      self.zones[zone.player_name] = zone

  def zone(self, name):
    """Return sonos device for zone name."""
    if name in self.zones:
      return self.zones[name]
    logging.warning("Don't know a zone called %s.", name)
    return None
