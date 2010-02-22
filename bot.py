#!/usr/bin/python

import os
import Queue
import sys
import time

sys.path += ['plugins'] # so 'import hook' works without duplication
sys.path += ['lib']
os.chdir(sys.path[0] or '.')   # do stuff relative to the installation directory


class Bot(object):
    pass


bot = Bot()

print 'Loading plugins'

# bootstrap the reloader
eval(compile(open(os.path.join('core', 'reload.py'), 'U').read(), 
    os.path.join('core', 'reload.py'), 'exec'))
reload(init=True)

print 'Connecting to IRC'

bot.conns = {}

try:
    for connection in bot.config['connections']:
        for name, conf in connection.iteritems():
            if name in bot.conns:
                print 'ERROR: more than one connection named "%s"' % name
                raise ValueError
            ssl = conf.get('ssl', False)
            if ssl:
                bot.conns[name] = SSLIRC(conf['server'], conf['nick'],
                        port=conf.get('port', 6667), channels=conf['channels'], conf=conf,
                        ignore_certificate_errors=conf.get('ignore_cert', True))
            else:
                bot.conns[name] = IRC(conf['server'], conf['nick'],
                        port=conf.get('port', 6667), channels=conf['channels'], conf=conf)
except Exception, e:
    print 'ERROR: malformed config file', Exception, e
    sys.exit()

bot.persist_dir = os.path.abspath('persist')
if not os.path.exists(bot.persist_dir):
    os.mkdir(bot.persist_dir)

print 'Running main loop'

while True:
    reload() # these functions only do things
    config() #  if changes have occured

    for conn in bot.conns.itervalues():
        try:
            out = conn.out.get_nowait()
            main(conn, out)
        except Queue.Empty:
            pass
    while all(conn.out.empty() for conn in bot.conns.itervalues()):
        time.sleep(.3)
