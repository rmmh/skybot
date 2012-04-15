import socket
import time

from util import hook, http


socket.setdefaulttimeout(10)  # Global setting


@hook.event('KICK')
def rejoin(paraml, conn=None):
    """Autorejoin channels."""
    if paraml[1] == conn.nick:
        if paraml[0].lower() in conn.channels:
            conn.join(paraml[0])


@hook.event('INVITE')
def invite(paraml, conn=None):
    """Join channels when invited."""
    conn.join(paraml[-1])


@hook.event('004')
def onjoin(paraml, conn=None, bot=None):
    # Identify to services
    nickserv_password = conn.conf.get('nickserv_password', '')
    nickserv_name = conn.conf.get('nickserv_name', 'nickserv')
    nickserv_command = conn.conf.get('nickserv_command', 'IDENTIFY %s')
    if nickserv_password:
        conn.msg(nickserv_name, nickserv_command % nickserv_password)
        time.sleep(1)

    # Set mode on self
    mode = conn.conf.get('mode')
    if mode:
        conn.cmd('MODE', [conn.nick, mode])

    # Join channels
    for channel in conn.channels:
        conn.join(channel)
        time.sleep(1)  # Don't flood JOINs

    # Set HTTP User-Agent
    # TODO: The http library should retrieve the user-agent and not the other
    # way around.
    http.ua_skybot = ('Skybot/r%d %s (http://github.com/rmmh/skybot)' %
                      (bot.version["REV_NUMBER"], bot.version["SHORT_HASH"]))


@hook.regex(r'^\x01VERSION\x01$')
def version(inp, notice=None, bot=None):
    notice('\x01VERSION Skybot (r%d %s) - http://github.com/rmmh/skybot/\x01' %
           (bot.version["REV_NUMBER"], bot.version["SHORT_HASH"]))
