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

def get_quote_by_nick(db, chan, nick, num=False):
    """Returns a formatted quote from a nick, random or selected by number"""
    count = db.execute('''SELECT COUNT(*)
                          FROM quote
                          WHERE deleted != 1
                          AND chan = ?
                          AND lower(nick) = lower(?)''', (chan, nick)).fetchall()[0][0]
    if count == 0: # If there are no quotes in the database
        return "I don't have any quotes for %s" % nick
    if num and num < 0: # If the selected quote is less than 0, count back if possible
        num = count + num + 1 if num + count > -1 else count + 1
    if num and num > count: # If a number is given and and there are not enough quotes
        return "I only have %d quote%s for %s" % (count, ('s', '')[count == 1], nick)
    if num is False: #If a number is not given, select a random one
        num = random.randint(1, count)

    quote = db.execute('''SELECT time, nick, msg
                          FROM quote
                          WHERE deleted != 1
                          AND chan = ?
                          AND lower(nick) = lower(?)
                          ORDER BY time
                          LIMIT ?, 1''', (chan, nick, (num-1))).fetchall()[0]
    return format_quote(quote, num, count)

def get_quote_by_chan(db, chan, num=False): 
    """Returns a formatted quote from a channel, random or selected by number"""
    count = db.execute('''SELECT COUNT(*)
                          FROM quote
                          WHERE deleted != 1
                          AND chan = ?''', (chan,)).fetchall()[0][0]
    if count == 0: # If there are no quotes in the database
        return "The channel %s does not have any quotes" % chan
    if num and num < 0: #If the selected quote is less than 0, count back if possible
        num = count + num + 1 if num + count > -1 else count + 1
    if num and num > count: # If a number is given and and there are not enough quotes
        return "I only have %d quote%s for %s" % (count, ('s', '')[count == 1], chan)
    if not num: #If a number is not given, select a random one
        num = random.randint(1, count)

    quote = db.execute('''SELECT time, nick, msg 
                          FROM quote
                          WHERE deleted != 1
                          AND chan = ? 
                          ORDER BY time
                          LIMIT ?, 1''', (chan, (num -1))).fetchall()[0]
    return format_quote(quote, num, count)

@hook.command('q')
@hook.command
def quote(inp, nick='', chan='', db=None):
    ".q/.quote [#chan] [nick] [#n]/.quote add <nick> <msg> -- gets " \
        "random or [#n]th quote by <nick> or from <#chan>/adds quote"
    create_table_if_not_exists(db)

    add = re.match(r"add[^\w@]+(\S+?)>?\s+(.*)", inp, re.I)
    retrieve = re.match(r"(\S+)(?:\s+#?(-?\d+))?$", inp)
    retrieve_chan = re.match(r"(#\S+)\s+(\S+)(?:\s+#?(-?\d+))?$", inp)

    if add:
        quoted_nick, msg = add.groups()
        return add_quote(db, chan, quoted_nick, nick, msg)
    elif retrieve:
        select, num = retrieve.groups()
        by_chan = True if select.startswith('#') else False
        if num:
            num = int(num)
        if by_chan: 
            return get_quote_by_chan(db, select, num)
        else:
            return get_quote_by_nick(db, chan, select, num)
    elif retrieve_chan:
        chan, nick, num = retrieve_chan.groups()
        return get_quote_by_nick(db, chan, nick, num)
    
    return quote.__doc__
