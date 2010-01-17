import re
from lxml import etree
import locale

from util import hook


def ytdata(id):
    url = 'http://gdata.youtube.com/feeds/api/videos/' + id
    x = etree.parse(url)

    # I can't figure out how to deal with schemas/namespaces properly :(
    yt = '{http://gdata.youtube.com/schemas/2007}'
    media = '{http://search.yahoo.com/mrss/}'

    rating = x.find('{http://schemas.google.com/g/2005}rating')
    data = dict(rating.items())
    data['title'] = x.find('{http://www.w3.org/2005/Atom}title').text
    data['views'] = locale.format('%d', int(x.find(yt + 'statistics').get(
                        'viewCount')), 1)
    length = int(x.find(media + 'group/' + yt + 'duration').get('seconds'))
    data['length'] = ''
    if length / 3600: # > 1 hour
        data['length'] += str(length/3600) + 'h '
    if length / 60: # > 1 minute
        data['length'] += str(length/60 % 60) + 'm '
    data['length'] += "%ds" % (length % 60)

    return data

youtube_re = re.compile(r'.*youtube.*v=([-_a-z0-9]+)', flags=re.IGNORECASE)


#@hook.command(hook=r'(.*)', prefix=False)
def youtube(inp):
    m = youtube_re.match(inp)
    if m:
        data = ytdata(m.group(1))
        return '\x02%(title)s\x02 - rated \x02%(average)s/%(max)s\x02 ' \
                '(%(numRaters)s) - views \x02%(views)s\x02 - length \x02' \
                '%(length)s\x02' % data
