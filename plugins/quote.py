import random
import re
import time

from util import hook

def format_quote(q, num, n_quotes):
    """Returns a formatted string of a quote"""
    ctime, nick, msg = q
    return "[%d/%d] %s <%s> %s" % (num, n_quotes,
        time.strftime("%Y-%m-%d", time.gmtime(ctime)), nick, msg)

def create_table_if_not_exists(db):
    """Creates an empty quote table if one does not already exist"""
    db.execute('''CREATE TABLE IF NOT EXISTS quote (
                     chan, 
                     nick, 
                     add_nick, 
                     msg, 
                     time real,
                     deleted default 0, 
                     PRIMARY KEY (chan, nick, msg)
                  )''')
    db.commit()

def add_quote(db, chan, nick, add_nick, msg):
    """Adds a quote to a nick, returns message string"""
    try:
        db.execute('''INSERT OR FAIL INTO quote 
                      (chan, nick, add_nick, msg, time) 
                      VALUES(?,?,?,?,?)''',
                   (chan, nick, add_nick, msg, time.time()))
        db.commit()
    except db.IntegrityError:
        return "message already stored, doing nothing."
    return "quote added."


def del_quote(db, chan, nick, add_nick, msg):
    """Deletes a quote from a nick"""
    db.execute('''UPDATE quote 
                  SET deleted = 1 
                  WHERE chan=? 
                  AND lower(nick)=lower(?)
                  AND msg=msg''')
    db.commit()


def get_quotes_by_nick(db, chan, nick):
    """Return an array of every quote from a nick"""
    return db.execute('''SELECT time, nick, msg
                         FROM quote
                         WHERE deleted != 1 
                         AND chan=? and lower(nick)=lower(?)
                         ORDER BY time''', (chan, nick)).fetchall()


def get_quotes_by_chan(db, chan):
    """Return an array of every quote from a channel"""
    return db.execute('''SELECT time, nick, msg 
                         FROM quote
                         WHERE deleted!=1
                         AND chan=? 
                         ORDER BY time''', (chan,)).fetchall()



@hook.command('q')
@hook.command
def quote(inp, nick='', chan='', db=None):
    """.q/.quote [#chan] [nick] [#n]/.quote add <nick> <msg> --

    gets random or [#n]th quote by <nick> or from <#chan>/adds quote
    """

    create_table_if_not_exists(db)

    add = re.match(r"add[^\w@]+(\S+?)>?\s+(.*)", inp, re.I)
    retrieve_nick = re.match(r"(\S+)(?:\s+#?(-?\d+))?$", inp)
    retrieve_chan = re.match(r"(#\S+)\s+(\S+)(?:\s+#?(-?\d+))?$", inp)

    if add:
        quoted_nick, msg = add.groups()
        return add_quote(db, chan, quoted_nick, nick, msg)
    elif retrieve_nick:
        select, num = retrieve_nick.groups()

        by_chan = False
        if select.startswith('#'):
            by_chan = True
            quotes = get_quotes_by_chan(db, select)
        else:
            quotes = get_quotes_by_nick(db, chan, select)
    elif retrieve_chan:
        chan, nick, num = retrieve_chan.groups()

        quotes = get_quotes_by_nick(db, chan, nick)
    else:
        return quote.__doc__

    n_quotes = len(quotes)

    if not n_quotes:
        return "no quotes found"

    if num:
        num = int(num)

    if num:
        if num > n_quotes or (num < 0 and num < -n_quotes):
            return "I only have %d quote%s for %s" % (n_quotes,
                        ('s', '')[n_quotes == 1], select)
        elif num < 0:
            selected_quote = quotes[num]
            num = n_quotes + num + 1
        else:
            selected_quote = quotes[num - 1]
    else:
        num = random.randint(1, n_quotes)
        selected_quote = quotes[num - 1]

    return format_quote(selected_quote, num, n_quotes)
