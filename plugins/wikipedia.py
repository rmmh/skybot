#!/usr/bin/python
'''Searches wikipedia and returns first sentence of article
Scaevolus 2009'''

import urllib
from lxml import etree
import re

import hook

api_prefix = "http://en.wikipedia.org/w/api.php"
search_url = api_prefix + "?action=opensearch&search=%s&format=xml"

paren_re = re.compile('\s*\(.*\)$')

@hook.command(hook='w')
@hook.command
def wiki(query):
    print query
    q = search_url % (urllib.quote(query, safe=''))
    print q
    x = etree.parse(q)

    ns = '{http://opensearch.org/searchsuggest2}'
    items = x.findall(ns + 'Section/' + ns + 'Item')

    def extract(item):
        return [item.find(ns + x).text for x in 
                            ('Text', 'Description', 'Url')]
    
    title, desc, url = extract(items[0])

    if 'may refer to' in desc:
        title, desc, url = extract(items[1])
    
    title = paren_re.sub('', title)

    if title.lower() not in desc.lower():
        desc = title + desc
 
    desc = re.sub('\s+', ' ', desc).strip() #remove excess spaces

    if len(desc) > 300:
        desc = desc[:300] + '...'

    return '%s -- %s' % (desc, url)
