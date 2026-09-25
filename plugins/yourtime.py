"""yourtime.py: written by Lord_DeathMatch in October 2012
       based on tell by sklnd and Scaevolus"""

import re
from datetime import timedelta, datetime, tzinfo

from util import hook


class GMT(tzinfo):
    def __init__(self, difference):
        self.difference = difference

    def utcoffset(self, dt):
        return timedelta(hours=self.difference) + self.dst(dt)

    def dst(self, dt):
        return timedelta(0)


def db_init(db):
    "check to see that our db has the yourtime table and return a db section."
    db.execute("create table if not exists yourtime"
                "(username, timezone,"
                "primary key(username))")
    db.commit()
    return db


@hook.command(autohelp=False)
def yourtime(inp, nick='', chan='', notice=None, db=None):
    ".yourtime -- determine current time in nick's location."

    db_init(db)

    query = inp.split(' ', 1)
    if len(query) != 1:
        return yourtime.__doc__

    timezone = db.execute(
        "select timezone from yourtime where username=lower(?)",
        (query[0],)).fetchall()

    if not timezone:
        return '"%s" has not set their timezone' % (query[0])
    else:
        return "For %s it is %s" % (query[0], datetime.now(GMT(timezone[0][0])).ctime())


@hook.command('setzone')
@hook.command('myzone')
def myzone(inp, nick='', chan='', db=None, notice=None):
    ".myzone <timezone> -- set your recorded timezone"

    db_init(db)

    query = inp.split(' ', 1)

    if len(query) != 1:
        return myzone.__doc__

    match = re.match(r'GMT(?P<timezone>.*)', query[0], re.IGNORECASE)
    if match:
        print 'timezone;', match.groupdict()['timezone']
        timezone = float(match.groupdict()['timezone'])
    else:
        notice("Unrecognized format. Please enter your timezone in GMT+* format.")
        return

    nick = nick.lower()
    try:
        db.execute("insert into yourtime(username, timezone) values(?,?)", (nick, timezone))
        db.commit()
    except db.IntegrityError:
        db.execute("update yourtime set timezone=(?) where username=lower(?)", (timezone, nick))
        db.commit()

    if timezone >= 0:
        human_readable = 'GMT+' + str(timezone)
    else:
        human_readable = 'GMT-' + str(timezone)
    notice("Timezone stored as %s" % human_readable)
