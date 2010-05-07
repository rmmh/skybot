import re

from util import hook, http


@hook.command
def calc(inp):
    '''.calc <term> -- returns Google Calculator result'''

    page = http.get('http://www.google.com/search', q=inp)

    # ugh, scraping HTML with regexes
    m = re.search(r'<h2 class=r style="font-size:138%"><b>(.*?)</b>', page)

    if m is None:
        return "could not calculate " + inp

    result = m.group(1).replace("<font size=-2> </font>", ",")
    result = result.replace(" &#215; 10<sup>", "E").replace("</sup>", "")
    result = result.replace("\xa0", ",")
    return result
