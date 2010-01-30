import os
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
        if input.chan == input.nick: # private message, prefix not required
            prefix = r'^(?:[.!]?|'
        else:
            prefix = r'^(?:[.!]|'
        hook = prefix + input.conn.nick + r'[:,]*\s)' + hook

    input.re = re.match(hook, input.msg, flags=re.I)
    if input.re is None:
        return None

    acl = bot.config.get('acls', {}).get(func.__name__)
    if acl:
        print acl
        if 'deny-except' in acl:
            allowed_channels = map(str.lower, acl['deny-except'])
            if input.chan.lower() not in allowed_channels:
                return None
        if 'allow-except' in acl:
            denied_channels = map(str.lower, acl['allow-except'])
            if input.chan.lower() in denied_channels:
                return None

    input.inp_unstripped = ' '.join(input.re.groups())
    input.inp = input.inp_unstripped.strip()

    return input
