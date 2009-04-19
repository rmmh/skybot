import thread

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
        self.chan = paraml[0]
        if self.chan == bot.nick:
            self.chan = nick
        elif command =='JOIN':
            self.chan = msg


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

def main(out):
    printed = False
    for csig, func, args in (bot.plugs['command'] + bot.plugs['event']):
        input = Input(*out)
        for fsig, sieve in bot.plugs['sieve']:
            try:
                input = sieve(bot, input, func, args)
            except Exception, e:
                print 'sieve error:', e
                input = None
            if input == None:
                break
        if input == None:
            continue
        if not printed:
            print '<<<', input.raw
            printed = True
        thread.start_new_thread(FakeBot(bot, input, func).run, ())
