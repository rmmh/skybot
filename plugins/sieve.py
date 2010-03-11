from util import hook


@hook.sieve
def sieve_suite(bot, input, func, kind, args):    
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
    
    return input
