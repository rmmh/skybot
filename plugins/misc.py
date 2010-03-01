from util import hook
import socket

socket.setdefaulttimeout(5)  # global setting


#autorejoin channels
@hook.event('KICK')
def rejoin(inp, paraml=[], conn=None):
    if paraml[1] == conn.nick:
        if paraml[0].lower() in conn.channels:
            conn.join(paraml[0])


#join channels when invited
@hook.event('INVITE')
def invite(inp, command='', conn=None):
    if command == 'INVITE':
        conn.join(inp)


#join channels when server says hello & identify bot
@hook.event('004')
def onjoin(inp, conn=None):
    for channel in conn.channels:
        conn.join(channel)

    nickserv_password = conn.conf.get('nickserv_password', '')
    nickserv_name = conn.conf.get('nickserv_name', 'nickserv')
    nickserv_command = conn.conf.get('nickserv_command', 'IDENTIFY %s')
    if nickserv_password:
        conn.msg(nickserv_name, nickserv_command % nickserv_password)
