" seen.py: written by sklnd in about two beers July 2009"

import time

from util import hook, timesince


@hook.thread
@hook.event('PRIVMSG')
def seeninput(inp, input=None, bot=None):
    db = bot.get_db_connection(input.server)
    db_init(db)
    db.execute("insert or replace into seen(name, time, quote, chan)"
        "values(?,?,?,?)", (input.nick.lower(), time.time(), input.msg,
            input.chan))
    db.commit()


@hook.command
def seen(inp, nick='', chan='', db=None):
    ".seen <nick> -- Tell when a nickname was last in active in irc"

    if not inp:
        return seen.__doc__

    if inp.lower() == nick.lower():
        return "Have you looked in a mirror lately?"

    db_init(db)

    last_seen = db.execute("select name, time, quote from seen where name"
                           " like ? and chan = ?", (inp, chan)).fetchone()

    if last_seen:
        reltime = timesince.timesince(last_seen[1])
        if last_seen[0] != inp.lower():  # for glob matching
            inp = last_seen[0]
        return '%s was last seen %s ago saying: %s' % \
                    (inp, reltime, last_seen[2])
    else:
        return "I've never seen %s" % inp


def db_init(db):
    "check to see that our db has the the seen table and return a connection."
    db.execute("create table if not exists seen(name, time, quote, chan, "
                 "primary key(name, chan))")
    db.commit()
