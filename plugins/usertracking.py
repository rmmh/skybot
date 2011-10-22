import re
import time

from util import hook


class Users(object):
    def __init__(self, users={}, channels={}):
        self.users = dict(users)
        self.channels = dict(channels)

    def __getitem__(self, item):
        try:
            return self.users[item]
        except KeyError:
            return self.channels[item]

    def _join(self, nick, user, host, channel, modes=""):
        userobj = self._user(nick, user, host)
        chanobj = self._chan(channel)
        chanobj.users[nick] = userobj
        modes = modes.replace("@", "o").replace("+", "v")
        chanobj.usermodes[nick] = set(modes)

    def _exit(self, nick, channel):
        "all types of channel-=user events"
        chanobj = self.channels[channel]
        del chanobj.users[nick]
        del chanobj.usermodes[nick]

    def _chnick(self, old, new):
        print "changing nick '%s' to '%s'" % (old, new)
        user = self.users[old]
        del self.users[old]
        self.users[new] = user
        user.nick = new

    def _mode(self, chan, mode, argument=None):
        if chan not in self.channels:
            return
        changetype = mode[0]
        modeid = mode[1]
        if modeid in "ov":
            if changetype == "+":
                self.channels[chan].usermodes[argument].add(modeid)
            else:
                self.channels[chan].usermodes[argument].remove(modeid)
        else:
            if changetype == "+":
                self.channels[chan].modes[modeid] = argument
            else:
                del self.channels[chan].modes[modeid]

    def _trydelete(self, nick):
        for i in self.channels.values():
            if nick in i.users:
                return
        del self.users[nick]

    def _user(self, nick, user, host):
        if nick in self.users:
            userobj = self.users[nick]
        else:
            userobj = User(nick, user, host)
            self.users[nick] = userobj
        return userobj

    def _chan(self, name):
        if name in self.channels:
            chanobj = self.channels[name]
        else:
            chanobj = Channel(name, self.users)
            self.channels[name] = chanobj
        return chanobj


class User(object):
    def __init__(self, nick, user, host, lastmsg=0):
        self.nick = nick
        self.user = user
        self.host = host
        self.realname = None
        self.channels = None
        self.server = None
        self.authed = None
        self.lastmsg = lastmsg or time.time()


class Channel(object):
    def __init__(self, name, users, topic=None):
        self.name = name
        self.topic = topic
        self.users = Userdict(users)
        self.usermodes = Userdict(users)
        self.modes = dict()

    def isop(self, nick):
        return "o" in self.usermodes[nick]

    def isvoice(self, nick):
        return "v" in self.usermodes[nick]


class Userdict(dict):
    def __init__(self, users, *args, **named):
        self.users = users
        dict.__init__(self, *args, **named)

    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, self.users[item])
        except KeyError:
            return dict.__getitem__(self, item)

    def __setitem__(self, item, value):
        try:
            return dict.__setitem__(self, self.users[item], value)
        except KeyError:
            return dict.__setitem__(self, item, value)


@hook.sieve
def valueadd(bot, input, func, kind, args):
    if not hasattr(input.conn, "users"):
        input.conn.users = Users()
        botuser = User(input.nick, input.nick, "127.0.0.1")
        input.conn.users.users[input.nick] = botuser

    input["users"] = input.conn.users
    userinfo = input.conn.users._user(input.nick, input.user, input.host)
    input["userinfo"] = userinfo
    if input.chan in input.conn.users.channels:
        input["chaninfo"] = input.conn.users[input.chan]
    else:
        input["chaninfo"] = None
    return input


flag_re = re.compile(r"^([@+]*)(.*)$")


@hook.event("332 353 311 319 312 330 318")
@hook.event("JOIN PART KICK QUIT PRIVMSG MODE NICK")
@hook.singlethread
def tracking(inp, command=None, input=None, users=None):
    if command == "353":  # when the names list comes in
        chan = inp[2]
        names = inp[3]
        for name in names.split(" "):
            match = flag_re.match(name)
            flags = match.group(1)
            nick = match.group(2)
            users._join(nick, None, None, chan, flags)
    elif command == "311":  # whois: nick, user, host, realname"
        nick = inp[1]
        user = inp[2]
        host = inp[3]
        if nick not in input.conn.users.users:
            users._user(nick, user, host)
        users[nick].realname = inp[5]
    elif command == "319":  # whois: channel list
        users[inp[1]].channels = inp[2].split(" ")
    elif command == "312":  # whois: server
        users[inp[1]].server = inp[2]
    elif command == "330":  # whois: user logged in
        print inp
        users[inp[1]].authed = inp[2]
    elif command == "318":  # whois: end of whois
        user = users[inp[1]]
        user.authed = user.authed or ""
    elif command == "JOIN":
        users._join(input.nick, input.user, input.host, input.chan)
    elif command in ["PART", "KICK", "QUIT"]:
        for channel in users.channels.values():
            if input.nick in channel.users:
                users._exit(input.nick, channel.name)
        users._trydelete(input.nick)
    elif command == "PRIVMSG":  # updates last seen time
        users[input.nick].lastmsg = time.time()
    elif command == "MODE":  # mode changes - getting op and suchh
        users._mode(*inp)
    elif command == "NICK":
        users._chnick(input.nick, inp[0])


@hook.command
def mymodes(inp, input=None, users=None):
    modes = users[input.chan].usermodes[input.nick]
    if len(modes):
        return "+" + "".join(modes)
    else:
        return "but you have no modes ..."
