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
import copy

import irc
import yaml

os.chdir(sys.path[0]) #do stuff relative to the installation directory

class Bot(object):
    def __init__(self):
        self.commands = [] # fn, name, func, args
        self.filters = [] #fn, name, func

bot = Bot()
bot.nick = nick
bot.channel = channel
bot.network = network

print 'Loading plugins'
typs = '|'.join('command filter event'.split())
magic_re = re.compile(r'^\s*#(%s)(?:: +(\S+) *(\S.*)?)?\s*$' % typs)

def reload_plugins(mtime=[0]):
    new_mtime = os.stat('plugins')
    if new_mtime == mtime[0]:
        return

    bot.commands = []
    bot.filters = []


    for filename in glob.glob("plugins/*.py"):
        shortname = os.path.splitext(os.path.basename(filename))[0]
        try:
            plugin = imp.load_source(shortname, filename)
            source = open(filename).read().split('\n')
            #this is a nasty hack, but it simplifies registration
            funcs = [x for x in dir(plugin) 
                     if str(type(getattr(plugin,x))) == "<type 'function'>"]
            for func in funcs:
                #read the line before the function definition, looking for a
                # comment that tells the bot about what it does
                func = getattr(plugin, func)
                lineno = func.func_code.co_firstlineno
                if lineno == 1:
                    continue #can't have a line before the first line...
                m = magic_re.match(source[lineno-2])
                if m:
                    typ, nam, rest = m.groups()
                    if nam is None:
                        nam = func.__name__
                    if rest is None:
                        rest = '\s*(.*)'
                    if typ == 'command':
                        args = {'name': nam, 'hook': nam + rest}
                        bot.commands.append((filename, nam, func, args))
                    elif typ == 'filter':
                        bot.filters.append((filename, nam, func))
                    elif typ == 'event':
                        args = {'name': nam, 'prefix':False, 
                            'events': [nam] + rest.split()}
                        bot.commands.append((filename, nam, func, args))
        except Exception, e:
            print e

    mtime[0] = new_mtime

reload_plugins()

print 'Connecting to IRC'
bot.irc = irc.irc(network, nick)
bot.irc.join(channel)
bot.commandprefix = '^(?:\.|'+nick+'[:,]*\s*)'

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
    def __init__(self, bot, input, fn, func):
        self.bot = bot
        self.input = input
        self.msg = bot.irc.msg
        self.cmd = bot.irc.cmd
        self.join = bot.irc.join
        self.fn = func
        self.func = func
        self.doreply = True
        if input.command == "PRIVMSG":
            self.chan = input.paraml[0]

    def say(self, msg):
        self.bot.irc.msg(self.input.paraml[0], msg)

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

print bot.commands
print bot.filters

while True:
    try: 
        out = bot.irc.out.get(timeout=1)
        reload_plugins()
        for fn, name, func, args in bot.commands:
            input = Input(*out)
            for fn, nam, filt in bot.filters:
                input = filt(bot, func, args, input)
                if input == None:
                    break
            if input == None:
                continue
            print '<<<', input.raw
            thread.start_new_thread(FakeBot(bot, input, fn, func).run, ())
    except Queue.Empty:
        pass
