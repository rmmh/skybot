from util import hook

import tell
import tag


def get_nicks_by_tagset(db, chan, tagset):
    # mostly copied from tag.py. It even uses the tag db!
    nicks = None
    for tags in tagset.split('&'):
        tags = tags.strip()

        current_nicks = db.execute("select nick from tag where " +
                                   "lower(subject)=lower(?)"
                                   " and chan=?", (tags, chan)).fetchall()

        if not current_nicks:
            return None

        if nicks is None:
            nicks = set(current_nicks)
        else:
            nicks.intersection_update(current_nicks)

    if not nicks:
        return []
    return [nick[0] for nick in nicks]


def oxford(names, conjunction="and"):
    if len(names) == 0:
        return "nobody"
    elif len(names) == 1:
        return names[0]
    elif len(names) == 2:
        return "%s %s %s" % (names[0], conjunction, names[1])

    names = names[:]
    names[-1] = "%s %s" % (conjunction, names[-1])
    return ", ".join(names)


@hook.command
def broadcast(inp, nick='', chan='', db=None):
    ".broadcast <tagset> <message> -- do a .tell to everybody in <tagset>"

    tell.db_init(db)

    q = inp.split(" ", 1)
    if len(q) < 2:
        return broadcast.__doc__

    tagset, msg = q

    nicks = get_nicks_by_tagset(db, chan, tagset)

    if nicks is None or len(nicks) == 0:
        return "Nobody fitting that description here."

    if nick in nicks:
        nicks.remove(nick)

    if len(nicks) == 0:
        return "You're the only one like that. Freak."

    successes = []
    failures = []
    for to in nicks:
        ret = tell.tell("%s %s" % (to, msg), nick, chan, db)

        if ret == "I'll pass that along.":
            successes += [tag.munge(to, 1)]
        else:
            failures += [tag.munge(to, 1)]

    result = ""

    if len(successes) > 0:
        result += "I passed it along to " + oxford(successes) + ". "
    if len(failures) > 0:
        result += "I didn't get to send it to " + oxford(failures, "or") + "."

    return result
