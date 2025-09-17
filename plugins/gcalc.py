
from util import hook, http


@hook.command
def calc(inp):
    """.calc <term> -- returns Google Calculator result"""

    h = http.get_html("http://www.google.com/search", q=inp)

    m = h.xpath('//h2[@class="r"]/text()')

    if not m:
        return "could not calculate " + inp

    res = " ".join(m[0].split())

    return res
