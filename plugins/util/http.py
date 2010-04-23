# convenience wrapper for urllib2 & friends

import json
import urllib
import urllib2
import urlparse

from urllib import quote, quote_plus
from urllib2 import HTTPError, URLError

import lxml

user_agent = 'Skybot/1.0 http://bitbucket.org/Scaevolus/skybot'

ua_firefox = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.6) ' \
    'Gecko/20070725 Firefox/2.0.0.6'
ua_internetexplorer = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'


def get(*args, **kwargs):
    return open(*args, **kwargs).read()


def get_html(*args, **kwargs):
    return lxml.html.fromstring(get(*args, **kwargs))


def get_xml(*args, **kwargs):
    return lxml.etree.fromstring(get(*args, **kwargs))


def get_json(*args, **kwargs):
    return json.loads(get(*args, **kwargs))


def open(url, query_params={}, user_agent=user_agent, post_data=None, 
         get_method=None, **kwargs):
    query_params.update(kwargs)

    url = prepare_url(url, query_params)

    request = urllib2.Request(url, post_data)

    if get_method is not None:
        request.get_method = lambda: get_method

    request.add_header('User-Agent', user_agent)
    return urllib2.build_opener().open(request)

    
def prepare_url(url, queries):
    if queries:
        scheme, netloc, path, query, fragment = urlparse.urlsplit(url)

        query = dict(urlparse.parse_qsl(query))
        query.update(queries)
        query = urllib.urlencode(dict((to_utf8(key), to_utf8(value))
                                  for key, value in query.iteritems()))

        url = urlparse.urlunsplit((scheme, netloc, path, query, fragment))

    return url


def to_utf8(s):
    if isinstance(s, str):
        return s
    else:
        return s.encode('utf8', 'ignore')
