import thread
import traceback

class Input(object):

    def __init__(self, conn, raw, prefix, command,
            params, nick, user, host, paraml, msg):
        self.conn = conn            # irc object
        self.server = conn.server   # hostname of server
        self.raw = raw              # unprocessed line of text
        self.prefix = prefix        # usually hostmask
        self.command = command      # PRIVMSG, JOIN, etc.
        self.params = params        
        self.nick = nick
        self.user = user            # user@host
        self.host = host
        self.paraml = paraml        # params[-1] without the :
        self.msg = msg
        self.chan = paraml[0]
        if self.chan == conn.nick:  # is a PM
            self.chan = nick

    def say(self, msg):
        self.conn.msg(self.chan, msg)

    def reply(self, msg):
        self.say(self.nick + ': ' + msg)

    def pm(self, msg):
        self.conn.msg(self.nick, msg)


def run(func, input):
    ac = func.func_code.co_argcount
    if ac == 2:
        out = func(bot, input)
    elif ac == 1:
        out = func(input.inp)
    if out is not None:
        input.reply(unicode(out))


def main(conn, out):
    for csig, func, args in bot.plugs['tee']:
        input = Input(conn, *out)
        func._iqueue.put((bot, input))
    for csig, func, args in (bot.plugs['command'] + bot.plugs['event']):
        input = Input(conn, *out)
        for fsig, sieve in bot.plugs['sieve']:
            try:
                input = sieve(bot, input, func, args)
            except Exception, e:
                print 'sieve error',
                traceback.print_exc(Exception)
                input = None
            if input == None:
                break
        if input == None:
            continue
        thread.start_new_thread(run, (func, input))
