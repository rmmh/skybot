import urllib
import random
from lxml import html
import json

from util import hook


def api_get(kind, query):
    req_url = 'http://ajax.googleapis.com/ajax/services/search/%s?' \
            'v=1.0&safe=off&q=%s'
    url = req_url % (kind, urllib.quote(query, safe=''))
    page = urllib.urlopen(url).read()
    return json.loads(page)


@hook.command
def gis(inp):
    '''.gis <term> -- returns first google image result (safesearch off)'''
    if not inp:
        return gis.__doc__

    parsed = api_get('images', inp)
    if not 200 <= parsed['responseStatus'] < 300:
        raise IOError('error searching for images: %d: %s' % (
                parsed['responseStatus'], ''))
    if not parsed['responseData']['results']:
        return 'no images found'
    return random.choice(parsed['responseData']['results'][:10]
            )['unescapedUrl'] # squares is dumb


@hook.command
@hook.command('g')
def google(inp):
    '''.g/.google <query> -- returns first google search result'''
    if not inp:
        return google.__doc__

    parsed = api_get('web', inp)
    if not 200 <= parsed['responseStatus'] < 300:
        raise IOError('error searching for pages: %d: %s' % (
                parsed['responseStatus'], ''))
    if not parsed['responseData']['results']:
        return 'no results found'

    result = parsed['responseData']['results'][0]

    title, content = map(lambda x: html.fromstring(x).text_content(),
            (result['titleNoFormatting'], result['content']))

    out = '%s -- \x02%s\x02: "%s"' % (result['unescapedUrl'], title, content)
    out = ' '.join(out.split())

    if len(out) > 300:
        out = out[:out.rfind(' ')] + '..."'

    return out
