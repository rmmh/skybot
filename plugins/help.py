from util import hook


@hook.command
def help(inp, bot=None, pm=None):
    ".help [command] -- gives a list of commands/help for a command"

    funcs = {}
    for csig, func, args in bot.plugs['command']:
        if args['hook'] != r'(.*)':
            if func.__doc__ is not None:
                funcs[csig[1]] = func

    if not inp:
        pm('available commands: ' + ' '.join(sorted(funcs)))
    else:
        if inp in funcs:
            pm(funcs[inp].__doc__)
