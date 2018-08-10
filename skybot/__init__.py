import os
import Queue
import sys
import traceback
import time

from bot import Bot

bot = Bot()

def main():
    os.chdir(os.path.dirname(__file__) or '.')  # do stuff relative to the install directory

    print 'Loading plugins'

    # bootstrap the reloader
    eval(compile(open(os.path.join('core', 'reload.py'), 'U').read(),
                 os.path.join('core', 'reload.py'), 'exec'),
         globals())
    reload(init=True)

    print 'Connecting to IRC'

    try:
        config()
        if not hasattr(bot, 'config'):
            exit()
    except Exception, e:
        print 'ERROR: malformed config file:', e
        traceback.print_exc()
        sys.exit()

    print 'Running main loop'

    while True:
        reload()  # these functions only do things
        config()  # if changes have occured

        for conn in bot.conns.itervalues():
            try:
                out = conn.out.get_nowait()
                main(conn, out)
            except Queue.Empty:
                pass
        while all(conn.out.empty() for conn in bot.conns.itervalues()):
            time.sleep(.1)
