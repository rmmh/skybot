"weather, thanks to google"

import os
import codecs
import thread
import urllib
from lxml import etree

from util import hook


lock = thread.allocate_lock()
stalk = {}


def load_stalk(filename, mtimes={}):
    if not os.path.exists(filename):
        return {}
    mtime = os.stat(filename).st_mtime
    if mtimes.get(filename, 0) != mtime:
        mtimes[filename] = mtime
        return dict(x.strip().split(None, 1) for x in
                codecs.open(filename, 'r', 'utf-8'))


def save_stalk(filename, houses):
    out = codecs.open(filename, 'w', 'utf-8')
    out.write('\n'.join('%s %s' % x for x in sorted(houses.iteritems()))) #heh
    out.flush()
    out.close()


@hook.command
def weather(bot, input):
    ".weather <location> -- queries the google weather API for weather data"
    global stalk

    filename = os.path.join(bot.persist_dir, 'weather')
    if not stalk:
        with lock:
            stalk = load_stalk(filename)

    nick = input.nick.lower()
    loc = input.inp.strip().lower()
    if not loc: # blank line
        loc = stalk.get(nick, '')
        if not loc:
            return weather.__doc__

    data = urllib.urlencode({'weather': loc.encode('utf-8')})
    url = 'http://www.google.com/ig/api?' + data
    w = etree.parse(url).find('weather')

    if w.find('problem_cause') is not None:
        return "Couldn't fetch weather data for '%s', try using a zip or " \
                "postal code." % input.inp

    info = dict((e.tag, e.get('data')) for e in w.find('current_conditions'))
    info['city'] = w.find('forecast_information/city').get('data')
    info['high'] = w.find('forecast_conditions/high').get('data')
    info['low'] = w.find('forecast_conditions/low').get('data')

    input.reply('%(city)s: %(condition)s, %(temp_f)sF/%(temp_c)sC (H:%(high)s'\
            'F, L:%(low)sF), %(humidity)s, %(wind_condition)s.' % info)

    if loc != stalk.get(nick, ''):
        with lock:
            stalk[nick] = loc
            save_stalk(filename, stalk)
