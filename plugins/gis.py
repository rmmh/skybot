import yaml
import urllib

import hook


@hook.command
def gis(inp):
    req_url = 'http://ajax.googleapis.com/ajax/services/search/images?' \
            'v=1.0&safe=off&q='
    url = req_url + urllib.quote(inp, safe='')
    json = urllib.urlopen(url).read()
    parsed = yaml.load(json)
    if not 200 <= parsed['responseStatus'] < 300:
        raise IOError('error searching for images: %d: %s' % (
                parsed['responseStatus'], ''))
    if not parsed['responseData']['results']:
        return 'no images found'
    return parsed['responseData']['results'][0]['unescapedUrl']
