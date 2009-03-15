import re

#filter
def filter_suite(bot, func, args, input):
    args.setdefault('events', ['PRIVMSG'])

    if input.command not in args['events']:
        if args['events'] != '*':
            return None

    args.setdefault('hook', r'(.*)')
    args.setdefault('prefix', True)
    
    hook = args['hook']
    if args['prefix']:
        hook = bot.commandprefix + args['hook']

    input.re = re.match(hook, input.msg)
    if input.re is None:
        return None

    input.inp = ' '.join(input.re.groups())

    return input
