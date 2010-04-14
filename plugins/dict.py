import re
import urllib

from lxml import html

from util import hook


@hook.command('u')
@hook.command
def urban(inp):
    '''.u/.urban <phrase> -- looks up <phrase> on urbandictionary.com'''
    if not inp:
        return urban.__doc__

    url = 'http://www.urbandictionary.com/define.php?term=' + \
            urllib.quote(inp, safe='')
    page = html.parse(url)
    words = page.xpath("//td[@class='word']")
    defs = page.xpath("//div[@class='definition']")

    if not defs:
        return 'no definitions found'

    out = words[0].text_content().strip() + ': ' + ' '.join(
            defs[0].text_content().split())

    if len(out) > 400:
        out = out[:out.rfind(' ', 0, 400)] + '...'

    return out


## A dictionary look-up plugin for Skybot made by Ghetto Wizard and Scaevolus

@hook.command('dict')
@hook.command
def define(inp):
    ".define/.dict <word> -- fetches definition of <word>"

    if not inp:
        return define.__doc__

    base_url = 'http://dictionary.reference.com/browse/'

    raw_data = urllib.urlopen(base_url + urllib.quote(inp, '')).read()
    raw_data = raw_data.decode('utf-8')

    definition = html.fromstring(raw_data).xpath('//span[@class="dnindex"]'
                                                 ' | //div[@class="dndata"]')

    if not definition:
        return 'No results for ' + inp

    result = ' '.join(section.text_content() for section in definition)
    result = re.sub(r'\s+', ' ', result)

    if len(result) > 400:
        result = result[:result.rfind(' ', 0, 400)]
        result = re.sub(r'[^A-Za-z]+\.?$', '', result) + ' ...' #truncate

    return result
