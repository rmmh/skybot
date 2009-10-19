" tell.py: written by sklnd in July 2009"

import os
import time
from datetime import datetime
import sqlite3

from util import hook, timesince


dbname = "skybot.db"


def adapt_datetime(ts):
    return time.mktime(ts.timetuple())

sqlite3.register_adapter(datetime, adapt_datetime)


@hook.command(hook=r'(.*)', prefix=False, ignorebots=True)
def tellinput(bot, input):
    dbpath = os.path.join(bot.persist_dir, dbname)
    conn = dbconnect(dbpath)

    cursor = conn.cursor()
    command = "select count(name) from tell where name = ? and chan = ?"
    results = cursor.execute(command, (input.nick, input.chan)).fetchone()


    if results[0] > 0:
        command = "select id, user_from, quote, date from tell " \
                    "where name = ? and chan = ? limit 1"
        tell = cursor.execute(command, (input.nick, input.chan)).fetchall()[0]
        more = results[0] - 1;
        reltime = timesince.timesince(datetime.fromtimestamp(tell[3]))

        reply = "%(teller)s said %(reltime)s ago: %(quote)s" %
                {"teller": tell[1], "quote": tell[2], "reltime": reltime}
        if more:
            reply += " (+%(more)d more, to view say .showtells)" % {"more": more}

        bot.reply(reply)
        command = "delete from tell where id = ?"
        cursor.execute(command, (tell[0], ))
       
        conn.commit()
    conn.close()

@hook.command
def showtells(bot, input):
    ".showtells - View all pending tell messages (sent in PM)."
    
    dbpath = os.path.join(bot.persist_dir, dbname)
    conn = dbconnect(dbpath)

    cursor = conn.cursor()
    command = "select id, user_from, quote, date from tell " \
                "where name = ? and chan = ?"
    tells = cursor.execute(command, (input.nick, input.chan)).fetchall()
    
    if(len(tells) > 0):
        for tell in tells:
            reltime = timesince.timesince(datetime.fromtimestamp(tell[3]))
            bot.msg(input.nick, '%(teller)s said %(reltime)s ago: %(quote)s' %
                    {'teller': tell[1], 'quote': tell[2], 'reltime': reltime})
            
            command = "delete from tell where id = ?"
            cursor.execute(command, (tell[0], ))
        
        conn.commit()
    else:
         bot.msg(input.nick, "You have no pending tells.")
    
    conn.close()


@hook.command
def tell(bot, input):
    ".tell <nick> <message> - Relay <message> to <nick> the next time he talks"

    if len(input.msg) < 6:
        return tell.__doc__

    query = input.msg[6:].strip().partition(" ")

    if query[0] == input.nick:
        return "No."


    if query[2] != "":
        dbpath = os.path.join(bot.persist_dir, dbname)
        conn = dbconnect(dbpath)

        command = "select count(*) from tell_probation where name=? and chan=?"
        if conn.execute(command, (input.nick, input.chan)).fetchone()[0] > 0:
            return "No."

        command = "select count(*) from tell where name=? and user_from=?"
        if conn.execute(command, (query[0], input.nick)).fetchone()[0] >= 3:
            return "You've told that person too many things."

        cursor = conn.cursor()
        command = "insert into tell(name, user_from, quote, chan, date) " \
                    "values(?,?,?,?,?)"
        cursor.execute(command, (query[0], input.nick, query[2], input.chan,
            datetime.now()))

        conn.commit()
        conn.close()
        return "I'll pass that along."

    else:
        return tell.__doc__


def dbconnect(db):
    "check to see that our db has the the seen table and return a connection."
    conn = sqlite3.connect(db)
    results = conn.execute("select count(*) from sqlite_master where name=?",
                ("tell", )).fetchone()

    if results[0] == 0:
        conn.execute("create table if not exists tell(id integer primary key "
                     "autoincrement, name varchar(30) not null, user_from "
                     "varchar(30) not null, quote varchar(250) not null, "
                     "chan varchar(32) not null, date datetime not null);")

        conn.commit()

    results = conn.execute("select count(*) from sqlite_master where name=?",
                ("tell_probation", )).fetchone()
    if results[0] == 0:
        conn.execute("create table if not exists "+ \
                     "tell_probation(name varchar(30), chan varchar(32),"
                     "primary key(name, chan));")
        conn.commit()

    return conn
