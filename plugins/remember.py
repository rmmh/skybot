"""
remember.py: written by Scaevolus 2010
"""

from util import hook
from string import lstrip
import re

multi_word_regex='(".*")(.*)'

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
def remember(inp, nick='', chan='', db=None):
    ".remember <word> <data> -- maps word to data in the memory"
    db_init(db)

    re_match = re.match(multi_word_regex,inp)
    if re_match:
        try:
            head = re_match.group(1)
            tail = re_match.group(2)
            tail = lstrip(tail)
        except:
            return remember.__doc__
    else:
        try:
            head, tail = inp.split(None, 1)
        except ValueError:
            return remember.__doc__


    data = get_memory(db, chan, head)
    db.execute("replace into memory(chan, word, data, nick) values"
               " (?,lower(?),?,?)", (chan, head, head + ' ' + tail, nick))
    db.commit()
    if data:
        return 'forgetting "%s", remembering this instead.' % \
                data.replace('"', "''")
    else:
        return 'done.'


@hook.command
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
