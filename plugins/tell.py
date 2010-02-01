" tell.py: written by sklnd in July 2009"
"       2010.01.25 - modified by Scaevolus"

import time

from util import hook, timesince

def get_tells(conn, user_to, chan):
    return conn.execute("select user_from, message, time from tell where"
                         " user_to=lower(?) and chan=? order by time", 
                         (user_to.lower(), chan)).fetchall()


@hook.command(hook=r'(.*)', prefix=False)
def tellinput(bot, input):
    if 'showtells' in input.inp.lower():
        return
    
    conn = db_connect(bot, input.server)

    tells = get_tells(conn, input.nick, input.chan)

    if tells:
        user_from, message, time = tells[0]
        reltime = timesince.timesince(time)

        reply = "%s said %s ago: %s" % (user_from, reltime, message)
        if len(tells) > 1:
            reply += " (+%d more, .showtells to view)" % (len(tells) - 1)

        conn.execute("delete from tell where user_to=lower(?) and message=?",
                     (input.nick, message))
        conn.commit()
        return reply

@hook.command
def showtells(bot, input):
    ".showtells -- view all pending tell messages (sent in PM)."
    
    conn = db_connect(bot, input.server)

    tells = get_tells(conn, input.nick, input.chan)
    
    if not tells:
        input.pm("You have no pending tells.")
        return

    for tell in tells:
        user_from, message, time = tell
        reltime = timesince.timesince(time)
        input.pm("%s said %s ago: %s" % (user_from, reltime, message))
    
    conn.execute("delete from tell where user_to=lower(?) and chan=?",
                  (input.nick, input.chan))
    conn.commit()

@hook.command
def tell(bot, input):
    ".tell <nick> <message> -- relay <message> to <nick> when <nick> is around"

    query = input.inp.split(' ', 1)

    if len(query) != 2 or not input.inp:
        return tell.__doc__

    user_to = query[0].lower()
    message = query[1].strip()
    user_from = input.nick
    
    if user_to == user_from.lower():
        return "No."

    conn = db_connect(bot, input.server)

    if conn.execute("select count() from tell where user_to=?",
                    (user_to,)).fetchone()[0] >= 5:
        return "That person has too many things queued."

    try:
        conn.execute("insert into tell(user_to, user_from, message, chan,"
                     "time) values(?,?,?,?,?)", (user_to, user_from, message,
                     input.chan, time.time()))
        conn.commit()
    except conn.IntegrityError:
        return "Message has already been queued."

    return "I'll pass that along."


def db_connect(bot, server):
    "check to see that our db has the tell table and return a connection."
    conn = bot.get_db_connection(server)

    conn.execute("create table if not exists tell"
                "(user_to, user_from, message, chan, time,"
                "primary key(user_to, message))")
    conn.commit()
    
    return conn
