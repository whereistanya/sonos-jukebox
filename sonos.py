#!/usr/bin/python2.7
"""Handle interactions with the Sonos devices on the network."""

import logging
from threading import Thread
import soco

class PlayerException(Exception):
  """We can't play sonos for any reason."""
  pass

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

  def toggle(self, zone_name):
    """Pause or unpause the zone."""
    state = self.get_state(zone_name)
    if state == "PLAYING":
      logging.warning("Zone %s has state %s. Pausing.", zone_name, state)
      self.pause(zone_name)
    else:
      logging.warning("Zone %s has state %s. Playing.", zone_name, state)
      self.unpause(zone_name)

  def have_zone(self, zone):
    """Returns whether this is a zone we know about.

    Returns:
      (bool)
    """
    return zone in self.zones.keys()

  def pause(self, zone_name):
    """Pause the currently playing music in the zone.

      Args:
        zone_name: (string) Which Sonos to pause.
    """
    zone = self.zones[zone_name]
    zone.pause()

  def unpause(self, zone_name):
    """Unpause the music in the zone.

      Args:
        zone_name: (string) Which Sonos to unpause.
    """
    zone = self.zones[zone_name]
    zone.play()

  def play(self, urls, zone_name):
    """Play a bunch of MP3s from their URLs.

      Args:
        urls: ([string, ...]) URLs to send to the Sonos
        zone_name: (string) Which Sonos to play on.
    """
    if not self.have_zone(zone_name):
      raise PlayerException("Can't find the %s zone. Have %s" % (
          zone_name, self.zones.keys()))
    zone = self.zones[zone_name]
    zone.clear_queue()
    for url in urls:
      logging.warning("Adding %s", url)
      zone.add_uri_to_queue(url)

    queue = zone.get_queue()
    logging.warning("Queue is now: %s.", queue)
    zone.play_from_queue(0)

  def next(self, zone_name):
    """Jump to the next track.

      Args:
        zone_name: (string) Which Sonos to operate.
    """
    zone = self.zones[zone_name]
    zone.next()

  def previous(self, zone_name):
    """Go back one track.

      Args:
        zone_name: (string) Which Sonos to operate.
    """
    zone = self.zones[zone_name]
    zone.previous()

  def play_radio(self, url, zone_name):
    """TODO(tanya): Implement aac-playing."""
    pass


  def get_current(self, zone_name):
    """Return current playing track as a dict.

    Args:
      zone_name: (string) Which Sonos to play on.
    Returns:
      ({'string': 'string'}) a dict of track information including album,
                             artist, title, etc.
   """
    if not self.have_zone(zone_name):
      raise PlayerException("Can't find the %s zone. Have %s" % (
          zone_name, self.zones.keys()))
    zone = self.zones[zone_name]
    return zone.get_current_track_info()

  def get_state(self, zone_name):
    """Return current playing state (playing, paused).

    Args:
      zone_name: (string) Which Sonos to play on.
    Returns:
      (string): play state
    """

    zone = self.zones[zone_name]
    info = zone.get_current_transport_info()
    return info['current_transport_state']
