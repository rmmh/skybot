from util import hook
import random
import re
import simplejson as json


def db_init(db):
    db.execute("create table if not exists markov(prefix, suffix,"
               " primary key(prefix))")
    db.commit()
    db.execute("create table if not exists markov_settings_one("
               "setting, auto, frequency, primary key(setting))")
    db.commit()


def get_memory(db, prefix):
    suffix_list = db.execute("select suffix from markov where prefix=?",
                             (prefix,)).fetchone()
    if suffix_list:
        return suffix_list[0]
    else:
        return None


def create_memory(db, prefix, suffix):
    suffix_list = get_memory(db, prefix)
    if suffix_list:
        suffix_list = json.loads(suffix_list)
        for i in suffix_list:
            if i[0] == suffix:
                i[1] += 1
                break
        else:
            suffix_list.append([suffix, 1])
    else:
        suffix_list = [[suffix, 1]]

    db.execute("replace into markov(prefix, suffix) values"
               " (?,?)", (prefix, json.dumps(suffix_list)))
    db.commit()


def get_settings(db):
    settings = db.execute("select * from markov_settings_one where setting=0"
                          ).fetchone()
    if settings:
        return settings
    else:
        return None


def set_settings(db, settings):
    db.execute(
        "replace into markov_settings_one(setting, auto, "
        "frequency) values (?,?,?)", (0, settings[0], settings[1]))
    db.commit()


def less(db, conn, channel, string):
    if not string:
        return
    if string == re.findall(r"[ ]*", string)[0]:
        return
    two = re.findall(r"[^ ]+[ ][^ ]+", string)
    if two:
        two = two[0].strip()
        prefix = re.split(r" [^ ]+$", two)[0]
        suffix = re.findall(r"[^ ]+$", two)[0]
        create_memory(db, prefix, suffix)

        three = re.findall(r"[^ ]+[ ][^ ]+[ ][^ ]+", string)
        if three:
            three = three[0].strip()
            prefix = re.split(r" [^ ]+$", three)[0]
            suffix = re.findall(r"[^ ]+$", three)[0]
            create_memory(db, prefix, suffix)

            four = re.findall(r"[^ ]+[ ][^ ]+[ ][^ ]+[ ][^ ]+", string)
            if four:
                four = four[0].strip()
                prefix = re.split(r" [^ ]+$", four)[0]
                suffix = re.findall(r"[^ ]+$", four)[0]
                create_memory(db, prefix, suffix)
        else:
            terminal = re.findall(r"[ ]*[^ ]+$", two)[0]
            if terminal:
                terminal = terminal.strip()
                create_memory(db, terminal, "")

    less(db, conn, channel, re.sub("[^ ]+", "", string, count=1))


@hook.event("PRIVMSG")
def markov(inp, db=None, bot=None, conn=None):
    """The guts of the operation"""
    db_init(db)
    if len(inp[1]) > 0 and inp[1][0] != ".":
        less(db, conn, inp[0], inp[1])
    rand = random.random()
    settings = get_settings(db)
    if bool(settings[1]) and rand < (1.0/float(settings[2])) and inp[
            1][0] != ".":
        output = get_random_row(db)
        say_chain(db, output, conn, inp[0])


def find_one(inp, db):
    memory = get_memory(db, inp)
    if not memory:
        return None
    suffix_list = json.loads(memory)

    total_count = 0
    for suffix in suffix_list:
        total_count += suffix[1]
    for suffix in suffix_list:
        suffix[1] = suffix[1] / float(total_count)

    rand = random.random()
    for suffix in suffix_list:
        rand -= suffix[1]
        if rand < 0:
            return suffix[0]


def get_suffix_list(inp, db):
    memory = get_memory(db, inp)
    if not memory:
        return None
    return json.loads(memory)


def normalize_suffix_list(suffix_list):
    total_count = 0
    for suffix in suffix_list:
        total_count += suffix[1]
    for suffix in suffix_list:
        suffix[1] = suffix[1] / float(total_count)


def pick_one(suffix_list):
    if not suffix_list:
        return None
    rand = random.random()
    for suffix in suffix_list:
        rand -= suffix[1]
        if rand < 0:
            return suffix[0]


def get_random_row(db):
    return db.execute("SELECT prefix FROM markov ORDER BY RANDOM() LIMIT 1;"
                      ).fetchone()[0]


def say_chain(db, output, conn, channel):
    next_word = find_one(output, db)
    while next_word:
        output += " " + next_word
        suffix_list = []
        one = re.findall(r"[^ ]+$", output)
        if one:
            one_suffix = get_suffix_list(one[0], db)
            if one_suffix:
                suffix_list += one_suffix
        two = re.findall(r"[^ ]+$", output)
        if two:
            two_suffix = get_suffix_list(two[0], db)
            if two_suffix:
                suffix_list += two_suffix
        three = re.findall(r"[^ ]+$", output)
        if three:
            three_suffix = get_suffix_list(three[0], db)
            if three_suffix:
                suffix_list += three_suffix
        normalize_suffix_list(suffix_list)
        next_word = pick_one(suffix_list)
    conn.msg(channel, output)


@hook.event("PRIVMSG")
def auto_chain(inp, db=None, conn=None):
    db_init(db)
    rand = random.random()
    if rand < 0.15 and inp[1][0] != ".":
        output = get_random_row(db)
        say_chain(db, output, conn, inp[0])


@hook.command
def chain(inp, db=None, conn=None, chan=None):
    """Creates a markov chain. Usage: .chain <seed word or phrase>"""
    db_init(db)
    say_chain(db, inp, conn, chan)


@hook.command
def markon(inp, db=None):
    """Turns on Automatic Markov Chains with a frequency value.\
     Usage: .markon 10"""
    db_init(db)
    try:
        assert(int(inp) > 0)
    except:
        return "Need to include a positive integer"
    set_settings(db, (True, int(inp)))
    return "Markov, on! Will automatically generate a chain on \
        message with {0} probability".format(str(1.0/float(inp))[:4])


@hook.regex("^.markoff$")
def markoff(inp, db=None):
    """Turns off Automatic Markov Chains"""
    set_settings(db, (False, 1))
    return "Markov, off! No more random bullshit in the chat."

