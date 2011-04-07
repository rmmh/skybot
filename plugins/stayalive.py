import time

from util import hook

@hook.event('004')
def stayalive(paraml, conn=None):
    # Ping server every n seconds
    #
    # if we are behind the proxy/NAT, we need to constantly ping the server by ourselves
    # otherwise we will be kicked with ping timeout
    mode = conn.conf.get('stayalive')
    if mode:
        while True:
        	# ping the server every n seconds, XChat for example pings every 15 seconds
            time.sleep(conn.conf.get('stayalive_delay', 20))
            conn.cmd('PING :%s' % conn.conf.get('nick'))
