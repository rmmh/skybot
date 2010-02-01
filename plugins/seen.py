" seen.py: written by sklnd in about two beers July 2009"

import time

from util import hook, timesince


@hook.tee
def seeninput(bot, input):
    if input.command != 'PRIVMSG':
        return

    conn = db_connect(bot, input.server)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO seen(name, date, quote, chan)"
        "values(?,?,?,?)", (input.nick.lower(), time.time(),
        input.msg, input.chan))
    conn.commit()


@hook.command
def seen(bot, input):
    ".seen <nick> -- Tell when a nickname was last in active in irc"

    if len(input.msg) < 6:
        return seen.__doc__

    query = input.inp

    if query.lower() == input.nick.lower():
        return "Have you looked in a mirror lately?"

    conn = db_connect(bot, input.server)
    cursor = conn.cursor()

    command = "SELECT date, quote FROM seen WHERE name LIKE ? AND chan = ?" \
              "ORDER BY date DESC"
    cursor.execute(command, (query, input.chan))
    results = cursor.fetchone()

    if results:
        reltime = timesince.timesince(results[0])
        return '%s was last seen %s ago saying: %s' % \
                    (query, reltime, results[1])
    else:
        return "I've never seen %s" % query


def db_connect(bot, server):
    "check to see that our db has the the seen table and return a connection."
    conn = bot.get_db_connection(server)
    
    conn.execute("CREATE TABLE IF NOT EXISTS "
                 "seen(name varchar(30) not null, date datetime not null, "
                 "quote varchar(250) not null, chan varchar(32) not null, "
                 "primary key(name, chan));")
    conn.commit()

    return conn
