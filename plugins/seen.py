" seen.py: written by sklnd in about two beers July 2009"

import time
import unittest

from util import hook, timesince


def db_init(db):
    "check to see that our db has the the seen table and return a connection."
    db.execute("create table if not exists seen(name, time, quote, chan, "
               "primary key(name, chan))")
    db.commit()


@hook.singlethread
@hook.event('PRIVMSG', ignorebots=False)
def seeninput(paraml, input=None, db=None, bot=None):
    db_init(db)
    db.execute("insert or replace into seen(name, time, quote, chan)"
               "values(?,?,?,?)", (input.nick.lower(), time.time(), input.msg,
                                   input.chan))
    db.commit()


@hook.command
def seen(inp, nick='', chan='', db=None, input=None):
    ".seen <nick> -- Tell when a nickname was last in active in irc"

    inp = inp.lower()

    if input.conn.nick.lower() == inp:
        # user is looking for us, being a smartass
        return "You need to get your eyes checked."

    if inp == nick.lower():
        return "Have you looked in a mirror lately?"

    db_init(db)

    last_seen = db.execute("select name, time, quote from seen where"
                           " name = ? and chan = ?", (inp, chan)).fetchone()

    if last_seen:
        reltime = timesince.timesince(last_seen[1])
        if last_seen[2][0:1] == "\x01":
            return '%s was last seen %s ago: *%s %s*' % \
                (inp, reltime, inp, last_seen[2][8:-1])
        else:
            return '%s was last seen %s ago saying: %s' % \
                (inp, reltime, last_seen[2])
    else:
        return "I've never seen %s" % inp


class SeenTest(unittest.TestCase):
    class Mock(object):
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    def setUp(self):
        import sqlite3
        self.db = sqlite3.connect(':memory:')

    def seeninput(self, nick, msg, chan='#test'):
        seeninput(None, db=self.db,
                  input=self.Mock(nick=nick, msg=msg, chan=chan))

    def seen(self, inp, nick='bob', chan='#test', bot_nick='skybot'):
        return seen(inp, nick=nick, chan=chan, db=self.db,
                    input=self.Mock(conn=self.Mock(nick=bot_nick)))

    def test_missing(self):
        assert "I've never seen nemo" in self.seen('NEMO')

    def test_seen(self):
        self.seeninput('nemo', 'witty banter')
        assert 'nemo was last seen' in self.seen('nemo')
        assert 'witty banter' in self.seen('nemo')

    def test_seen_missing_channel(self):
        self.seeninput('nemo', 'msg', chan='#secret')
        assert 'never seen' in self.seen('nemo')

    def test_seen_ctcp(self):
        self.seeninput('nemo', '\x01ACTION test lol\x01')
        assert self.seen('nemo').endswith('ago: *nemo test lol*')

    def test_snark_eyes(self):
        assert 'eyes checked' in self.seen('skybot', bot_nick='skybot')

    def test_snark_mirror(self):
        assert 'mirror' in self.seen('bob', nick='bob')
