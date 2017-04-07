#!/usr/bin/python2.7
"""User-specific configuration."""

# Mac addresses of devices you want the server to react to. Mine are Amazon Dash
# buttons, named for the thing they're supposed to be used to buy, but they can
# be any device on your network.
MACS = {
    'ac:63:be:8f:62:09': 'glad',
    '44:65:0d:ab:a6:07': 'playdoh',
}

# play_local, directory_to_play, device
COMMANDS = {
    'glad': ['play_local', 'hamilton', 'Living Room'],
    'playdoh': ['play_local', 'moana', 'Living Room'],
}
