#!/usr/bin/python2.7
"""Return the IP address we're using.

A classic StackOverflow solution! Get the address on the local lan, by opening
a socket to an arbitrary internet address (well, the Goog's DNS), checking the
IP we're using, and then not using the socket. It's janky, but all of the
alternatives (e.g., shelling out to ifconfig and parsing the output, which is
different on each distro) are worse, I think. Don't use this for anything
important or repetitive, but it's probably ok for a one-off.
"""
import socket

def lookup():
  """Return the address.

  Returns:
    (string)
   """
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.connect(("8.8.8.8", 80))
  return sock.getsockname()[0]
