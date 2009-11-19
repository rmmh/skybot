from util import hook


#autorejoin channels
@hook.event('KICK')
def rejoin(bot, input):
    if input.paraml[1] == input.conn.nick:
        if input.paraml[0] in input.conn.channels:
            input.conn.join(input.paraml[0])

#join channels when invited
@hook.event('INVITE')
def invite(bot, input):
    if input.command == 'INVITE':
        input.conn.join(input.inp)

#join channels when server says hello & identify bot
@hook.event('004')
def onjoin(bot, input):
    for channel in input.conn.channels:
        input.conn.join(channel)

    nickserv_password = input.conn.conf.get('nickserv_password', '')
    nickserv_name = input.conn.conf.get('nickserv_name', 'nickserv')
    nickserv_command = input.conn.conf.get('nickserv_command', 'IDENTIFY %s')
    if nickserv_password:
        input.conn.msg(nickserv_name, nickserv_command % nickserv_password)
