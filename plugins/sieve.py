import re

from util import hook


@hook.sieve
def sieve_suite(bot, input, func, args):
    events = args.get('events', ['PRIVMSG'])

    if input.command not in events and events != '*':
        return None

    if input.nick.lower()[-3:] == 'bot' and args.get('ignorebots', True):
        return None

    hook = args.get('hook', r'(.*)')

    if args.get('prefix', True):
        # add a prefix, unless it's a private message
        hook = (r'^(?:[.!]|' if input.chan != input.nick else r'^(?:[.!]?|') \
                + input.conn.nick + r'[:,]*\s*)' + hook

    input.re = re.match(hook, input.msg, flags=re.I)
    if input.re is None:
        return None

    input.inp_unstripped = ' '.join(input.re.groups())
    input.inp = input.inp_unstripped.strip()

    return input
