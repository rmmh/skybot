from lxml import html
import urllib

from util import hook


@hook.command('u')
@hook.command
def urban(inp):
    '''.u/.urban <phrase> -- looks up <phrase> on urbandictionary.com'''
    if not inp.strip():
        return urban.__doc__

    url = 'http://www.urbandictionary.com/define.php?term=' + \
            urllib.quote(inp.strip(), safe='')
    page = html.parse(url)
    words = page.xpath("//td[@class='word']")
    defs = page.xpath("//div[@class='definition']")

    if not defs:
        return 'no definitions found'

    out = words[0].text_content().strip() + ' '.join(
            defs[0].text_content().split())

    if len(out) > 400:
        out = out[:out.rfind(' ', 0, 400)] + '...'

    return out
