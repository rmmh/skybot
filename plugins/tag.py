# -*- coding: utf-8 -*-

import re

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
    ret += ', '.join('%s (%d)' % row for row in tags)
    if len(ret) > 400:
        ret = ret[:ret.rfind(' ', 0, 400)] + '...'
    return ret


def get_tags_by_nick(db, chan, nick):
    return db.execute("select subject from tag where lower(nick)=lower(?)"
                      " and chan=?"
                      " order by lower(subject)", (nick, chan)).fetchall()


def get_nicks_by_tag(db, chan, subject):
    nicks = db.execute("select nick from tag where lower(subject)=lower(?)"
                       " and chan=?"
                       " order by lower(nick)", (subject, chan)).fetchall()

    nicks = [munge(x[0], 1) for x in nicks]
    if not nicks:
        return 'tag not found'
    return 'nicks tagged "%s": ' % subject + ', '.join(nicks)


@hook.command
def tag(inp, chan='', db=None):
    '.tag <nick>/[add|del] <nick> <tag>/list [tag] -- get list of tags on ' \
    '<nick>/(un)marks <nick> as <tag>/gets list of tags/nicks marked as [tag]'

    db.execute('create table if not exists tag(chan, subject, nick)')

    add = re.match(r'(?:a(?:dd)? )?(\S+) (.+)', inp)
    delete = re.match(r'd(?:el(?:ete)?)? (\S+) (.+)\s*$', inp)
    retrieve = re.match(r'l(?:ist)(?: (.+))?\s*$', inp)

    if retrieve:
        search_tag = retrieve.group(1)
        if search_tag:
            return get_nicks_by_tag(db, chan, search_tag)
        else:
            return get_tag_counts_by_chan(db, chan)
    if delete:
        nick, del_tag = delete.groups()
        return delete_tag(db, chan, nick, del_tag)
    if add:
        nick, subject = add.groups()
        return add_tag(db, chan, nick, subject)
    else:
        tags = get_tags_by_nick(db, chan, inp)

        if not tags:
            return get_nicks_by_tag(db, chan, inp)
        else:
            return 'tags for "%s": ' % munge(inp, 1) + ', '.join(
                tag[0] for tag in tags)


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
