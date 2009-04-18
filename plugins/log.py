"""
log.py: written by Scaevolus 2009
"""

from __future__ import with_statement

import os
import thread
import codecs
import time

import hook

lock = thread.allocate_lock()
log_fds = {} # '%(net)s %(chan)s' : (filename, fd)

timestamp_format = '%H:%M:%S'

def get_log_filename(dir, network, chan):
    return os.path.join(dir, 'log', gmtime('%Y'), network,
            gmtime('%%s.%m-%d.log') % chan).lower()

def gmtime(format):
    return time.strftime(format, time.gmtime())

def get_log_fd(dir, network, chan):
    fn = get_log_filename(dir, network, chan)
    cache_key = '%s %s' % (network, chan)
    filename, fd = log_fds.get(cache_key, ('', 0))

    if fn != filename: # we need to open a file for writing
        if fd != 0: # is a valid fd
            fd.flush()
            fd.close()
        dir = os.path.split(fn)[0]
        if not os.path.exists(dir):
            os.makedirs(dir)
        fd = codecs.open(fn, 'a', 'utf-8')
        log_fds[cache_key] = (fn, fd)

    return fd

@hook.event(ignorebots=False)
def log(bot, input):
    ".remember <word> <data> -- maps word to data in the memory"
    with lock: 
        fd = get_log_fd(bot.persist_dir, bot.network, 'raw')
        fd.write(gmtime(timestamp_format) + ' ' + input.raw + '\n')

        if input.chan:
            fd = get_log_fd(bot.persist_dir, bot.network, input.chan)
            fd.write(gmtime(timestamp_format) + ' ' + input.raw + '\n')
