#!/usr/bin/python

network = "irc.synirc.net"
nick = "skybot"
channel = "#cobol"

import sys
import os
import glob
import imp
import re
import thread
import Queue
import collections

sys.path += ['plugins'] # so 'import hook' works without duplication

import irc
import yaml

os.chdir(sys.path[0])   # do stuff relative to the installation directory

class Bot(object):
    def __init__(self, nick, channel, network):
        self.nick = nick
        self.channel = channel
        self.network = network

bot = Bot(nick, channel, network)

print 'Loading plugins'

plugin_mtimes = {}

def reload_plugins():
    
    if not hasattr(bot, 'plugs'):
        bot.plugs = collections.defaultdict(lambda: [])

    for filename in glob.glob("core/*.py") + glob.glob("plugins/*.py"):
        mtime = os.stat(filename).st_mtime
        if mtime != plugin_mtimes.get(filename):
            shortname = os.path.splitext(os.path.basename(filename))[0]
            try:
                plugin = imp.load_source(shortname, filename)
            except Exception, e:
                print '    error:', e
                continue
            
            # remove plugins already loaded from this filename
            for name, data in bot.plugs.iteritems():
                bot.plugs[name] = filter(lambda x: x[0][0] != filename, data)

            for obj in vars(plugin).itervalues():
                if hasattr(obj, '_skybot_hook'): #check for magic
                    for type, data in obj._skybot_hook:
                        bot.plugs[type] += [data]

            plugin_mtimes[filename] = mtime

reload_plugins()

print '  plugin listing:'
for type, plugs in sorted(bot.plugs.iteritems()):
    print '    %s:' % type
    for plug in plugs:
        out = '      %s:%s:%s' % (plug[0])
        print out,
        if len(plug) == 3 and 'hook' in plug[2]:
            print '%s%s' % (' ' * (35 - len(out)), plug[2]['hook'])
        else:
            print
print

print 'Connecting to IRC'
bot.irc = irc.irc(network, nick)
bot.irc.join(channel)
bot.persist_dir = os.path.abspath('persist')

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
        if command == "PRIVMSG":
            if paraml[0] != bot.nick:
                self.chan = paraml[0]
            else:
                self.chan = nick
        else:
            self.chan = ""

class FakeBot(object):
    def __init__(self, bot, input, func):
        self.bot = bot
        self.persist_dir = bot.persist_dir
        self.network = bot.network
        self.input = input
        self.msg = bot.irc.msg
        self.cmd = bot.irc.cmd
        self.join = bot.irc.join
        self.func = func
        self.doreply = True
        self.chan = input.chan

    def say(self, msg):
        self.bot.irc.msg(self.chan, msg)

    def reply(self, msg):
        self.say(self.input.nick + ': ' + msg)

    def run(self):
        ac = self.func.func_code.co_argcount
        if ac == 2:
            out = self.func(self, self.input)
        elif ac == 1:
            out = self.func(self.input.inp)
        if out is not None:
            if self.doreply:
                self.reply(unicode(out))
            else:
                self.say(unicode(out))

while True:
    try: 
        out = bot.irc.out.get(timeout=1)
        reload_plugins()
        printed = False
        for csig, func, args in (bot.plugs['command'] + bot.plugs['event']):
            input = Input(*out)
            for fsig, sieve in bot.plugs['sieve']:
                try:
                    input = sieve(bot, input, func, args)
                except Exception, e:
                    print 'filter error:', e
                    input = None
                if input == None:
                    break
            if input == None:
                continue
            if not printed:
                print '<<<', input.raw
                printed = True
            thread.start_new_thread(FakeBot(bot, input, func).run, ())
    except Queue.Empty:
        pass
