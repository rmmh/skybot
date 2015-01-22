"""
remember.py: written by Scaevolus 2010
"""

import re
import string
import unittest

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
        if _tail == '':
            return "I don't know about that."
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


class MemoryTest(unittest.TestCase):
    def setUp(self):
        import sqlite3
        self.db = sqlite3.connect(':memory:')

    def remember(self, inp, nick='someone', chan='#test'):
        return remember(inp, nick=nick, chan=chan, db=self.db)

    def forget(self, inp, chan='#test'):
        return forget(inp, chan=chan, db=self.db)

    def question(self, inp, chan='#test'):
        output = []
        question(re.match(r'(.*)', inp),
                 chan=chan, say=output.append, db=self.db)
        return output[0] if output else None

    def test_remember(self):
        assert 'done.' == self.remember('dogs :3')
        assert 'dogs :3' == self.question('dogs')

    def test_remember_doc(self):
        assert '.remember <word>' in self.remember('bad_syntax')

    def test_remember_overwrite(self):
        self.remember('dogs :(')
        assert 'forgetting "dogs :("' in self.remember('dogs :3')
        assert 'dogs :3' == self.question('dogs')

    def test_remember_hygiene(self):
        self.remember('python good', chan='#python')
        self.remember('python bad', chan='#ruby')
        assert 'python good' == self.question('python', '#python')
        assert 'python bad' == self.question('python', '#ruby')

    def test_remember_append(self):
        self.remember('ball big')
        self.remember('ball +red')
        assert 'ball big red' == self.question('ball')

    def test_remember_append_punctuation(self):
        self.remember('baby young')
        self.remember('baby +, hungry')
        assert 'baby young, hungry' == self.question('baby')

    def test_remember_replace(self):
        self.remember('person is very rich (rich!)')
        self.remember('person s/rich/poor/')
        assert 'person is very poor (rich!)' == self.question('person')

    def test_remember_replace_invalid(self):
        self.remember('fact bar')
        assert 'invalid replacement' in self.remember('fact s/too/many/seps/!')
        assert 'invalid replacement' in self.remember('fact s/toofew')

    def test_remember_replace_ineffective(self):
        self.remember('hay stack')
        assert 'unchanged' in self.remember('hay s:needle:shiny needle')

    def test_remember_replace_missing(self):
        assert "I don't know about that" in self.remember('hay s/what/lol')

    def test_question_empty(self):
        assert self.question('not_in_db') is None

    def test_forget(self):
        self.remember('meat good', chan='#carnivore')
        self.remember('meat bad', chan='#vegan')
        assert 'forgot `meat good`' in self.forget('meat', chan='#carnivore')
        assert 'meat bad' == self.question('meat', chan='#vegan')

    def test_forget_missing(self):
        assert "don't know" in self.forget('fakekey')
