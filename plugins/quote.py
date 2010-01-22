import os
import sqlite3
import random
import re
import time

from util import hook

dbname = "skybot.db"

def db_connect(db):
    conn = sqlite3.connect(db)
    conn.execute("create table if not exists quote"
                 "(server, nick, adder, msg unique, time real)")
    conn.commit()
    return conn

def add_quote(conn, server, adder, nick, msg):
    now = time.time()
    print repr((conn, server, adder, nick, msg, time))
    conn.execute("insert or fail into quote(server, nick, adder, msg, time) "
                 "values(?,?,?,?,?)", (server, nick, adder, msg, now))
    conn.commit()

def get_quotes(conn, server, nick):
    return conn.execute("select time, nick, msg from quote where server=?"
            " and nick LIKE ? order by time", (server, nick)).fetchall()
    # note: nick_name matches nick-name -- _ in a LIKE indicates any character
    #       this will probably be unnoticeable, and the fix is easy enough
       
@hook.command('q')
@hook.command
def quote(bot, input):
    ".q/.quote <nick> [#n]/.quote add <nick> <msg> -- retrieves " \
        "random/numbered quote, adds quote"

    dbpath = os.path.join(bot.persist_dir, dbname)
    conn = db_connect(dbpath)

    try:
        add = re.match(r"add\s+<?[^\w]?(\S+?)>?\s+(.*)", input.inp, re.I)
        retrieve = re.match(r"(\S+)(?:\s+#?(\d+))?", input.inp)

        if add:
            nick, msg = add.groups()
            try:
                add_quote(conn, input.server, input.nick, nick, msg)
            except sqlite3.IntegrityError: # message already in DB
                return "message already stored, doing nothing."
            return "quote added."
        elif retrieve:
            nick, num = retrieve.groups()

            quotes = get_quotes(conn, input.server, nick)
            n_quotes = len(quotes)

            if not n_quotes:
                return "no quotes found"

            if num:
                num = int(num)

            if num:
                if num > n_quotes:
                    return "I only have %d quote%s for %s" % (n_quotes, 
                                ('s', '')[n_quotes == 1], nick)
                else:
                    selected_quote = quotes[num - 1]
            else:
                num = random.randint(1, n_quotes)
                selected_quote = quotes[num - 1]

            ctime, nick, msg = selected_quote
            return "[%d/%d] %s <%s> %s" % (num, n_quotes, 
                    time.strftime("%Y-%m-%d", time.gmtime(ctime)), nick, msg)
        else:
            return quote.__doc__
    finally:
        conn.commit()
        conn.close()
