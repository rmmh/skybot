from util import hook


@hook.event('KICK INVITE')
def rejoin(bot, input):
    if input.command == 'KICK':
        if input.paraml[1] == bot.bot.nick:
            if input.paraml[0] == bot.bot.channel:
                bot.join(input.paraml[0])

    if input.command == 'INVITE':
        bot.join(input.inp)
