#!/usr/bin/python

network = "irc.synirc.net"
nick = "UggBot"
channel = "#uggbot"

import sys
import os
import Queue

sys.path += ['plugins'] # so 'import hook' works without duplication
os.chdir(sys.path[0])   # do stuff relative to the installation directory

import irc


class Bot(object):
    pass

bot = Bot()

print 'Loading plugins'

# bootstrap the reloader
eval(compile(open('core/reload.py', 'U').read(), 'core/reload.py', 'exec'))

print 'Connecting to IRC'

bot.nick = nick
bot.channel = channel
bot.network = network
bot.irc = irc.irc(network, nick)
bot.irc.join(channel)
bot.persist_dir = os.path.abspath('persist')

print 'Running main loop'

while True:
    try:
        out = bot.irc.out.get(timeout=1)
        reload()
        main(out)
    except Queue.Empty:
        pass
