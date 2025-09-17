# -*- coding: utf-8 -*-
from builtins import range, object
from past.utils import old_div
import math
import random
import re
import threading

from util import hook


def sanitize(s):
    return re.sub(r"[\x00-\x1f]", "", s)


@hook.command
def munge(inp, munge_count=0):
    reps = 0
    for n in range(len(inp)):
        rep = character_replacements.get(inp[n])
        if rep:
            inp = inp[:n] + rep + inp[n + 1 :]
            reps += 1
            if reps == munge_count:
                break
    return inp


class PaginatingWinnower(object):
    def __init__(self):
        self.lock = threading.Lock()
        self.inputs = {}

    def winnow(self, inputs, limit=400, ordered=False):
        "remove random elements from the list until it's short enough"
        with self.lock:
            combiner = lambda l: ", ".join(sorted(l))

            # try to remove elements that were *not* removed recently
            inputs_sorted = combiner(inputs)
            if inputs_sorted in self.inputs:
                same_input = True
                recent = self.inputs[inputs_sorted]
                if len(recent) == len(inputs):
                    recent.clear()
            else:
                same_input = False
                if len(self.inputs) >= 100:
                    # a true lru is effort, random replacement is easy
                    self.inputs.pop(random.choice(list(self.inputs)))
                recent = set()
                self.inputs[inputs_sorted] = recent

            suffix = ""

            while len(combiner(inputs)) >= limit:
                if same_input and any(inp in recent for inp in inputs):
                    if ordered:
                        for inp in recent:
                            if inp in inputs:
                                inputs.remove(inp)
                    else:
                        inputs.remove(
                            random.choice([inp for inp in inputs if inp in recent])
                        )
                else:
                    if ordered:
                        inputs.pop()
                    else:
                        inputs.pop(random.randint(0, len(inputs) - 1))
                suffix = " ..."

            recent.update(inputs)
            return combiner(inputs) + suffix


winnow = PaginatingWinnower().winnow


def add_tag(db, chan, nick, subject):
    match = db.execute(
        "select * from tag where lower(nick)=lower(?) and"
        " chan=? and lower(subject)=lower(?)",
        (nick, chan, subject),
    ).fetchall()
    if match:
        return "already tagged"

    db.execute(
        "replace into tag(chan, subject, nick) values(?,?,?)", (chan, subject, nick)
    )
    db.commit()

    return "tag added"


def delete_tag(db, chan, nick, del_tag):
    count = db.execute(
        "delete from tag where lower(nick)=lower(?) and"
        " chan=? and lower(subject)=lower(?)",
        (nick, chan, del_tag),
    ).rowcount
    db.commit()

    if count:
        return "deleted"
    else:
        return "tag not found"


def get_tag_counts_by_chan(db, chan):
    tags = db.execute(
        "select subject, count(*) from tag where chan=?"
        " group by lower(subject)"
        " order by lower(subject)",
        (chan,),
    ).fetchall()

    tags.sort(key=lambda x: x[1], reverse=True)
    if not tags:
        return "no tags in %s" % chan
    return winnow(["%s (%d)" % row for row in tags], ordered=True)


def get_tags_by_nick(db, chan, nick):
    return db.execute(
        "select subject from tag where lower(nick)=lower(?)"
        " and chan=?"
        " order by lower(subject)",
        (nick, chan),
    ).fetchall()


def get_tags_string_by_nick(db, chan, nick):
    tags = get_tags_by_nick(db, chan, nick)

    if tags:
        return 'tags for "%s": ' % munge(nick, 1) + winnow([tag[0] for tag in tags])
    else:
        return ""


def get_nicks_by_tagset(db, chan, tagset):
    nicks = None
    for tag in tagset.split("&"):
        tag = tag.strip()

        current_nicks = db.execute(
            "select lower(nick) from tag where " + "lower(subject)=lower(?)"
            " and chan=?",
            (tag, chan),
        ).fetchall()

        if not current_nicks:
            return "tag '%s' not found" % tag

        if nicks is None:
            nicks = set(current_nicks)
        else:
            nicks.intersection_update(current_nicks)

    nicks = [munge(x[0], 1) for x in sorted(nicks)]
    if not nicks:
        return 'no nicks found with tags "%s"' % tagset
    return 'nicks tagged "%s": ' % tagset + winnow(nicks)


@hook.command
def tag(inp, chan="", db=None):
    ".tag <nick> <tag> -- marks <nick> as <tag> {related: .untag, .tags, .tagged, .is}"

    db.execute("create table if not exists tag(chan, subject, nick)")

    add = re.match(r"(\S+) (.+)", inp)

    if add:
        nick, subject = add.groups()
        if nick.lower() == "list":
            return "tag syntax has changed. try .tags or .tagged instead"
        elif nick.lower() == "del":
            return 'tag syntax has changed. try ".untag %s" instead' % subject
        return add_tag(db, chan, sanitize(nick), sanitize(subject))
    else:
        tags = get_tags_string_by_nick(db, chan, inp)
        if tags:
            return tags
        else:
            return tag.__doc__


