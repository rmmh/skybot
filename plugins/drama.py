'''Searches Encyclopedia Dramatica and returns the first paragraph of the
article'''
from __future__ import unicode_literals

from util import hook, http

api_url = "http://encyclopediadramatica.rs/api.php"
ed_url = "http://encyclopediadramatica.rs/"


@hook.command('ed')
@hook.command
def drama(inp):
    '''.drama <phrase> -- gets first paragraph of Encyclopedia Dramatica ''' \
        '''article on <phrase>'''

    j = http.get_json(api_url, action="opensearch", search=inp)
    if not j[1]:
        return 'no results found'
    article_name = j[1][0].replace(' ', '_').encode('utf8')

    url = ed_url + http.quote(article_name, '')
    page = http.get_html(url)

    for p in page.xpath('//div[@id="bodyContent"]//p'):
        if p.text_content():
            summary = ' '.join(p.text_content().splitlines())
            if len(summary) > 300:
                summary = summary[:summary.rfind(' ', 0, 300)] + "..."
            return '%s :: \x02%s\x02' % (summary, url)

    return "error"
