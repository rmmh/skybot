import re
import urllib2

import hook


tinyurl_re = re.compile(r'http://(?:www\.)?tinyurl.com/([A-Za-z0-9\-]+)', flags=re.IGNORECASE)


@hook.command(hook=r'(.*)', prefix=False)
def tinyurl(inp):
    tumatch = tinyurl_re.search(inp)
    if tumatch:
        try:
            return urllib2.urlopen(tumatch.group()).url.strip()
        except urllib2.URLError:
            pass
