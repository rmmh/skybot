from lxml import html
from util import hook
import urllib

@hook.command
def down(inp):
    '''.down <url> -- checks http://downforeveryoneorjustme.com to see if the site is down'''

    url = 'http://downforeveryoneorjustme.com/' + urllib.quote(inp.strip(), safe='')
    page = html.parse(url)
    status = page.xpath("//title")[0].text_content()

    return status

#local testing
#print down("googlelakj.com")