@hook.command
def untag(inp, chan="", db=None):
    ".untag <nick> <tag> -- unmarks <nick> as <tag> {related: .tag, .tags, .tagged, .is}"

    delete = re.match(r"(\S+) (.+)$", inp)

    if delete:
        nick, del_tag = delete.groups()
        return delete_tag(db, chan, nick, del_tag)
    else:
        return untag.__doc__


@hook.command
def tags(inp, chan="", db=None):
    ".tags <nick>/<nick1> <nick2>/list -- get list of tags for <nick>, or a list of tags {related: .tag, .untag, .tagged, .is}"
    if inp == "list":
        return get_tag_counts_by_chan(db, chan)
    elif " " in inp:
        tag_intersect = None
        nicks = [nick.strip() for nick in inp.split(" ")]
        munged_nicks = [munge(x, 1) for x in nicks]
        for nick in nicks:
            curr_tags = get_tags_by_nick(db, chan, nick)

            if not curr_tags:
                return 'nick "%s" not found' % nick

            if tag_intersect is None:
                tag_intersect = set(curr_tags)
            else:
                tag_intersect.intersection_update(curr_tags)

        msg = 'shared tags for nicks "%s"' % winnow(munged_nicks)
        if not tag_intersect:
            return f"no {msg}"
        else:
            return f"{msg}: " + winnow(
                [tag[0] for tag in tag_intersect], 400 - len(msg)
            )

    tags = get_tags_string_by_nick(db, chan, inp)
    if tags:
        return tags
    else:
        return get_nicks_by_tagset(db, chan, inp)


@hook.command
def tagged(inp, chan="", db=None):
    ".tagged <tag> [& tag...] -- get nicks marked as <tag> (separate multiple tags with &) {related: .tag, .untag, .tags, .is}"

    return get_nicks_by_tagset(db, chan, inp)


@hook.command("is")
def is_tagged(inp, chan="", db=None):
    ".is <nick> <tag> -- checks if <nick> has been marked as <tag> {related: .tag, .untag, .tags, .tagged}"

    args = re.match(r"(\S+) (.+)$", inp)

    if args:
        nick, tag = args.groups()
        found = db.execute(
            "select 1 from tag"
            " where lower(nick)=lower(?)"
            "   and lower(subject)=lower(?)"
            "   and chan=?",
            (nick, tag, chan),
        ).fetchone()
        if found:
            return "yes"
        else:
            return "no"
    else:
        return is_tagged.__doc__


def distance(lat1, lon1, lat2, lon2):
    deg_to_rad = old_div(math.pi, 180)
    lat1 *= deg_to_rad
    lat2 *= deg_to_rad
    lon1 *= deg_to_rad
    lon2 *= deg_to_rad

    R = 6371  # km
    d = (
        math.acos(
            math.sin(lat1) * math.sin(lat2)
            + math.cos(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)
        )
        * R
    )
    return d


@hook.command(autohelp=False)
def near(inp, nick="", chan="", db=None):
    try:
        loc = db.execute(
            "select lat, lon from location where chan=? and nick=lower(?)", (chan, nick)
        ).fetchone()
    except db.OperationError:
        loc = None

    if loc is None:
        return "use .weather <loc> first to set your location"

    lat, lon = loc

    db.create_function("distance", 4, distance)
    nearby = db.execute(
        "select nick, distance(lat, lon, ?, ?) as dist from location where chan=?"
        " and nick != lower(?) order by dist limit 20",
        (lat, lon, chan, nick),
    ).fetchall()

    in_miles = "mi" in inp.lower()

    out = "(km) "
    factor = 1.0
    if in_miles:
        out = "(mi) "
        factor = 0.621

    while nearby and len(out) < 200:
        nick, dist = nearby.pop(0)
        out += "%s:%.0f " % (munge(nick, 1), dist * factor)

    return out


character_replacements = {
    "a": "ä",
    #    'b': 'Б',
    "c": "ċ",
    "d": "đ",
    "e": "ë",
    "f": "ƒ",
    "g": "ġ",
    "h": "ħ",
    "i": "í",
    "j": "ĵ",
    "k": "ķ",
    "l": "ĺ",
    #    'm': 'ṁ',
    "n": "ñ",
    "o": "ö",
    "p": "ρ",
    #    'q': 'ʠ',
    "r": "ŗ",
    "s": "š",
    "t": "ţ",
    "u": "ü",
    #    'v': '',
    "w": "ω",
    "x": "χ",
    "y": "ÿ",
    "z": "ź",
    "A": "Å",
    "B": "Β",
    "C": "Ç",
    "D": "Ď",
    "E": "Ē",
    #    'F': 'Ḟ',
    "G": "Ġ",
    "H": "Ħ",
    "I": "Í",
    "J": "Ĵ",
    "K": "Ķ",
    "L": "Ĺ",
    "M": "Μ",
    "N": "Ν",
    "O": "Ö",
    "P": "Р",
    #    'Q': 'Ｑ',
    "R": "Ŗ",
    "S": "Š",
    "T": "Ţ",
    "U": "Ů",
    #    'V': 'Ṿ',
    "W": "Ŵ",
    "X": "Χ",
    "Y": "Ỳ",
    "Z": "Ż",
}
