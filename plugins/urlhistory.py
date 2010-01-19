import os
import time
import sqlite3
import pickle
import re

from util import hook, urlnorm

url_re = re.compile(r'([a-zA-Z]+://|www\.)[^ ]*')

dbname = "skybot.db"

expiration_period = 60 * 60 * 24 # 1 day
expiration_period_text = "24 hours"

ignored_urls = [urlnorm.normalize("http://google.com")]

def dbconnect(db):
    "check to see that our db has the the seen table and return a connection."
    conn = sqlite3.connect(db)
    conn.execute("create table if not exists urlhistory"
                 "(server, chan, url, nick, time)")
    conn.commit()
    return conn

def insert_history(conn, server, chan, url, nick):
    now = time.time()
    conn.execute("insert into urlhistory(server, chan, url, nick, time) "
                 "values(?,?,?,?,?)", (server, chan, url, nick, time.time()))
    conn.commit()

def get_history(conn, server, chan, url):
    conn.execute("delete from urlhistory where time < ?", 
                 (time.time() - expiration_period,))
    nicks = conn.execute("select nick from urlhistory where server=? "
            "and chan=? and url=?", (server, chan, url)).fetchall()
    return [x[0] for x in nicks]
    
def get_nicklist(nicks):
    nicks = sorted(set(nicks))
    if len(nicks) <= 2:
        return ' and '.join(nicks)
    else:
        return ', and '.join((', '.join(nicks[:-1]), nicks[-1]))

def ordinal(count):
    return ["once", "twice", "%d times" % count][min(count, 3) - 1]
       
@hook.command(hook=r'(.*)', prefix=False)
def urlinput(bot, input):
    dbpath = os.path.join(bot.persist_dir, dbname)
    m = url_re.search(input.msg.encode('utf8'))
    if not m:
        return

    # URL detected
    conn = dbconnect(dbpath)
    try:
        url = urlnorm.normalize(m.group(0))
        if url not in ignored_urls:
            dupes = get_history(conn, input.server, input.chan, url)
            insert_history(conn, input.server, input.chan, url, input.nick)
            if dupes and input.nick not in dupes:
                input.reply("That link has been posted " + ordinal(len(dupes))
                    + " in the past " + expiration_period_text + " by " +
                    get_nicklist(dupes))
    finally:
        conn.commit()
        conn.close()
