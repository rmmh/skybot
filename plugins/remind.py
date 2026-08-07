from util import hook, timesince
import time
import re
import _thread
import sqlite3
import os

# In seconds
conversions = {
    'y': 31536000,
    'M': 2628003,
    'd': 86400,
    'h': 3600,
    'm': 60,
    's': 1
}

# When a reminder timer is below `threading_threshold`, it will spawn a thread
# Reminders are updated on any PRIVMSG event
# so it is recommended that `threading_threshold` ~= max(time between activity)
threading_threshold = 5*conversions['m']    # In seconds
maximum_duration = 5*conversions['y']       # The maximum length for a reminder
maximum_reminders = 10                      # Maximum amount of reminders per channel-user


def db_init(db):
    db.execute('create table if not exists reminders(nick, chan, reminder, expire_time, creation_time, active_thread, '
               'primary key(nick, chan, creation_time))')
    db.commit()


def insert_reminder(db, nick, chan, reminder, expire_time, creation_time, active_thread):
    db.execute('insert into reminders(nick, chan, reminder, expire_time, creation_time, active_thread) '
               'values(?, ?, ?, ?, ?, ?)',
               (nick, chan, reminder, expire_time, creation_time, int(active_thread)))
    db.commit()


def del_reminder(db, nick, chan, reminder):
    count = db.execute('delete from reminders where nick=? and chan=? and reminder=?',
               (nick, chan, reminder)).rowcount
    db.commit()
    return count


def get_reminders(db, nick):
    return db.execute('select reminder, expire_time from reminders '
                      'where nick=?',
                      (nick,)).fetchall()


def input_in_seconds(time_string):
    """
    :param time_string will be a string in the form of 1y2M3d4h5m6s in any order
    """
    reg = re.compile('([\d]+)([yMdhms])')
    time_tuples = reg.findall(time_string)
    wait_time = 0
    for time_value, time_unit in time_tuples:
        conversion_value = conversions.get(time_unit, None)
        if conversion_value is None:
            return remindme.__doc__
        wait_time += int(time_value)*conversion_value
    return wait_time


def reminder_thread(nick, chan, reminder, wait_time, creation_time, conn, bot):
    if float(wait_time) >= 1:
        # Handle the case where a reminder didn't spawn a thread before expiring
        time.sleep(float(wait_time))

    elapsed_time = int(time.time() - creation_time)
    remainder_seconds = elapsed_time % 60
    if elapsed_time < 60:
        creation_time_output = str(elapsed_time) + ' seconds'
    else:
        creation_time_output = timesince.timesince(creation_time)
        if remainder_seconds:
            # Prevent '1 minute & 0 seconds'
            creation_time_output += ' & ' + str(remainder_seconds) + ' seconds'

    conn.msg(chan, nick + ': ' + 'You set a reminder ' + str(creation_time_output) + ' ago: ' + reminder)

    # Cheat real bad and just reimplement core/db.get_db_connection
    filename = os.path.join(bot.persist_dir, '%s.%s.db' % (conn.nick, conn.server_host))
    db = sqlite3.connect(filename, timeout=10)
    db.execute('delete from reminders where nick=? and chan=? and creation_time=?',
               (nick, chan, creation_time))
    db.commit()


@hook.singlethread
@hook.event('PRIVMSG')
def update_reminders(paraml, input=None, db=None, bot=None):
    """
    Every time a privmsg happens:
        - Update reminders expire_time
        - Spawn threads that will
    (Consider some throttling here)
    For any such reminder, spawn a new thread and set active_thread in db

    Stale db entries can happen if the system crashes before reminder threads complete
    Check for:
        - # of active threads is 0 (singleton)
        - # of active threads !- num of returned rows for active_thread = True
        - active_thread = True and (expire_time - now) < 0
        - active_thread = False and (expire_time - now) < 0
    """
    db_init(db)

    # Experimental single query with clean-up
    all_reminders = db.execute('select nick, chan, reminder, expire_time, creation_time, active_thread '
                               'from reminders').fetchall()

    for reminder in all_reminders:
        nick = reminder[0]
        chan = reminder[1]
        reminder_text = reminder[2]
        expire_time = float(reminder[3])
        creation_time = float(reminder[4])
        active_thread = reminder[5]

        wait_time = expire_time - time.time()

        if active_thread:
            # Any active threads with negative wait_time are stale: clean up
            if wait_time < 0:
                _thread.start_new_thread(reminder_thread,
                                        (nick, chan, reminder_text, wait_time, creation_time, input.conn, bot))
                db.execute('delete from reminders where nick=? and chan=? and creation_time=?',
                           (nick, chan, creation_time))
        else:
            # If any reminders without active threads are below the threading_threshold: spawn a thread
            # This handles wait_time < 0, i.e. a thread wasn't spawned and the reminder expired
            if wait_time < threading_threshold:
                _thread.start_new_thread(reminder_thread,
                                        (nick, chan, reminder_text, wait_time, creation_time, input.conn, bot))
                db.execute('update reminders set active_thread = 1 where '
                           'nick=? and chan=? and creation_time=?',
                           (nick, chan, creation_time))

    db.commit()


@hook.singlethread
@hook.command
@hook.command('remind')
def remindme(inp, nick='', chan='', db=None, conn=None, bot=None):
    """.remindme 1y9M7d5h3m1s <reminder text> will set a reminder for 1 year 9 months 7 days 5 hours 3 minutes 1 second.
    It's just like youtube timestamps. |
    .remindme list to see active reminders | .remindme del <reminder_text> to delete reminders (can delete multiple)"""
    db_init(db)
    query = inp.split(' ', 1)

    if query[0] == 'list':
        reminders = get_reminders(db, nick)
        for reminder in reminders:
            output = 'Reminder for \"' + reminder[0] + '\" expires on ' + time.ctime(reminder[1])
            conn.msg(nick, output)
        if not len(reminders):
            return 'No active reminders!'
        return

    if query[0] == 'del':
        reminder_text = query[1]
        deleted_rows = del_reminder(db, nick, chan, reminder_text)
        return "Deleted " + str(deleted_rows) + " reminders."

    if len(query) < 2:
        return remindme.__doc__

    time_input = query[0]
    reminder = query[1].strip()

    if not any((c in ['y', 'M', 'd', 'h', 'm', 's']) for c in str(time_input)) \
            or not any(char.isdigit() for char in str(time_input)):
        return remindme.__doc__

    wait_time = input_in_seconds(time_input)
    if wait_time > maximum_duration:
        return 'Your reminder can\'t be longer than ' + str(maximum_duration) + ' seconds'

    rows = len(db.execute('select creation_time from reminders where '
                          'nick=?', (nick,)).fetchall())

    if rows == maximum_reminders:
        return 'You can have at most ' + str(maximum_reminders) + ' reminders.'

    expire_time = time.time() + wait_time
    creation_time = time.time()

    if wait_time < threading_threshold:
        insert_reminder(db, nick, chan, reminder, expire_time, creation_time, True)
        _thread.start_new_thread(reminder_thread, (nick, chan, reminder, wait_time, creation_time, conn, bot))
    else:
        insert_reminder(db, nick, chan, reminder, expire_time, creation_time, False)

    confirmation = 'Reminder set for ' + time.ctime(expire_time) + ': ' + reminder
    return confirmation

