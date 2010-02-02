import time
import re

from util import hook, urlnorm

url_re = re.compile(r'([a-zA-Z]+://|www\.)[^ ]*')

expiration_period = 60 * 60 * 24 # 1 day
expiration_period_text = "24 hours"

ignored_urls = [urlnorm.normalize("http://google.com")]

def db_connect(bot, server):
    "check to see that our db has the the seen table and return a dbection."
    db = bot.get_db_connection(server)
    db.execute("create table if not exists urlhistory"
                 "(chan, url, nick, time)")
    db.commit()
    return db

def insert_history(db, chan, url, nick):
    now = time.time()
    db.execute("insert into urlhistory(chan, url, nick, time) "
                 "values(?,?,?,?)", (chan, url, nick, time.time()))
    db.commit()

def get_history(db, chan, url):
    db.execute("delete from urlhistory where time < ?", 
                 (time.time() - expiration_period,))
    nicks = db.execute("select nick from urlhistory where "
            "chan=? and url=?", (chan, url)).fetchall()
    return [x[0] for x in nicks]
    
def get_nicklist(nicks):
    nicks = sorted(set(nicks), key=unicode.lower)
    if len(nicks) <= 2:
        return ' and '.join(nicks)
    else:
        return ', and '.join((', '.join(nicks[:-1]), nicks[-1]))

def ordinal(count):
    return ["once", "twice", "%d times" % count][min(count, 3) - 1]
       
@hook.command(hook=r'(.*)', prefix=False)
def urlinput(inp, nick='', chan='', server='', reply=None, bot=None):
    m = url_re.search(inp.encode('utf8'))
    if not m:
        return

    # URL detected
    db = db_connect(bot, server)
    try:
        url = urlnorm.normalize(m.group(0))
        if url not in ignored_urls:
            dupes = get_history(db, chan, url)
            insert_history(db, chan, url, nick)
            if dupes and nick not in dupes:
                reply("That link has been posted " + ordinal(len(dupes))
                    + " in the past " + expiration_period_text + " by " +
                    get_nicklist(dupes))
    finally:
        db.commit()
        db.close()
