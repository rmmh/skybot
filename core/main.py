import thread
import traceback


print thread.stack_size(1024 * 512)  # reduce vm size


class Input(dict):
    def __init__(self, conn, raw, prefix, command, params,
                    nick, user, host, paraml, msg):

        chan = paraml[0].lower()
        if chan == conn.nick:  # is a PM
            chan = nick

        def say(msg):
            conn.msg(chan, msg)

        def reply(msg):
            conn.msg(chan, nick + ': ' + msg)

        def pm(msg):
            conn.msg(nick, msg)

        dict.__init__(self, conn=conn, raw=raw, prefix=prefix, command=command,
                    params=params, nick=nick, user=user, host=host,
                    paraml=paraml, msg=msg, server=conn.server, chan=chan,
                    say=say, reply=reply, pm=pm, bot=bot)

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value


def run(func, input):
    args = func._skybot_args
    if args:
        if 'db' in args:
            input['db'] = get_db_connection(input['server'])
        if 0 in args:
            out = func(input['inp'], **input)
        else:
            kw = dict((key, input[key]) for key in args if key in input)
            out = func(input['inp'], **kw)
    else:
        out = func(input['inp'])
    if out is not None:
        input['reply'](unicode(out))


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
