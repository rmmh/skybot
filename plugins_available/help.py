from util import hook

@hook.command
def help(bot, input):
    ".help [command] -- gives a list of commands/help for a command"
    
    funcs = {}
    for csig, func, args in bot.plugs['command']:
        if args['hook'] != r'(.*)':
            if func.__doc__ is not None:
                funcs[csig[1]] = func

    if not input.inp.strip():
        input.pm('available commands: ' + ' '.join(sorted(funcs)))
    else:
        if input.inp in funcs:
            input.pm(funcs[input.inp].__doc__)
