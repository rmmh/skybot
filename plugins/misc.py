#event: KICK INVITE
def rejoin(bot, input):
    if input.command == 'KICK':
        if input.paraml[1] == bot.bot.nick:
            bot.join(input.paraml[0])

    if input.command == 'INVITE':
        bot.join(input.inp)
