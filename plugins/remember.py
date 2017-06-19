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


def get_page(data, start_idx, min_page_len, max_page_len):
    """
    slices the data string, starting at start_idx, into a chunk no longer
    than max_page_len. The slice will occur at a comma if the resulting
    string would not be shorter than min_page_len.
    returns a tuple of (result str, slice index)
    """
    page_data = data[start_idx:start_idx + max_page_len]

    if len(page_data) < max_page_len:
        return page_data, len(page_data) + start_idx

    last_comma_idx = page_data.rfind(',')

    if last_comma_idx < min_page_len:
        ret = data[start_idx:max_page_len + start_idx]
        return ret, len(ret) + start_idx

    end_idx = last_comma_idx + start_idx
    return data[start_idx:end_idx], end_idx


def get_pages(data, min_page_len, max_page_len):
    "slices the data string into pages using get_page, returning a list"
    result = []

    page_data, last_idx = get_page(data, 0, min_page_len, max_page_len)
    while page_data:
        result.append(page_data)
        page_data, last_idx = get_page(data, last_idx, min_page_len, max_page_len)

    return result

more_pages_message = ' (%s page(s) left)'
page_missing_message = "%s only has %s page(s)"
message_len_limit = 512 - len(more_pages_message) - 75 # fudge factor for protocol overhead

@hook.regex(r'^\? ?(\S+) ?(\d+)?')
def question(inp, chan='', say=None, db=None):
    "?<word> [page] -- shows what data is associated with word, paginated by page (default 1)"
    db_init(db)

    min_page_len = 100

    word = inp.group(1).strip()
    page = int(inp.group(2) or 1)

    if page is None:
        page = 1

    data = get_memory(db, chan, word)
    if data:
        pages = get_pages(data, min_page_len, message_len_limit)
        page_idx = page - 1 # 1-indexed
        try:
            page_data = pages[page_idx]
        except IndexError:
            say(page_missing_message % (word, len(pages)))
            return

        page_data = page_data.lstrip(', ')

        last_page = len(pages) - 1
        if page_idx == last_page:
            say(page_data)
            return

        pages_left = last_page - page_idx
        say(page_data + (more_pages_message % int(pages_left)))


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
        question(re.match(r'(\S+) ?(\d+)?', inp),
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

    def test_get_page(self):
        assert get_page('123456789', 0, 5, 8) == ('12345678', 8) # max length
        assert get_page('123,456789', 0, 5, 8) == ('123,4567', 8) # min length not satisfied
        assert get_page('123,45,67,89', 0, 5, 8) == ('123,45', 6) # chooses correct comma
        assert get_page('', 0, 5, 8) == ('', 0) # correct empty result
        # start offsets
        assert get_page('123456789', 1, 5, 9) == ('23456789', 9)
        assert get_page('123456789', 1, 5, 8) == ('23456789', 9)
        assert get_page('1234567,89', 1, 5, 8) == ('234567', 7)
        assert get_page('', 1, 5, 8) == ('', 1)

    def test_get_pages(self):
        assert get_pages('123456789', 5, 8) == ['12345678', '9']
        assert get_pages('123,456789', 5, 8) == ['123,4567', '89']
        assert get_pages('123,45,67,89', 5, 8) == ['123,45', ',67,89']
        assert get_pages('', 5, 8) == []

    def test_paging_message(self):
        long_string = 'long ' + 'a' * 1000

        self.remember(long_string, chan='#long')
        assert more_pages_message % 2 in self.question('long', chan='#long') # "2 pages left"
        assert more_pages_message % 1 in self.question('long 2', chan='#long')
        assert not re.match(r'\d', self.question('long 3', chan='#long'))

    def test_paging_result(self):
        long_string = 'long ' + 'x' * message_len_limit + 'y' * message_len_limit

        self.remember(long_string, chan='#long')
        p1_data = self.question('long', chan='#long')
        p2_data = self.question('long 2', chan='#long')
        p3_data = self.question('long 3', chan='#long')

        all_data = p1_data + p2_data + p3_data

        # no data lost
        assert all_data.count('x') == message_len_limit
        assert all_data.count('y') == message_len_limit

    def test_missing_page(self):
        long_string = 'long ' + 'a' * 1000

        self.remember('long ' + long_string)
        self.remember('thing foo')

        assert page_missing_message % ('thing', 1) in self.question('thing 2')
        assert page_missing_message % ('long', 3) in self.question('long 11')

    def test_strip_leading_comma(self):
        long_string = 'long ' + 'x' * (message_len_limit - 10) + ', ' + 'y' * (message_len_limit - 10)
        self.remember(long_string)
        assert ', ' not in self.question('long 2')

    def test_regressions(self):
        # improper split on last comma even though full message is < length limit
        gmg = 'gmg good morning goons, goodly morning goons, gob morning goons, good moring Gobiner, good morning gobs, goom morgan goobs'
        self.remember(gmg)
        assert self.question(gmg) == gmg

if __name__ == '__main__':
    unittest.main()
