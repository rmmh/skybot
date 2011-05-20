# searches scene releases using orlydb

from util import hook, http


@hook.command
def predb(inp):
    '.predb <query> -- searches scene releases using orlydb.com'

    try:
        h = http.get_html("http://orlydb.com/", q=inp)
    except HTTPError:
        return 'orlydb seems to be down'

    results = h.xpath("//div[@id='releases']/div/span[@class='release']/..")

    if not results:
        return "zero results"

    result = results[0]

    date, time = result.xpath("span[@class='timestamp']/text()")[0].split()
    section, = result.xpath("span[@class='section']//text()")
    name, = result.xpath("span[@class='release']/text()")

    size = result.xpath("span[@class='inforight']//text()")
    if size:
        size = ' :: ' + size[0].split()[0]
    else:
        size = ''
 
    return '%s - %s - %s%s' % (date, section, name, size)
