import os
import sqlite3
import random
import re
import time

from util import hook

dbname = "skybot.db"

def db_connect(db):
    conn = sqlite3.connect(db)
    conn.execute('''create table if not exists quotes
        (server, chan, nick, add_nick, msg, time real, deleted default 0, 
        primary key (server, chan, nick, msg))''')
    conn.commit()
    return conn

def add_quote(conn, server, chan, nick, add_nick, msg):
    now = time.time()
    print repr((conn, server, add_nick, nick, msg, time))
    conn.execute('''insert or fail into quotes (server, chan, nick, add_nick,
                    msg, time) values(?,?,?,?,?,?)''', 
                    (server, chan, nick, add_nick, msg, now))
    conn.commit()

def get_quotes_by_nick(conn, server, chan, nick):
    return conn.execute("select time, nick, msg from quotes where deleted!=1 "
            "and server=? and chan=? and lower(nick)=lower(?) order by time",
            (server, chan, nick)).fetchall()

def get_quotes_by_chan(conn, server, chan):
    return conn.execute("select time, nick, msg from quotes where deleted!=1 "
           "and server=? and chan=? order by time", (server, chan)).fetchall()


def format_quote(q, num, n_quotes):
    ctime, nick, msg = q
    return "[%d/%d] %s <%s> %s" % (num, n_quotes, 
        time.strftime("%Y-%m-%d", time.gmtime(ctime)), nick, msg)


@hook.command('q')
@hook.command
def quote(bot, input):
    ".q/.quote <nick/#chan> [#n]/.quote add <nick> <msg> -- gets " \
        "random or [#n]th quote by <nick> or from <#chan>/adds quote"

    dbpath = os.path.join(bot.persist_dir, dbname)
    conn = db_connect(dbpath)

    try:
        add = re.match(r"add\s+<?[^\w]?(\S+?)>?\s+(.*)", input.inp, re.I)
        retrieve = re.match(r"(\S+)(?:\s+#?(-?\d+))?", input.inp)
        chan = input.chan

        if add:
            nick, msg = add.groups()
            try:
                add_quote(conn, input.server, chan, nick, input.nick, msg)
            except sqlite3.IntegrityError: 
                return "message already stored, doing nothing."
            return "quote added."
        elif retrieve:
            select, num = retrieve.groups()
            
            by_chan = False
            if select.startswith('#'):
                by_chan = True
                quotes = get_quotes_by_chan(conn, input.server, select)
            else:
                quotes = get_quotes_by_nick(conn, input.server, chan, select)

            n_quotes = len(quotes)

            if not n_quotes:
                return "no quotes found"

            if num:
                num = int(num)

            if num:
                if num > n_quotes:
                    return "I only have %d quote%s for %s" % (n_quotes, 
                                ('s', '')[n_quotes == 1], select)
                else:
                    selected_quote = quotes[num - 1]
            else:
                num = random.randint(1, n_quotes)
                selected_quote = quotes[num - 1]

            return format_quote(selected_quote, num, n_quotes)
        else:
            return quote.__doc__
    finally:
        conn.commit()
        conn.close()
