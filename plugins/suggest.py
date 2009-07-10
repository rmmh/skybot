import random
import urllib
import urllib2

from util import hook, yaml

@hook.command
def suggest(inp):
    ".suggest <phrase> -- returns a random suggested google search"
    if not inp.strip():
        return suggest.__doc__

    url = 'http://google.com/complete/search?q=' + urllib.quote(inp, safe='')
    json = urllib2.urlopen(url).read()
    json = json[json.find('(') + 1: -1]
    suggestions = yaml.load(json)[1]
    if not suggestions:
        return 'no suggestions found'
    suggestion = random.choice(suggestions)
    return '#%d: %s (%s)' % tuple([int(suggestion[2]) + 1] + suggestion[0:2])
