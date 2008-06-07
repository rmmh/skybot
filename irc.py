import thread, socket, asyncore, asynchat, sys, re
import Queue
queue = Queue.Queue

class crlf_tcp(asynchat.async_chat):
    "Handles tcp connections that consist of lines ending with crlf"
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
        thread.start_new_thread(self.queue_read_loop,())
        asyncore.loop()

    def queue_read_loop(self):
        #this is an attempt at making this thread-safe
        #at least with this, only TWO things could be modifying the output
        #buffer at the same time
        while True:
            line = self.oqueue.get()
            print ">>> %r" % line
            self.push(line.encode('utf-8')+'\r\n')

    def collect_incoming_data(self, data):
        self.buffer += data
    
    def found_terminator(self):
        line = self.buffer
        # print repr(line)
        self.iqueue.put(line.encode('utf-8'))
        self.buffer = ''

irc_prefix_re = re.compile(r'(.*?) (.*?) (.*)')
irc_noprefix_re = re.compile(r'()(.*?) (.*)')
irc_param_re = re.compile(r'(?:^|(?<= ))(:.*|[^ ]*)')
irc_netmask_re = re.compile(r':?([^!@]*)!?([^@]*)@?(.*)')

class irc(object):
    "handles the IRC protocol"
    #see the docs/ folder for more information on the protocol

    def __init__(self, network, nick, port=6667):
        self.conn = crlf_tcp(network, port)
        thread.start_new_thread(self.conn.run,())
        self.out = queue() #responses from the server are placed here 
        # format: [rawline, (prefix, command, params),
        # (nick, user, host), command, paramlist]
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
            self.out.put([msg, (prefix, command, params), (nick, user, host),
                    command, paramlist])
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
        
s = irc('irc.synirc.net', 'skybot')
s.join("#cobol")

def readlines(s):
    for line in sys.stdin:
        print line
        s.msg('#cobol',line.rstrip())

thread.start_new_thread(readlines, (s,))

while True:
    try:
        print repr(s.out.get(timeout=2))
    except Queue.Empty:
        pass
    except KeyboardInterrupt:
        sys.exit()
