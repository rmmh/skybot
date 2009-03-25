import yaml
import urllib

import hook

languages = 'en ja de he es ko ru en zh en'.split();
language_pairs = zip(languages[:-1], languages[1:])

def babel_gen(inp):
    req_url = 'http://ajax.googleapis.com/ajax/services/language/translate' \
            '?v=1.0&q=%s&langpair=%s'

    yield 'en', inp
    for slang, tlang in language_pairs:
        inp = inp.encode('utf8')
        print slang, tlang, inp
        json = urllib.urlopen(req_url % (urllib.quote(inp, safe=''), 
                              slang + '%7C' + tlang)).read()
        parsed = yaml.load(json)
        if not 200 <= parsed['responseStatus'] < 300:
            raise IOError, 'error with the translation server'
        inp = parsed['responseData']['translatedText']
        yield tlang, inp

@hook.command
def babel(inp):
    try:
        return list(babel_gen(inp))[-1][1]
    except IOError:
        return 'error with the translation server'

@hook.command
def babelexp(inp):
    try:
        babels = list(babel_gen(inp))
    except IOError:
        return 'error with the translation server'

    out = u''
    for lang, text in babels:
        out += '%s:"%s", ' % (lang, text.decode('utf8'))

    if len(out) > 300:
        out = out[:150] + ' ... ' + out[-150:]

    return out[:-2]
