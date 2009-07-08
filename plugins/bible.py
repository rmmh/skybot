import urllib

from util import hook


@hook.command('god')
@hook.command
def bible(inp):
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
