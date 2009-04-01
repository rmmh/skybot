import re

import hook

@hook.sieve
def sieve_suite(bot, input, func, args):
    events = args.get('events', ['PRIVMSG'])

    if input.command not in events and events != '*':
        return None

    if input.nick.lower()[-3:] == 'bot' and args.get('ignorebots', True):
        return None

    hook = args.get('hook', r'(.*)')
    args.setdefault('prefix', True)
    
    if args.get('prefix', True):
        hook = bot.commandprefix + hook

    if input.command == 'INVITE':
            print func, hook

    input.re = re.match(hook, input.msg, flags=re.I)
    if input.re is None:
        return None

    input.inp = ' '.join(input.re.groups())

    return input
