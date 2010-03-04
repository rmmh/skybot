'''Searches Encyclopedia Dramatica and returns the first paragraph of the 
article'''

import json
from lxml import html
import urllib2

from util import hook

api_url = "http://encyclopediadramatica.com/api.php?action=opensearch&search=%s"
ed_url = "http://encyclopediadramatica.com/%s"

ua_header = ('User-Agent','Skybot/1.0 http://bitbucket.org/Scaevolus/skybot/')


@hook.command('ed')   
@hook.command
def drama(inp):
    '''.drama <phrase> -- gets first paragraph of Encyclopedia Dramatica ''' \
    '''article on <phrase>'''
    if not inp:
        return drama.__doc__
    
    q = api_url % (urllib2.quote(inp, safe=''))
    request = urllib2.Request(q)
    request.add_header(*ua_header)
    j = json.loads(urllib2.build_opener().open(request).read())
    if not j[1]:
        return 'no results found'
    article_name = j[1][0].replace(' ', '_')
    
    url = ed_url % (urllib2.quote(article_name))
    request = urllib2.Request(url)
    request.add_header(*ua_header)
    page = html.fromstring(urllib2.build_opener().open(request).read())
    
    for p in page.xpath('//div[@id="bodyContent"]/p'):
        if p.text_content():
            summary = ' '.join(p.text_content().splitlines())
            if len(summary) > 300:
                summary = summary[:summary.rfind(' ', 0, 300)] + "..."
            return '%s :: \x02%s\x02' % (summary, url)

    return "error"
