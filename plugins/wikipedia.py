'''Searches wikipedia and returns first sentence of article
Scaevolus 2009'''

import urllib2
from lxml import etree
import re

from util import hook


api_prefix = "http://en.wikipedia.org/w/api.php"
search_url = api_prefix + "?action=opensearch&search=%s&format=xml"

paren_re = re.compile('\s*\(.*\)$')


@hook.command('w')
@hook.command
def wiki(inp):
    '''.w/.wiki <phrase> -- gets first sentence of wikipedia ''' \
    '''article on <phrase>'''

    if not inp:
        return wiki.__doc__

    q = search_url % (urllib2.quote(inp, safe=''))

    request = urllib2.Request(q)
    request.add_header('User-Agent',
                'Skybot/1.0 http://bitbucket.org/Scaevolus/skybot/')
    opener = urllib2.build_opener()
    xml = opener.open(request).read()
    x = etree.fromstring(xml)

    ns = '{http://opensearch.org/searchsuggest2}'
    items = x.findall(ns + 'Section/' + ns + 'Item')

    if items == []:
        if x.find('error') is not None:
            return 'error: %(code)s: %(info)s' % x.find('error').attrib
        else:
            return 'no results found'

    def extract(item):
        return [item.find(ns + x).text for x in
                            ('Text', 'Description', 'Url')]

    title, desc, url = extract(items[0])

    if 'may refer to' in desc:
        title, desc, url = extract(items[1])

    title = paren_re.sub('', title)

    if title.lower() not in desc.lower():
        desc = title + desc

    desc = re.sub('\s+', ' ', desc).strip()  # remove excess spaces

    if len(desc) > 300:
        desc = desc[:300] + '...'

    return '%s -- %s' % (desc, url)
