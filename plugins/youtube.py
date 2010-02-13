import json
import locale
import re
import urllib2

from util import hook

locale.setlocale(locale.LC_ALL, '')

youtube_re = re.compile(r'.*youtube.*v=([-_a-z0-9]+)', flags=re.I)
url = 'http://gdata.youtube.com/feeds/api/videos/%s?alt=json'

#@hook.command(hook=r'(.*)', prefix=False)
def youtube(inp):
    m = youtube_re.match(inp)
    if m:
        j = json.load(urllib2.urlopen(url % m.group(1)))['entry']
        
        out = '\x02%s\x02' % j['title']['$t']

        rating = j.get('gd$rating')
        if rating:
            out += ' - rated \x02%.2f/%.1f\x02 (%d)' % (rating['average'],
                    rating['max'], rating['numRaters'])

        stats = j.get('yt$statistics')
        if stats:
            view_count = int(stats['viewCount'])
            out += ' - views \x02%s\x02' % locale.format('%d', view_count, 1)

        out += ' - length \x02'
        length = int(j['media$group']['yt$duration']['seconds'])
        if length / 3600: # > 1 hour
            out += '%dh ' % (length / 3600)
        if length / 60:
            out += '%dm ' % (length / 60 % 60)
        out += "%ds" % (length % 60)

        return out
