# -*- coding: utf-8 -*-

import re

from util import hook


@hook.command
def munge( input, munge_count=0 ):
    replacement_count = 0

    # First, attempt a simple replacement with a lookalike character.
    for i in xrange( len(input) ) :
        replacement = character_replacements.get( input[i] )
	if replacement:
	    output = input[:i] + replacement.decode('utf8') + input[i+1:]
            replacement_count += 1
            break

    # If that fails, attempt to replace the first vowel after first position
    # with a question mark.
    if replacement_count == 0 :
        first_vowel_match = re.match( '^..*?([aeiouAEIOU])', input )
        if first_vowel_match :
            i = first_vowel_match.start(1)
            output = input[:i] + '?' + input[i+1:]
            replacement_count += 1

    # If both options fail, blindly replace the second character with '?'.
    if replacement_count == 0 and len(input) >= 3 :
        output = input[:1] + '?' + input[2:]
        replacement_count += 1

    # If that also fails, this is just a terrible nick; no sympathy.
    if replacement_count == 0 : 
        output = input

    return output


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
    delete = re.match(r'd(?:el(?:ete)?)? (\S+) (.+)', inp)
    retrieve = re.match(r'l(?:ist)(?: (\S+))?$', inp)

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
    'e': 'ë',
    'i': 'í',
    'n': 'ñ',
    'o': 'ö',
    'u': 'ü',
    'y': 'ÿ',
    'A': 'Å',
    'C': 'Ç',
    'I': 'Í',
    'O': 'Ö'}
