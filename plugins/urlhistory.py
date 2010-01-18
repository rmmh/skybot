import os
import time
from datetime import datetime
import sqlite3
import pickle
from datetime import timedelta
import re

from util import hook, timesince
from util import urlnorm
#from util import texttime

url_re = re.compile(r'([a-zA-Z]+://|www\.)[^ ]*')


dbname = "skybot.db"

expiration_period = timedelta(days=1)

ignored_urls = [ urlnorm.normalize("http://google.com") ]

#TODO: Generate expiration_period_text from expiration_period
expiration_period_text = "24 hours"

def adapt_datetime(ts):
    return time.mktime(ts.timetuple())

sqlite3.register_adapter(datetime, adapt_datetime)


def insert_history(conn, url, channel, nick):
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute("insert into urlhistory(url, nick, chan, time) values(?,?,?,?)", (url, nick, channel, now))
    conn.commit()

def select_history_for_url_and_channel(conn, url, channel):
    cursor = conn.cursor()
    results = cursor.execute("select nick, time from urlhistory where url=? and chan=?", (url, channel)).fetchall()
    j = 0
    now = datetime.now()
    nicks = []
    for i in xrange(len(results)):
        reltime = datetime.fromtimestamp(results[j][1])
        if (now - reltime) > expiration_period:
            conn.execute("delete from urlhistory where url=? and chan=? and nick=? and time=?", (url, channel, results[j][0], results[j][1]))
            results.remove(results[j])
        else:
            nicks.append(results[j][0])
            j += 1
    return nicks
    
def get_nicklist(nicks):
    nicks = list(set(nicks))
    nicks.sort()
    l = len(nicks)
    if l == 0:
      return ""
    elif l == 1:
      return nicks[0]
    elif l == 2:
      return nicks[0] + " and " + nicks[1]
    else:
      result = ""
      for i in xrange(l-1):
          result += nicks[i] + ", "
      result += "and " + nicks[-1]
      return result

def dbconnect(db):
    "check to see that our db has the the seen table and return a connection."
    conn = sqlite3.connect(db)
    
    results = conn.execute("select count(*) from sqlite_master where name=?",
            ("urlhistory",)).fetchone()
    if(results[0] == 0):
        conn.execute("create table if not exists urlhistory(url text not null, nick text not null, chan text not null, time datetime not null, primary key(url, nick, chan, time));")
        conn.commit()
    return conn

def normalize_url(url):
    return urlnorm.normalize(url)
 
def get_once_twice(count):
   if count == 1:
       return "once"
   elif count == 2:
       return "twice"
   else:
       return str(count) + " times"
       
@hook.command(hook=r'(.*)', prefix=False, ignorebots=True)
def urlinput(bot, input):
    dbpath = os.path.join(bot.persist_dir, dbname)
    m = url_re.search(input.msg)
    if m:
        # URL detected
        url = normalize_url(m.group(0))
        if url not in ignored_urls:
           conn = dbconnect(dbpath)
           dupes = select_history_for_url_and_channel(conn, url, input.chan)
           num_dupes = len(dupes)
           if num_dupes > 0 and input.nick not in dupes:
               nicks = get_nicklist(dupes)
               reply = "That link has been posted " + get_once_twice(num_dupes)
               reply += " in the past " + expiration_period_text + " by " + nicks
               input.reply(reply)
           insert_history(conn, url, input.chan, input.nick)
           conn.close()

