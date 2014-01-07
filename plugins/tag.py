# -*- coding: utf-8 -*-

import random
import re
import threading

from util import hook


@hook.command
def munge(inp, munge_count=0):
    reps = 0
    for n in xrange(len(inp)):
        rep = character_replacements.get(inp[n])
        if rep:
            inp = inp[:n] + rep.decode('utf8') + inp[n + 1:]
            reps += 1
            if reps == munge_count:
                break
    return inp

class PaginatingWinnower(object):
    def __init__(self):
        self.lock = threading.Lock()
        self.last_input = []
        self.recent = set()

    def winnow(self, inputs, limit=400, ordered=False):
        "remove random elements from the list until it's short enough"
        with self.lock:
            # try to remove elements that were *not* removed recently
            inputs_sorted = sorted(inputs)
            if inputs_sorted == self.last_input:
                same_input = True
            else:
                same_input = False
                self.last_input = inputs_sorted
                self.recent.clear()

            combiner = lambda l: u', '.join(l)
            suffix = ''

            while len(combiner(inputs)) >= limit:
                if same_input and any(inp in self.recent for inp in inputs):
                    if ordered:
                        for inp in self.recent:
                            if inp in inputs:
                                inputs.remove(inp)
                    else:
                        inputs.remove(random.choice([inp for inp in inputs if inp in self.recent]))
                else:
                    if ordered:
                        inputs.pop()
                    else:
                        inputs.pop(random.randint(0, len(inputs) - 1))
                suffix = ' ...'

            self.recent.update(inputs)
            return combiner(inputs) + suffix

winnow = PaginatingWinnower().winnow

def add_tag(db, chan, nick, subject):
    match = db.execute('select * from tag where lower(nick)=lower(?) and'
                       ' chan=? and lower(subject)=lower(?)',
                       (nick, chan, subject)).fetchall()
    if match:
        return 'already tagged'

    db.execute('replace into tag(chan, subject, nick) values(?,?,?)',
               (chan, subject, nick))
    db.commit()

    return 'tag added'


def delete_tag(db, chan, nick, del_tag):
    count = db.execute('delete from tag where lower(nick)=lower(?) and'
                       ' chan=? and lower(subject)=lower(?)',
                       (nick, chan, del_tag)).rowcount
    db.commit()

    if count:
        return 'deleted'
    else:
        return 'tag not found'


def get_tag_counts_by_chan(db, chan):
    tags = db.execute("select subject, count(*) from tag where chan=?"
                      " group by lower(subject)"
                      " order by lower(subject)", (chan,)).fetchall()

    tags.sort(key=lambda x: x[1], reverse=True)
    if not tags:
        return 'no tags in %s' % chan
    ret = '%s tags: ' % chan
    return winnow(['%s (%d)' % row for row in tags], ordered=True)


def get_tags_by_nick(db, chan, nick):
    tags = db.execute("select subject from tag where lower(nick)=lower(?)"
                      " and chan=?"
                      " order by lower(subject)", (nick, chan)).fetchall()
    if tags:
        return 'tags for "%s": ' % munge(nick, 1) + winnow([
                tag[0] for tag in tags])
    else:
        return ''


def get_nicks_by_tagset(db, chan, tagset):
    nicks = None
    for tag in tagset.split('&'):
        tag = tag.strip()

        current_nicks = db.execute("select nick from tag where " +
                                   "lower(subject)=lower(?)"
                                   " and chan=?", (tag, chan)).fetchall()

        if not current_nicks:
            return "tag '%s' not found" % tag

        if nicks is None:
            nicks = set(current_nicks)
        else:
            nicks.intersection_update(current_nicks)

    nicks = [munge(x[0], 1) for x in sorted(nicks)]
    if not nicks:
        return 'no tags found in intersection of "%s"' % tagset
    return 'nicks tagged "%s": ' % tagset + winnow(nicks)


@hook.command
def tag(inp, chan='', db=None):
    '.tag [add|del] <nick> <tag> -- marks/unmarks <nick> as <tag> {related: .tags, .tagged}'

    db.execute('create table if not exists tag(chan, subject, nick)')

    add = re.match(r'(?:a(?:dd)? )?(\S+) (.+)', inp)
    delete = re.match(r'd(?:el(?:ete)?)? (\S+) (.+)\s*$', inp)

    if delete:
        nick, del_tag = delete.groups()
        return delete_tag(db, chan, nick, del_tag)
    if add:
        nick, subject = add.groups()
        return add_tag(db, chan, nick, subject)
    else:
        tags = get_tags_by_nick(db, chan, inp)
        if tags:
            return tags
        else:
            return tag.__doc__

@hook.command
def tags(inp, chan='', db=None):
    '.tags <nick>/list -- get list of tags for <nick>, or a list of tags {related: .tag, .tagged}'
    if inp == 'list':
        return get_tag_counts_by_chan(db, chan)

    tags = get_tags_by_nick(db, chan, inp)
    if tags:
        return tags
    else:
        return get_nicks_by_tagset(db, chan, inp)


@hook.command
def tagged(inp, chan='', db=None):
    '.tagged <tag> [& tag...] -- get nicks marked as <tag> (separate multiple tags with &) {related: .tag, .tags}'

    return get_nicks_by_tagset(db, chan, inp)


character_replacements = {
    'a': 'ä',
#    'b': 'Б',
    'c': 'ċ',
    'd': 'đ',
    'e': 'ë',
    'f': 'ƒ',
    'g': 'ġ',
    'h': 'ħ',
    'i': 'í',
    'j': 'ĵ',
    'k': 'ķ',
    'l': 'ĺ',
#    'm': 'ṁ',
    'n': 'ñ',
    'o': 'ö',
    'p': 'ρ',
#    'q': 'ʠ',
    'r': 'ŗ',
    's': 'š',
    't': 'ţ',
    'u': 'ü',
#    'v': '',
    'w': 'ω',
    'x': 'χ',
    'y': 'ÿ',
    'z': 'ź',
    'A': 'Å',
    'B': 'Β',
    'C': 'Ç',
    'D': 'Ď',
    'E': 'Ē',
#    'F': 'Ḟ',
    'G': 'Ġ',
    'H': 'Ħ',
    'I': 'Í',
    'J': 'Ĵ',
    'K': 'Ķ',
    'L': 'Ĺ',
    'M': 'Μ',
    'N': 'Ν',
    'O': 'Ö',
    'P': 'Р',
#    'Q': 'Ｑ',
    'R': 'Ŗ',
    'S': 'Š',
    'T': 'Ţ',
    'U': 'Ů',
#    'V': 'Ṿ',
    'W': 'Ŵ',
    'X': 'Χ',
    'Y': 'Ỳ',
    'Z': 'Ż'}
