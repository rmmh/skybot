import sys
import re
import socket
import thread 
import asyncore
import asynchat
import Queue

queue = Queue.Queue

def decode(txt, codecs=['utf-8', 'iso-8859-1', 'shift_jis', 'cp1252']):
    if len(codecs) == 0:
        return txt.decode('utf-8', 'ignore')
    try:
        return txt.decode(codecs[0])
    except UnicodeDecodeError:
        return decode(txt, codecs[1:])

class crlf_tcp(asynchat.async_chat):
    "Handles tcp connections that consist of utf-8 lines ending with crlf"
    def __init__(self, host, port):
        asynchat.async_chat.__init__(self)
        self.set_terminator('\r\n')
        self.buffer = ""
        self.obuffer = ""
        self.oqueue = queue() #where we stick things that need to be sent
        self.iqueue = queue() #where we stick things that were received
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port

    def run(self):
        self.connect((self.host, self.port))
        asyncore.loop()

    def handle_connect(self):
        thread.start_new_thread(self.queue_read_loop,())

    def queue_read_loop(self):
        while True:
            line = self.oqueue.get()
            print ">>> %r" % line   
            self.push(line.encode('utf-8','replace')+'\r\n')

    def collect_incoming_data(self, data):
        self.buffer += data
    
    def found_terminator(self):
        line = self.buffer
        self.iqueue.put(decode(line))
        self.buffer = ''

irc_prefix_re = re.compile(r'(.*?) (.*?) (.*)')
irc_noprefix_re = re.compile(r'()(.*?) (.*)')
irc_param_re = re.compile(r'(?:^|(?<= ))(:.*|[^ ]+)')
irc_netmask_re = re.compile(r':?([^!@]*)!?([^@]*)@?(.*)')

class irc(object):
    "handles the IRC protocol"
    #see the docs/ folder for more information on the protocol

    def __init__(self, network, nick, port=6667):
        self.conn = crlf_tcp(network, port)
        thread.start_new_thread(self.conn.run,())
        self.out = queue() #responses from the server are placed here 
        # format: [rawline, prefix, command, params,
        # nick, user, host, paramlist, msg]
        self.nick(nick)
        self.cmd("USER", ["skybot v0.01", "0", "bot"])
        thread.start_new_thread(self.parse_loop,())

    def parse_loop(self):
        while True:
            msg = self.conn.iqueue.get()
            if msg.startswith(":"): #has a prefix
                prefix, command, params = irc_prefix_re.match(msg).groups()
            else:
                prefix, command, params = irc_noprefix_re.match(msg).groups()
            nick, user, host = irc_netmask_re.match(prefix).groups()
            paramlist = irc_param_re.findall(params)
            lastparam = ""
            if paramlist and paramlist[-1].startswith(':'):
                    lastparam = paramlist[-1][1:]
            self.out.put([msg, prefix, command, params, nick, user, host,
                    paramlist, lastparam])
            if command == "PING":
                self.cmd("PONG", [params])

    def nick(self, nick):
        self.cmd("NICK", [nick])

    def join(self, channel):
        self.cmd("JOIN", [":"+channel])

    def msg(self, target, text):
        self.cmd("PRIVMSG", [target, ":"+text])

    def cmd(self, command, params=None):
        if params:
            self.send(command+' '+' '.join(params))
        else:
            self.send(command)

    def send(self, str):
        self.conn.oqueue.put(str)
