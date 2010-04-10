import urllib

from lxml import html

from util import hook


@hook.command('god')
@hook.command
def bible(inp):
    ".bible <passage> -- gets <passage> from the Bible (ESV)"

    if not inp:
        return bible.__doc__

    base_url = 'http://www.esvapi.org/v2/rest/passageQuery?key=IP&' \
        'output-format=plain-text&include-heading-horizontal-lines&' \
        'include-headings=false&include-passage-horizontal-lines=false&' \
        'include-passage-references=false&include-short-copyright=false&' \
        'include-footnotes=false&line-length=0&passage='

    text = urllib.urlopen(base_url + urllib.quote(inp)).read()

    text = ' '.join(text.split())

    if len(text) > 400:
        text = text[:text.rfind(' ', 0, 400)] + '...'

    return text

## Koran look-up plugin by Ghetto Wizard

@hook.command('allah')
@hook.command
def koran(inp):
    ".koran <chapter.verse> -- gets <chapter.verse> from the Koran"

    if not inp:
        return koran.__doc__

    base_url = 'http://quod.lib.umich.edu/cgi/k/koran/koran-idx?type=simple&q1='

    raw_data = urllib.urlopen(base_url + urllib.quote(inp, '')).read()
    
    results = html.fromstring(raw_data).xpath('//li')
    
    if not results:
        return 'No results for ' + inp

    return results[0].text_content()
