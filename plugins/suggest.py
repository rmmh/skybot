import random
import re

from util import hook, http


@hook.command
def suggest(inp, inp_unstripped=None):
    ".suggest [#n] <phrase> -- gets a random/the nth suggested google search"

    if inp_unstripped is not None:
        inp = inp_unstripped
    m = re.match('^#(\d+) (.+)$', inp)
    num = 0
    if m:
        num, inp = m.groups()
        num = int(num)

    json = http.get_json('http://suggestqueries.google.com/complete/search', client='firefox', q=inp)
    suggestions = json[1]
    if not suggestions:
        return 'no suggestions found'

    if not num:
        num = random.randint(1, len(suggestions))
    if len(suggestions) + 1 <= num:
        return 'only got %d suggestions' % len(suggestions)
    out = suggestions[num - 1]
    return '#%d: %s' % (num, out)
