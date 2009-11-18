import sys
import re
import socket
import thread
import asyncore
import asynchat
import Queue


def decode(txt):
    for codec in ('utf-8', 'iso-8859-1', 'shift_jis', 'cp1252'):
        try:
            return txt.decode(codec)
        except UnicodeDecodeError:
            continue
    return txt.decode('utf-8', 'ignore')


class crlf_tcp(asynchat.async_chat):
    "Handles tcp connections that consist of utf-8 lines ending with crlf"

    def __init__(self, host, port):
        asynchat.async_chat.__init__(self)
        self.set_terminator('\r\n')
        self.buffer = ""
        self.obuffer = ""
        self.oqueue = Queue.Queue() #where we stick things that need to be sent
        self.iqueue = Queue.Queue() #where we stick things that were received
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 0)
        self.host = host
        self.port = port

    def run(self):
        self.connect((self.host, self.port))
        asyncore.loop()

    def handle_connect(self):
        thread.start_new_thread(self.queue_read_loop, ())

    def queue_read_loop(self):
        while True:
            line = self.oqueue.get().splitlines()[0][:500]
            print ">>> %r" % line
            self.push(line.encode('utf-8', 'replace') + '\r\n')

    def collect_incoming_data(self, data):
        self.buffer += data

    def found_terminator(self):
        line = self.buffer
        self.iqueue.put(decode(line))
        self.buffer = ''

irc_prefix_rem = re.compile(r'(.*?) (.*?) (.*)').match
irc_noprefix_rem = re.compile(r'()(.*?) (.*)').match
irc_netmask_rem = re.compile(r':?([^!@]*)!?([^@]*)@?(.*)').match
irc_param_ref = re.compile(r'(?:^|(?<= ))(:.*|[^ ]+)').findall


class irc(object):
    "handles the IRC protocol"
    #see the docs/ folder for more information on the protocol
    def __init__(self, server, nick, port=6667, channels=[]):
        self.server = server
        self.conn = crlf_tcp(server, port)
        self.channels = channels
        thread.start_new_thread(self.conn.run, ())
        self.out = Queue.Queue() #responses from the server are placed here
        # format: [rawline, prefix, command, params,
        # nick, user, host, paramlist, msg]
        self.nick = nick
        self.set_nick(nick)
        self.cmd("USER", ["skybot v0.01", "0", "bot"])
        thread.start_new_thread(self.parse_loop, ())

    def parse_loop(self):
        while True:
            msg = self.conn.iqueue.get()
            if msg.startswith(":"): #has a prefix
                prefix, command, params = irc_prefix_rem(msg).groups()
            else:
                prefix, command, params = irc_noprefix_rem(msg).groups()
            nick, user, host = irc_netmask_rem(prefix).groups()
            paramlist = irc_param_ref(params)
            lastparam = ""
            if paramlist and paramlist[-1].startswith(':'):
                    lastparam = paramlist[-1][1:]
            self.out.put([msg, prefix, command, params, nick, user, host,
                    paramlist, lastparam])
            if command == "PING":
                self.cmd("PONG", [params])

    def set_nick(self, nick):
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
