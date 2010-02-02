"""
remember.py: written by Scaevolus 2010
"""

from util import hook

def db_init(db):
    db.execute("create table if not exists memory(chan, word, data, nick,"
               " primary key(chan, word))")
    db.commit()

def get_memory(db, chan, word):
    row = db.execute("select data from memory where chan=? and word=lower(?)",
                      (chan, word)).fetchone()
    if row:
        return row[0].encode('utf8')
    else:
        return None

@hook.command
def remember(inp, nick='', chan='', db=None):
    ".remember <word> <data> -- maps word to data in the memory"
    db_init(db)

    try:
        head, tail = inp.split(None, 1)
    except ValueError:
        return remember.__doc__

    data = get_memory(db, chan, head)
    db.execute("replace into memory(chan, word, data, nick) values"
               " (?,lower(?),?,?)", (chan, head, head + ' ' + tail, nick))
    db.commit()
    if data:
        return 'forgetting that %r, remembering this instead.' % data
    else:
        return 'done.'

@hook.command
def forget(inp, chan='', db=None):
    ".forget <word> -- forgets the mapping that word had"
    if not inp:
        return forget.__doc__

    db_init(db)
    data = get_memory(db, chan, inp)

    if not chan.startswith('#'):
        return "I won't forget anything in private."

    if data:
        db.execute("delete from memory where chan=? and word=lower(?)",
                   (chan, inp))
        db.commit()
        return 'forgot that %r' % data
    else:
        return "I don't know about that."

@hook.command(hook='\?(.+)', prefix=False)
def question(inp, chan='', say=None, db=None):
    "?<word> -- shows what data is associated with word"
    db_init(db)

    data = get_memory(db, chan, inp)
    if data:
        say(data)
