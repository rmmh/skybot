import socket
import time

from util import hook

socket.setdefaulttimeout(10)  # global setting


#autorejoin channels
@hook.event('KICK')
def rejoin(paraml, conn=None):
    if paraml[1] == conn.nick:
        if paraml[0].lower() in conn.channels:
            conn.join(paraml[0])


#join channels when invited
@hook.event('INVITE')
def invite(paraml, conn=None):
    conn.join(paraml[-1])


#join channels when server says hello & identify bot
@hook.event('004')
def onjoin(paraml, conn=None):
    nickserv_password = conn.conf.get('nickserv_password', '')
    nickserv_name = conn.conf.get('nickserv_name', 'nickserv')
    nickserv_command = conn.conf.get('nickserv_command', 'IDENTIFY %s')
    if nickserv_password:
        conn.msg(nickserv_name, nickserv_command % nickserv_password)
        time.sleep(1)
    
    for channel in conn.channels:
        conn.join(channel)
        time.sleep(1) # don't flood JOINs
