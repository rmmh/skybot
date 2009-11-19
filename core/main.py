import thread
import traceback

class Input(object):

    def __init__(self, conn, raw, prefix, command,
            params, nick, user, host, paraml, msg):
        self.conn = conn
        self.server = conn.server
        self.raw = raw
        self.prefix = prefix
        self.command = command
        self.params = params
        self.nick = nick
        self.user = user
        self.host = host
        self.paraml = paraml
        self.msg = msg
        self.chan = paraml[0]
        if self.chan == conn.nick:
            self.chan = nick
        elif command =='JOIN':
            self.chan = msg


class FakeBot(object):

    def __init__(self, bot, conn, input, func):
        self.bot = bot
        self.conn = conn
        self.persist_dir = bot.persist_dir
        self.input = input
        self.msg = conn.msg
        self.cmd = conn.cmd
        self.join = conn.join
        self.func = func
        self.doreply = True
        self.chan = input.chan
    
    def say(self, msg):
        self.conn.msg(self.chan, msg)

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
        thread.start_new_thread(FakeBot(bot, conn, input, func).run, ())
