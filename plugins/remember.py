"""
remember.py: written by Scaevolus 2009
"""

from __future__ import with_statement

import os
import thread
import codecs

import hook

lock = thread.allocate_lock()
memory = {}


def load_memory(filename, mtimes={}):
    if not os.path.exists(filename):
        return {}
    mtime = os.stat(filename).st_mtime
    if mtimes.get(filename, 0) != mtime:
        mtimes[filename] = mtime
        return dict((x.split(None, 1)[0].lower(), x.strip()) for x in
                codecs.open(filename, 'r', 'utf-8'))


def save_memory(filename, memory):
    out = codecs.open(filename, 'w', 'utf-8')
    out.write('\n'.join(sorted(memory.itervalues())))
    out.flush()
    out.close()


def make_filename(dir, chan):
    return os.path.join(dir, 'memory')


@hook.command
def remember(bot, input):
    ".remember <word> <data> -- maps word to data in the memory"
    with lock:
        filename = make_filename(bot.persist_dir, input.chan)
        memory.setdefault(filename, load_memory(filename))

        try:
            head, tail = input.inp.split(None, 1)
        except ValueError:
            return remember.__doc__

        tail = tail.strip()
        low = head.lower()
        if low not in memory[filename]:
            bot.reply("done.")
        else:
            bot.reply('forgetting that "%s", remembering this instead.' %
                    memory[filename][low])
        memory[filename][low] = input.inp.strip()
        save_memory(filename, memory[filename])


@hook.command
def forget(bot, input):
    ".forget <word> -- forgets the mapping that word had"
    with lock:
        filename = make_filename(bot.persist_dir, input.chan)
        memory.setdefault(filename, load_memory(filename))

        if not input.inp.strip():
            return forget.__doc__

        low = input.inp.strip().lower()
        if low not in memory[filename]:
            return "I don't know about that."
        if not hasattr(input, 'chan'):
            return "I won't forget anything in private."
        bot.say("Forgot that %s" % memory[filename][low])
        del memory[filename][low]
        save_memory(filename, memory[filename])


@hook.command(hook='\?(.+)', prefix=False)
def question(bot, input):
    "?<word> -- shows what data is associated with word"
    with lock:
        filename = make_filename(bot.persist_dir, input.chan)
        memory.setdefault(filename, load_memory(filename))

        word = input.inp.split()[0].lower()
        if word in memory[filename]:
            bot.say("%s" % memory[filename][word])
