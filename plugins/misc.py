from util import hook


@hook.event('KICK INVITE')
def rejoin(bot, input):
    if input.command == 'KICK':
        if input.paraml[1] == input.conn.nick:
            if input.paraml[0] in input.conn.channels:
                input.conn.join(input.paraml[0])

    if input.command == 'INVITE':
        input.conn.join(input.inp)
