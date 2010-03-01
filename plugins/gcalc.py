import urllib2
import re

from lxml import html

from util import hook


@hook.command
def calc(inp):
    '''.calc <term> -- returns Google Calculator result'''
    if not inp:
        return calc.__doc__

    url = "http://www.google.com/search?q="
    request = urllib2.Request(url + urllib2.quote(inp, ''))
    request.add_header('User-Agent', 'skybot')
    page = urllib2.build_opener().open(request).read()

    # ugh, scraping HTML with regexes
    m = re.search(r'<h2 class=r style="font-size:138%"><b>(.*?)</b>', page)

    if m is None:
        return "could not calculate " + inp

    result = m.group(1).replace("<font size=-2> </font>", ",")
    result = result.replace(" &#215; 10<sup>", "E").replace("</sup>", "")
    result = result.replace("\xa0", ",")
    return result
