This directory has two toy projects for interacting with Sonos players.

# **talker/talker.py**
A command-line script that makes the sonos say words. Use it like
./talker.py "This is a damn fine cup of coffee." It briefly spins up a webserver
to get the sound file to the Sonos.

## Requirements

### Install python modules
sudo pip install soco        # for Sonos  
sudo pip install gtts        # for converting text to speech

## Modify talker.py
Set *SONOS_NAME* to your Sonos. Change the *PORT* too if you want.


# **server.py**
A thing that lets you control your Sonos using Amazon Dash buttons. I stole this
idea from [Rob Konigsberg](http://github.com/kberg), who was using Dash buttons
to make his Sonos play radio stations. This version serves local MP3s and plays
different directories depending on which button you press.

server.py runs as root on a linux machine on the same wifi as your Sonos(es).
It notices arp traffic from other devices on your network. It's configured to
watch for a bunch of specific MAC addresses and trigger an action (defined in
buttons.py) whenever one of them is active. It can watch for Amazon Dash buttons
or similar in this way.

It runs a tiny webserver to serve mp3s.

## Requirements

### Install python modules
sudo pip install scapy       # For sniffing the network  
sudo pip install soco        # for Sonos  
sudo pip install requests    # For REST API  

### Put MP3s in place
You need a long-running Linux machine on your local network to run server.py
on. Make a directory under its cwd called "mp3s". Make directories under that
with mp3s in them. Use those directory names in your config.

### Edit the config
Change buttons.py to list your MAC addresses, button names and actions. There's
one action so far, '*play_local*'. It plays a directory of music from the
machine that this is running on.

### Run the server as root

`sudo server.py`

or make it start on boot by adding an init.d or systemd config. There's a
systemd example at [config/sonos-jukebox.service](
https://github.com/whereistanya/sonos-jukebox/blob/master/config/sonos-jukebox.service).

## Testing it
Add your computer as a button in buttons.py, and trigger arp traffic from
it. On linux, you do that with `arping -c 1 [any IP]`.

## How do I know what my MAC address is?
On a linux machine, you can do `ifconfig` and copy the HWaddr and inet addr of
your own machine.

To see the addresses of other devices:

* run `sudo tcpdump -e -v arp` (from a linux machine on the same wifi network)
and watch what's going by. You might see your sonos, your wireless gateway, misc
other stuff you recognise. You'll need the device to be sending traffic or you
won't see it.

* Or edit server.py's arp_cb() method to to print the MAC addresses that it
sees.

## How do I use an Amazon Dash?
You need to order one from an account with Amazon Prime enabled, and you need to
configure it using the same account, so getting someone else to buy one won't
work (unless they're willing to log in on your wifi to set it up.)

Install the Amazon Shopping app and log in with the account that has prime. Go
to 'Your account' and scroll down to 'Dash devices'. Start setting up the device
as they describe it, but don't connect it to a product; just get it onto your
wireless network.

Then follow the instructions above to get the MAC address. Press the
button, and it should show up as arp traffic. Hopefully your network
is relatively quiet, so it'll be easy to pick out the Amazon Dash.
