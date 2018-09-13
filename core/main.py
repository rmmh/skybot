import re
from threading import Thread
import traceback


class Input(dict):

    def __init__(self, conn, raw, prefix, command, params,
                 nick, user, host, paraml, msg):

        chan = paraml[0].lower()
        if chan == conn.nick.lower():  # is a PM
            chan = nick

        def say(msg):
            conn.msg(chan, msg)

        def reply(msg):
            if chan == nick:  # PMs don't need prefixes
                self.say(msg)
            else:
                self.say(nick + ': ' + msg)

        def pm(msg, nick=nick):
            conn.msg(nick, msg)

        def set_nick(nick):
            conn.set_nick(nick)

        def me(msg):
            self.say("\x01%s %s\x01" % ("ACTION", msg))

        def notice(msg):
            conn.cmd('NOTICE', [nick, msg])

        def kick(target=None, reason=None):
            conn.cmd('KICK', [chan, target or nick, reason or ''])

        def ban(target=None):
            conn.cmd('MODE', [chan, '+b', target or host])

        def unban(target=None):
            conn.cmd('MODE', [chan, '-b', target or host])


        dict.__init__(self, conn=conn, raw=raw, prefix=prefix, command=command,
                      params=params, nick=nick, user=user, host=host,
                      paraml=paraml, msg=msg, server=conn.server, chan=chan,
                      notice=notice, say=say, reply=reply, pm=pm, bot=bot,
                      kick=kick, ban=ban, unban=unban, me=me,
                      set_nick=set_nick, lastparam=paraml[-1])

    # make dict keys accessible as attributes
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value


def do_sieve(sieve, bot, input, func, type, args):
    try:
        return sieve(bot, input, func, type, args)
    except Exception:
        print 'sieve error',
        traceback.print_exc()
        return None


class Handler(Thread):
    def __init__(self, func):
        super(Handler, self).__init__()

        # Handlers do not need to be cleaned up in any
        # special way, so mark them as "daemon"
        self.daemon = True

        self._func = func
        self._input_queue = Queue.Queue()
        self._db_connections = {}

    def _call_func(self, obj):
        func = self._func
        args = self._func._args

        if 'inp' not in obj:
            obj.inp = obj.paraml

        if args:
            if 'db' in args:
                obj.db = self._get_db_connection(obj.conn)

            if 'input' in args:
                obj.input = obj

            if 0 in args:
                out = func(obj.inp, **obj)
            else:
                kw = dict((key, obj[key]) for key in args if key in obj)
                out = func(obj.inp, **kw)
        else:
            out = func(obj.inp)

        if out is not None:
            obj.reply(unicode(out))

    def _get_db_connection(self, connection):
        if connection not in self._db_connections:
            self._db_connections[connection] = bot.get_db_connection(connection)

        return self._db_connections.get(connection)

    def run(self):
        while True:
            next_input = self._input_queue.get()

            if next_input == StopIteration:
                break

            try:
                self._call_func(next_input)
            except ValueError:
                traceback.print_exc()

    def stop(self):
        self._input_queue.put(StopIteration)

    def put(self, value):
        self._input_queue.put(value)


def dispatch(input, kind, func, args, autohelp=False):
    for sieve, in bot.plugs['sieve']:
        input = do_sieve(sieve, bot, input, func, kind, args)
        if input == None:
            return

    if autohelp and args.get('autohelp', True) and not input.inp \
            and func.__doc__ is not None:
        input.reply(func.__doc__)
        return

    if hasattr(func, '_apikey'):
        key = bot.config.get('api_keys', {}).get(func._apikey, None)
        if key is None:
            input.reply('error: missing api key')
            return
        input.api_key = key

    # There are some edge cases where we no longer will have an underlying thread
    # at this point because of reloads occurring.  It's not likely, but given that
    # the case would take down the bot, let's just protect against it and lose the
    # message.

    # TODO: Create a more fault tolerant way of passing messages to threads?
    if func in bot.threads:
        bot.threads[func].put(input)


def match_command(command):
    commands = list(bot.commands)

    # do some fuzzy matching
    prefix = filter(lambda x: x.startswith(command), commands)
    if len(prefix) == 1:
        return prefix[0]
    elif prefix and command not in prefix:
        return prefix

    return command

def make_command_re(bot_prefix, is_private, bot_nick):
    if not isinstance(bot_prefix, list):
        bot_prefix = [bot_prefix]
    if is_private:
        bot_prefix.append('')  # empty prefix
    bot_prefix = '|'.join(re.escape(p) for p in bot_prefix)
    bot_prefix += '|' + bot_nick + r'[:,]+\s+'
    command_re = r'(?:%s)(\w+)(?:$|\s+)(.*)' % bot_prefix
    return re.compile(command_re)

def test_make_command_re():
    match = make_command_re('.', False, 'bot').match
    assert not match('foo')
    assert not match('bot foo')
    for _ in xrange(2):
        assert match('.test').groups() == ('test', '')
        assert match('bot: foo args').groups() == ('foo', 'args')
        match = make_command_re('.', True, 'bot').match
    assert match('foo').groups() == ('foo', '')
    match = make_command_re(['.', '!'], False, 'bot').match
    assert match('!foo args').groups() == ('foo', 'args')

def main(conn, out):
    inp = Input(conn, *out)

    # EVENTS
    for func, args in bot.events[inp.command] + bot.events['*']:
        dispatch(Input(conn, *out), "event", func, args)

    if inp.command == 'PRIVMSG':
        # COMMANDS
        config_prefix = bot.config.get("prefix", ".")
        is_private = inp.chan == inp.nick  # no prefix required
        command_re = make_command_re(config_prefix, is_private, inp.conn.nick)

        m = command_re.match(inp.lastparam)

        if m:
            trigger = m.group(1).lower()
            command = match_command(trigger)

            if isinstance(command, list):  # multiple potential matches
                input = Input(conn, *out)
                input.reply("did you mean %s or %s?" %
                            (', '.join(command[:-1]), command[-1]))
            elif command in bot.commands:
                input = Input(conn, *out)
                input.trigger = trigger
                input.inp_unstripped = m.group(2)
                input.inp = input.inp_unstripped.strip()

                func, args = bot.commands[command]
                dispatch(input, "command", func, args, autohelp=True)

        # REGEXES
        for func, args in bot.plugs['regex']:
            m = args['re'].search(inp.lastparam)
            if m:
                input = Input(conn, *out)
                input.inp = m

                dispatch(input, "regex", func, args)
