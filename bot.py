#!/usr/bin/env python

import os
import Queue
import subprocess
import sys
import time


sys.path += ['plugins']  # So 'import hook' works without duplication
sys.path += ['lib']
os.chdir(sys.path[0] or '.')  # Set the current working directory


class Bot(object):
    pass


bot = Bot()

# Retrieve version using git
bot.version = {"REV_NUMBER": 0, "SHORT_HASH": "unknown"}
try:
    p = subprocess.Popen(['git', 'log', '--oneline'], stdout=subprocess.PIPE)
    stdout, _ = p.communicate()
    p.wait()

    bot.version["REV_NUMBER"] = len(stdout.splitlines())
    bot.version["SHORT_HASH"] = stdout.split(None, 1)[0]
except OSError:
    print "### INFO: git could not be used to retrieve version"

print 'Skybot (r%d %s) - http://github.com/rmmh/skybot' % (
                        bot.version["REV_NUMBER"], bot.version["SHORT_HASH"])

print 'Loading plugins'

# Bootstrap the reloader
eval(compile(open(os.path.join('core', 'reload.py'), 'U').read(),
             os.path.join('core', 'reload.py'), 'exec'))
reload(init=True)

config()
if not hasattr(bot, 'config'):
    exit()

print 'Connecting to IRC'

bot.conns = {}

try:
    for name, conf in bot.config['connections'].iteritems():
        if conf.get('ssl'):
            bot.conns[name] = SSLIRC(
                    conf['server'], conf['nick'], conf=conf,
                    port=conf.get('port', 6667),
                    channels=conf['channels'],
                    ignore_certificate_errors=conf.get('ignore_cert', True))
        else:
            bot.conns[name] = IRC(
                    conf['server'], conf['nick'], conf=conf,
                    port=conf.get('port', 6667), channels=conf['channels'])
except Exception, e:
    print 'ERROR: malformed config file', e
    sys.exit()

bot.persist_dir = os.path.abspath('persist')
if not os.path.exists(bot.persist_dir):
    os.mkdir(bot.persist_dir)

print 'Running main loop'

while True:
    # These functions only do things if changes have occured
    reload()
    config()

    for conn in bot.conns.itervalues():
        try:
            out = conn.out.get_nowait()
            main(conn, out)
        except Queue.Empty:
            pass
    while all(conn.out.empty() for conn in bot.conns.itervalues()):
        time.sleep(.1)
