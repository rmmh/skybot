#!/usr/bin/python

import sys
import os
import Queue

sys.path += ['plugins'] # so 'import hook' works without duplication
sys.path += ['lib']
os.chdir(sys.path[0])   # do stuff relative to the installation directory


class Bot(object):
    pass


bot = Bot()

print 'Loading plugins'

# bootstrap the reloader
eval(compile(open('core/reload.py', 'U').read(), 'core/reload.py', 'exec'))
reload(init=True)

print 'Connecting to IRC'

bot.conns = {}

try:
    for connection in bot.config['connections']:
        for name, conf in connection.iteritems():
            if name in bot.conns:
                print 'ERROR: more than one connection named "%s"' % name
                raise ValueError
            bot.conns[name] = irc(conf['server'], conf['nick'],
                    channels=conf['channels'])
            for channel in conf['channels']:
                bot.conns[name].join(channel)
except Exception, e:
    print 'ERROR: malformed config file', Exception, e
    sys.exit()

bot.persist_dir = os.path.abspath('persist')

print 'Running main loop'

while True:
    try:
        reload() # these functions only do things
        config() #  if changes have occured

        for conn in bot.conns.itervalues():
            out = conn.out.get(timeout=1)
            main(conn, out)
    except Queue.Empty:
        pass
