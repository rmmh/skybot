import re
import urllib2

from util import hook


tinyurl_re = (r'http://(?:www\.)?tinyurl.com/([A-Za-z0-9\-]+)',
                re.IGNORECASE)


@hook.regex(*tinyurl_re)
def tinyurl(match):
    try:
        return urllib2.urlopen(match.group()).url.strip()
    except urllib2.URLError:
        pass
