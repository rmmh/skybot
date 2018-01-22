from util import hook, http

# https://api.esv.org/account/create-application/
@hook.api_key('bible')
@hook.command('god')
@hook.command
def bible(inp, api_key=None):
    ".bible <passage> -- gets <passage> from the Bible (ESV)"

    base_url = ('https://api.esv.org/v3/passage/text/?'
                'include-headings=false&'
                'include-passage-horizontal-lines=false&'
                'include-heading-horizontal-lines=false&'
                'include-passage-references=false&'
                'include-short-copyright=false&'
                'include-footnotes=false&'
                )

    text = http.get_json(base_url, q=inp,
                         headers={'Authorization': 'Token ' + api_key})

    text = ' '.join(text['passages']).strip()

    if len(text) > 400:
        text = text[:text.rfind(' ', 0, 400)] + '...'

    return text


@hook.command('allah')
@hook.command
def koran(inp):  # Koran look-up plugin by Ghetto Wizard
    ".koran <chapter.verse> -- gets <chapter.verse> from the Koran"

    url = 'http://quod.lib.umich.edu/cgi/k/koran/koran-idx?type=simple'

    results = http.get_html(url, q1=inp).xpath('//li')

    if not results:
        return 'No results for ' + inp

    return results[0].text_content()
