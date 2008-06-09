#!/usr/bin/python

network = "irc.synirc.net"
nickname = "skybot"
channel = "#mongbot"

import sys, os, glob, imp, re
import thread, Queue, copy
import irc, yaml

os.chdir(sys.path[0]) #do stuff relative to the installation directory


class Empty(object): #this is used to store attributes
    pass


class Bot(object):
    def __init__(self):
        self.plugins = {}
        self.commands = {}
        self.listens = {}
        self.filters = {}
        self.daemons = {}

    def command(self, name, func, **filterargs):
        self.commands[name] = (func, filterargs)

    def listen(self, name, func):
        self.listens[name] = func

    def filter(self, name, func):
        self.filters[name] = func

    def daemon(self, name, func):
        self.daemons[name] = func

bot = Bot()

print 'Loading plugins'
for filename in glob.glob("plugins/*.py"):
    shortname = os.path.splitext(os.path.basename(filename))[0]
    try:
        bot.plugins[shortname] = imp.load_source(shortname,filename)
    except Exception, e:
        print e

print bot.plugins

print 'Registering plugins'
for name, plugin in bot.plugins.iteritems():
    if hasattr(plugin, 'setup'):
        try:
            plugin.setup(bot)
        except Exception, e:
            print e

print 'Connecting to IRC'

bot.irc = irc.irc(network, nickname)
bot.irc.join(channel)
bot.commandprefix = '^(?:\.|'+nickname+'[:,]*\s*)'

if bot.daemons:
    print 'Running daemons'
    for daemon in bot.daemons.itervalues():
        thread.start_new_thread(daemon, ())

print 'Running main loop'

class Input(object):
    def __init__(self, raw, prefix, command, 
            params, nick, user, host, paraml, msg):
        self.raw = raw
        self.prefix = prefix
        self.command = command
        self.params = params
        self.nick = nick
        self.user = user
        self.host = host
        self.paraml = paraml
        self.msg = msg

class FakeBot(object):
    def __init__(self, bot, input):
        self.bot = bot
        self.input = input
    
    def say(self, msg):
        self.bot.irc.msg(input.paraml[0], msg)

    def reply(self, msg):
        self.say(input.nick + ': ' + msg)

print bot.commands

while True:
    try: 
        out = bot.irc.out.get(timeout=1)
        #print repr(out)
        for func, args in bot.commands.itervalues():
            input = Input(*out)
            for filt in bot.filters.itervalues():
                input = filt(bot, func, args, input)
                if input == False:
                    break
            if input == False:
                continue
            thread.start_new_thread(func,(FakeBot(bot, input), input))
    except Queue.Empty:
        pass
    #except KeyboardInterrupt:
    #    sys.exit()
