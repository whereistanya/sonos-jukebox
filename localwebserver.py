#!/usr/bin/python2.7
"""A tiny web server for making local MP3s have http addresses."""

from threading import Thread
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import TCPServer

class HttpServer(Thread):
  """Tiny webserver."""

  def __init__(self, port):
    """Create a webserver, without starting it.

    Args:
      port: (int, required) local port to serve one
    """

    super(HttpServer, self).__init__()
    self.daemon = True
    handler = SimpleHTTPRequestHandler
    self.httpd = TCPServer(("", port), handler, bind_and_activate=False)
    self.httpd.allow_reuse_address = True
    self.httpd.server_bind()
    self.httpd.server_activate()

  def run(self):
    """Start the webserver."""
    self.httpd.serve_forever()

  def stop(self):
    """Stop the webserver."""
    self.httpd.socket.close()

