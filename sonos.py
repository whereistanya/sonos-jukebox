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
    for zone in soco.discover():
      self.zones[zone.player_name] = zone

    if len(self.zones) == 0:
      raise PlayerException("Can't find any Sonos zones.")


  def have_zone(self, zone):
    """Returns whether this is a zone we know about.

    Returns:
      (bool)
    """
    return zone in self.zones.keys()


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

  def play_radio(self, url, zone_name):
    """TODO(tanya): Implement aac-playing."""
    pass
