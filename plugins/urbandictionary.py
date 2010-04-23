import re

from util import hook, http


@hook.command('u')
@hook.command
def urban(inp):
    '''.u/.urban <phrase> -- looks up <phrase> on urbandictionary.com'''
    if not inp:
        return urban.__doc__

    url = 'http://www.urbandictionary.com/define.php'
    page = http.get_html(url, term=inp)
    words = page.xpath("//td[@class='word']")
    defs = page.xpath("//div[@class='definition']")

    if not defs:
        return 'no definitions found'

    out = words[0].text_content().strip() + ': ' + ' '.join(
            defs[0].text_content().split())

    if len(out) > 400:
        out = out[:out.rfind(' ', 0, 400)] + '...'

    return out
