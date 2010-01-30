import sys
import re
import socket
import time
import thread
import Queue

def decode(txt):
    for codec in ('utf-8', 'iso-8859-1', 'shift_jis', 'cp1252'):
        try:
            return txt.decode(codec)
        except UnicodeDecodeError:
            continue
    return txt.decode('utf-8', 'ignore')


class crlf_tcp(object):
    "Handles tcp connections that consist of utf-8 lines ending with crlf"

    def __init__(self, host, port, timeout=300):
        self.ibuffer = ""
        self.obuffer = ""
        self.oqueue = Queue.Queue() # lines to be sent out
        self.iqueue = Queue.Queue() # lines that were received
        self.socket = socket.socket(socket.AF_INET, socket.TCP_NODELAY)
        self.host = host
        self.port = port
        self.timeout = timeout

    def run(self):
        self.socket.connect((self.host, self.port))
        thread.start_new_thread(self.recv_loop, ())
        thread.start_new_thread(self.send_loop, ())

    def recv_loop(self):
        last_timestamp = time.time()
        while True:
            try:
                data = self.socket.recv(4096)
                self.ibuffer += data
                if data:
                    last_timestamp = time.time()
                else:
                    if time.time() - last_timestamp > self.timeout:
                        self.iqueue.put(StopIteration)
                        self.socket.close()
                        return
                    time.sleep(1)
            except socket.timeout, e:
                if time.time() - last_timestamp > self.timeout:
                    self.iqueue.put(StopIteration)
                    self.socket.close()
                    return
                continue
            
            while '\r\n' in self.ibuffer:
                line, self.ibuffer = self.ibuffer.split('\r\n', 1)
                self.iqueue.put(decode(line))

    def send_loop(self):
        while True:
            line = self.oqueue.get().splitlines()[0][:500]
            print ">>> %r" % line
            self.obuffer += line.encode('utf-8', 'replace') + '\r\n'
            while self.obuffer:
                sent = self.socket.send(self.obuffer)
                self.obuffer = self.obuffer[sent:]

irc_prefix_rem = re.compile(r'(.*?) (.*?) (.*)').match
irc_noprefix_rem = re.compile(r'()(.*?) (.*)').match
irc_netmask_rem = re.compile(r':?([^!@]*)!?([^@]*)@?(.*)').match
irc_param_ref = re.compile(r'(?:^|(?<= ))(:.*|[^ ]+)').findall


class irc(object):
    "handles the IRC protocol"
    #see the docs/ folder for more information on the protocol
    def __init__(self, server, nick, port=6667, channels=[], conf={}):
        self.channels = channels
        self.conf = conf
        self.server = server
        self.port = port
        self.nick = nick

        self.out = Queue.Queue() #responses from the server are placed here
        # format: [rawline, prefix, command, params,
        # nick, user, host, paramlist, msg]
        self.connect()

        thread.start_new_thread(self.parse_loop, ())

    def connect(self):
        self.conn = crlf_tcp(self.server, self.port)
        thread.start_new_thread(self.conn.run, ())
        self.set_nick(self.nick)
        self.cmd("USER",
            [conf.get('user', 'skybot'), "3", "*", ':' + conf.get('realname',
             'Python bot - http://bitbucket.org/Scaevolus/skybot/')])

    def parse_loop(self):
        while True:
            msg = self.conn.iqueue.get()

            if msg == StopIteration:
                self.connect()
                continue

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
