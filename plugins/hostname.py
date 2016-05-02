#hostname.py: javaj0hn
#Hostname tracker

import re
from util import hook

def db_init(db):
   db.execute("create table if not exists nicktracker"
              "(nick, hostname, chan)")
   db.commit()

def insert(db, chan, nick, hostname_cleaned):
   db.execute("insert into nicktracker(nick, hostname, chan) "
              "values(?,?,?)", (nick, hostname_cleaned, chan))
   db.commit()

@hook.command
def hostname(inp, hostname='', db=None, input=None):
   ".hostname <hostname> -- returns nick by hostname"
   match = db.execute("select DISTINCT nick from nicktracker where "
                      "hostname=?", (inp,)).fetchall()
   if not match:
      return "No match found."
   else:
      return '%s' % (match)

@hook.command
def nick(inp, nick='', db=None, input=None):
   ".nick <nick> -- returns hostnames by nick"
   match = db.execute("select DISTINCT hostname from nicktracker where "
                     "nick=?", (inp,)).fetchall()
   if not match:
      return "No match found."
   else:
      return '%s' % (match)

@hook.command
def channel(inp, chan='', db=None, input=None):
   ".chan <hostname> -- returns which channels I have seen this hostname in"
   match = db.execute("select chan from nicktracker where "
                      "hostname=?", (inp,)).fetchall()
   if not match:
      return "No match found."
   else:
      return '%s' % (match)

@hook.event('JOIN')
def main(paraml, input=None, nick='', chan='', db=None, bot=None):
   db_init(db)
   hostname = re.search(r'@([^\ ]*)', input.prefix)
   hostname_cleaned = format(hostname.group(0))
   insert(db, chan, nick, hostname_cleaned)
