import urllib
import htmlentitydefs
import re

from util import hook, yaml

########### from http://effbot.org/zone/re-sub.htm#unescape-html #############


def unescape(text):

    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is

    return re.sub("&#?\w+;", fixup, text)

##############################################################################

languages = 'ja fr de ko ru zh'.split()
language_pairs = zip(languages[:-1], languages[1:])


def goog_trans(text, slang, tlang):
    req_url = 'http://ajax.googleapis.com/ajax/services/language/translate' \
            '?v=1.0&q=%s&langpair=%s'
    url = req_url % (urllib.quote(text, safe=''), slang + '%7C' + tlang)
    json = urllib.urlopen(url).read()
    parsed = yaml.load(json)
    if not 200 <= parsed['responseStatus'] < 300:
        raise IOError('error with the translation server: %d: %s' % (
                parsed['responseStatus'], ''))
    return unescape(parsed['responseData']['translatedText'])


def babel_gen(inp):
    for language in languages:
        inp = inp.encode('utf8')
        trans = goog_trans(inp, 'en', language).encode('utf8')
        inp = goog_trans(trans, language, 'en')
        yield language, trans, inp


@hook.command
def babel(inp):
    try:
        return list(babel_gen(inp))[-1][2]
    except IOError, e:
        return e


@hook.command
def babelext(inp):
    try:
        babels = list(babel_gen(inp))
    except IOError, e:
        return e

    out = u''
    for lang, trans, text in babels:
        out += '%s:"%s", ' % (lang, text.decode('utf8'))

    out += 'en:"' + babels[-1][2].decode('utf8') + '"'

    if len(out) > 300:
        out = out[:150] + ' ... ' + out[-150:]

    return out
