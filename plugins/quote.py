import random
import re
import time

from util import hook


def add_quote(db, chan, nick, add_nick, msg):
    now = time.time()
    db.execute('''insert or fail into quote (chan, nick, add_nick,
                    msg, time) values(?,?,?,?,?)''',
                    (chan, nick, add_nick, msg, now))
    db.commit()


def get_quotes_by_nick(db, chan, nick):
    return db.execute("select time, nick, msg from quote where deleted!=1 "
            "and chan=? and lower(nick)=lower(?) order by time",
            (chan, nick)).fetchall()


def get_quotes_by_chan(db, chan):
    return db.execute("select time, nick, msg from quote where deleted!=1 "
           "and chan=? order by time", (chan,)).fetchall()


def format_quote(q, num, n_quotes):
    ctime, nick, msg = q
    return "[%d/%d] %s <%s> %s" % (num, n_quotes,
        time.strftime("%Y-%m-%d", time.gmtime(ctime)), nick, msg)


@hook.command('q')
@hook.command
def quote(inp, nick='', chan='', db=None):
    ".q/.quote <nick/#chan> [#n]/.quote add <nick> <msg> -- gets " \
        "random or [#n]th quote by <nick> or from <#chan>/adds quote"

    db.execute("create table if not exists quote"
        "(chan, nick, add_nick, msg, time real, deleted default 0, "
        "primary key (chan, nick, msg))")
    db.commit()

    try:
        add = re.match(r"add\s+<?[^\w]?(\S+?)>?\s+(.*)", inp, re.I)
        retrieve = re.match(r"(\S+)(?:\s+#?(-?\d+))?", inp)

        if add:
            quoted_nick, msg = add.groups()
            try:
                add_quote(db, chan, quoted_nick, nick, msg)
            except db.IntegrityError:
                return "message already stored, doing nothing."
            return "quote added."
        elif retrieve:
            select, num = retrieve.groups()

            by_chan = False
            if select.startswith('#'):
                by_chan = True
                quotes = get_quotes_by_chan(db, select)
            else:
                quotes = get_quotes_by_nick(db, chan, select)

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
        else:
            return quote.__doc__
    finally:
        db.commit()
        db.close()
