import re

def setup(bot):
    bot.filter("default_filters", filter_suite)

def filter_suite(bot, func, args, input):
    args.setdefault('events', ['PRIVMSG'])

    if input.command not in args['events']:
        return False

    args.setdefault('hook', r'(.*)')
    args.setdefault('prefix', True)
    
    hook = args['hook']
    if args['prefix']:
        hook = bot.commandprefix + args['hook']

    m = re.match(hook, input.msg)
    if not m:
        return False
    
    input.re = m
    return input
