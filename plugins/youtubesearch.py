import json
import locale
import re
import time
import urllib2
from urllib import quote_plus

from util import hook
from youtube import get_video_description

locale.setlocale(locale.LC_ALL, '')

url = "http://gdata.youtube.com/feeds/api/videos?q=%s&max-results=1&alt=json"
video_url = "http://youtube.com/watch?v=%s"

@hook.command
@hook.command('y')
def youtube(inp):
    '.youtube <query> -- returns the first YouTube search result for <query>'
    inp = quote_plus(inp)
    j = json.load(urllib2.urlopen(url % (inp)))
    if j.get('error'):
        return
    
    try:
        vid = j['feed']['entry'][0]['id']['$t']
        #youtube returns a gdata url for this some reason. The videoid has to be stripped out
        vid = vid[vid.rfind('/')+1:]
        return get_video_description(vid) + " " + video_url%vid
    except:
        return
