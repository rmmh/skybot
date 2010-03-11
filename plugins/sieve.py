import os
import re

from util import hook


@hook.sieve
def sieve_suite(bot, input, func, kind, args):    
    events = args.get('events', ['PRIVMSG'])

    if input.command not in events and '*' not in events:
        return None

    if input.command == 'PRIVMSG' and input.nick.lower()[-3:] == 'bot' \
            and args.get('ignorebots', True):
        return None

    acl = bot.config.get('acls', {}).get(func.__name__)
    if acl:
        if 'deny-except' in acl:
            allowed_channels = map(unicode.lower, acl['deny-except'])
            if input.chan.lower() not in allowed_channels:
                return None
        if 'allow-except' in acl:
            denied_channels = map(unicode.lower, acl['allow-except'])
            if input.chan.lower() in denied_channels:
                return None

#    input.inp_unstripped = ' '.join(input.re.groups())
#    input.inp = input.inp_unstripped.strip()

    return input
