import json
import locale
import re
import time
import urllib2

from util import hook

locale.setlocale(locale.LC_ALL, '')

youtube_re = re.compile(r'youtube.*?v=([-_a-z0-9]+)', flags=re.I)
url = 'http://gdata.youtube.com/feeds/api/videos/%s?v=2&alt=jsonc'

def get_video_description(vid):
    print vid
    j = json.load(urllib2.urlopen(url % vid))

    if j.get('error'):
        return 

    j = j['data']

    out = '\x02%s\x02' % j['title']

    out += ' - length \x02'
    length = j['duration']
    if length / 3600: # > 1 hour
        out += '%dh ' % (length / 3600)
    if length / 60:
        out += '%dm ' % (length / 60 % 60)
    out += "%ds\x02" % (length % 60)

    if 'rating' in j:
        out += ' - rated \x02%.2f/5.0\x02 (%d)' % (j['rating'],
                j['ratingCount'])
       

    if 'viewCount' in j:
        out += ' - \x02%s\x02 views' % locale.format('%d',
                                                     j['viewCount'], 1)
        
    upload_time = time.strptime(j['uploaded'], "%Y-%m-%dT%H:%M:%S.000Z")
    out += ' - \x02%s\x02 on \x02%s\x02' % (j['uploader'],
                time.strftime("%Y.%m.%d", upload_time))

    if 'contentRating' in j:
        out += ' - \x034NSFW\x02'

    return out
    

@hook.command(hook=r'(.*)', prefix=False)
def youtube(inp):
    m = youtube_re.search(inp)
    if m:
        return get_video_description(m.group(1))
