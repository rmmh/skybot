import random
import re
import sqlite3
import time

from util import hook


def add_quote(conn, chan, nick, add_nick, msg):
    now = time.time()
    conn.execute('''insert or fail into quote (chan, nick, add_nick,
                    msg, time) values(?,?,?,?,?)''', 
                    (chan, nick, add_nick, msg, now))
    conn.commit()

def get_quotes_by_nick(conn, chan, nick):
    return conn.execute("select time, nick, msg from quote where deleted!=1 "
            "and chan=? and lower(nick)=lower(?) order by time",
            (chan, nick)).fetchall()

def get_quotes_by_chan(conn, chan):
    return conn.execute("select time, nick, msg from quote where deleted!=1 "
           "and chan=? order by time", (chan,)).fetchall()


def format_quote(q, num, n_quotes):
    ctime, nick, msg = q
    return "[%d/%d] %s <%s> %s" % (num, n_quotes, 
        time.strftime("%Y-%m-%d", time.gmtime(ctime)), nick, msg)

@hook.command('q')
@hook.command
def quote(bot, input):
    ".q/.quote <nick/#chan> [#n]/.quote add <nick> <msg> -- gets " \
        "random or [#n]th quote by <nick> or from <#chan>/adds quote"

    conn = bot.get_db_connection(input.server)
    conn.execute("create table if not exists quote"
        "(chan, nick, add_nick, msg, time real, deleted default 0, "
        "primary key (chan, nick, msg))")
    conn.commit()

    try:
        add = re.match(r"add\s+<?[^\w]?(\S+?)>?\s+(.*)", input.inp, re.I)
        retrieve = re.match(r"(\S+)(?:\s+#?(-?\d+))?", input.inp)
        chan = input.chan

        if add:
            nick, msg = add.groups()
            try:
                add_quote(conn, chan, nick, input.nick, msg)
            except sqlite3.IntegrityError: 
                return "message already stored, doing nothing."
            return "quote added."
        elif retrieve:
            select, num = retrieve.groups()
            
            by_chan = False
            if select.startswith('#'):
                by_chan = True
                quotes = get_quotes_by_chan(conn, select)
            else:
                quotes = get_quotes_by_nick(conn, chan, select)

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
