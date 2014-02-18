"""
remember.py: written by Scaevolus 2010
"""

import string
import re

from util import hook


def db_init(db):
    db.execute("create table if not exists memory(chan, word, data, nick,"
               " primary key(chan, word))")
    db.commit()


def get_memory(db, chan, word):
    row = db.execute("select data from memory where chan=? and word=lower(?)",
                     (chan, word)).fetchone()
    if row:
        return row[0]
    else:
        return None


@hook.command
@hook.command("r")
def remember(inp, nick='', chan='', db=None):
    ".remember <word> [+]<data> s/<before>/<after> -- maps word to data in the memory, or "
    " does a string replacement (not regex)"
    db_init(db)

    append = False
    replacement = False

    try:
        head, tail = inp.split(None, 1)
    except ValueError:
        return remember.__doc__

    data = get_memory(db, chan, head)
    if data is not None:
        _head, _tail = data.split(None, 1)
    else:
        _head, _tail = head, ''

    if tail[0] == '+':
        append = True
        # ignore + symbol
        new = tail[1:]
        # data is stored with the input so ignore it when re-adding it
        if len(tail) > 1 and tail[1] in (string.punctuation + ' '):
            tail = _tail + new
        else:
            tail = _tail + ' ' + new

    if len(tail) > 2 and tail[0] == 's' and tail[1] in string.punctuation:
        args = tail.split(tail[1])
        if len(args) == 4 and args[3] == '':
            args = args[:-1]
        if len(args) == 3:
            replacement = True
            _, src, dst = args
            new_data = _tail.replace(src, dst, 1)
            if new_data == _tail:
                return 'replacement left data unchanged'
            tail = new_data
        else:
            return 'invalid replacement syntax -- try s$foo$bar instead?'

    db.execute("replace into memory(chan, word, data, nick) values"
               " (?,lower(?),?,?)", (chan, head, head + ' ' + tail, nick))
    db.commit()

    if data:
        if append:
            return "appending %s to %s" % (new, data.replace('"', "''"))
        elif replacement:
            return "replacing '%s' with '%s' in %s" % (src, dst, _tail)
        else:
            return 'forgetting "%s", remembering this instead.' % \
                data.replace('"', "''")
    else:
        return 'done.'


@hook.command
@hook.command("f")
def forget(inp, chan='', db=None):
    ".forget <word> -- forgets the mapping that word had"

    db_init(db)
    data = get_memory(db, chan, inp)

    if not chan.startswith('#'):
        return "I won't forget anything in private."

    if data:
        db.execute("delete from memory where chan=? and word=lower(?)",
                   (chan, inp))
        db.commit()
        return 'forgot `%s`' % data.replace('`', "'")
    else:
        return "I don't know about that."


@hook.regex(r'^\? ?(.+)')
def question(inp, chan='', say=None, db=None):
    "?<word> -- shows what data is associated with word"
    db_init(db)

    data = get_memory(db, chan, inp.group(1).strip())
    if data:
        say(data)
