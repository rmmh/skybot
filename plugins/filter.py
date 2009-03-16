import re

import hook

@hook.sieve
def filter_suite(bot, input, func, args):
    args.setdefault('events', ['PRIVMSG'])

    if input.command not in args['events']:
        if args['events'] != '*':
            return None

    args.setdefault('hook', r'(.*)')
    args.setdefault('prefix', True)
    
    hook = args['hook']
    if args['prefix']:
        hook = bot.commandprefix + args['hook']

    if input.command == 'INVITE':
            print func, hook

    input.re = re.match(hook, input.msg)
    if input.re is None:
        return None

    input.inp = ' '.join(input.re.groups())

    return input
