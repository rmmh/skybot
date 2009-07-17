import random
import urllib
import urllib2
import re

from util import hook, yaml

@hook.command
def suggest(inp):
    ".suggest [#n] <phrase> -- gets a random/the nth suggested google search"
    if not inp.strip():
        return suggest.__doc__
 
    m = re.match('^#(\d+) (.+)$', inp)
    if m:
        num, inp = m.groups()
        num = int(num)
        if num > 10:
            return 'can only get first ten suggestions'
    else:
        num = 0

    url = 'http://google.com/complete/search?q=' + urllib.quote(inp, safe='')
    json = urllib2.urlopen(url).read()
    json = json[json.find('(') + 1: -1]
    suggestions = yaml.load(json)[1]
    if not suggestions:
        return 'no suggestions found'
    if num:
        if len(suggestions) + 1 <= num:
            return 'only got %d suggestions' % len(suggestions)
        out = suggestions[num - 1]
    else:
        out = random.choice(suggestions)
    return '#%d: %s (%s)' % (int(out[2][0]) + 1, out[0], out[1])
