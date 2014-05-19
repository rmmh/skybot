# convenience wrapper for urllib2 & friends
import binascii
import cookielib
import hmac
import json
import random
import string
import time
import urllib
import urllib2
import urlparse

from hashlib import sha1
from urllib import quote, unquote, quote_plus as _quote_plus
from urllib2 import HTTPError, URLError

from lxml import etree, html


ua_skybot = 'Skybot/1.0 http://github.com/rmmh/skybot'

ua_firefox = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.6) ' \
             'Gecko/20070725 Firefox/2.0.0.6'
ua_internetexplorer = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'

jar = cookielib.CookieJar()


def get(*args, **kwargs):
    return open(*args, **kwargs).read()


def get_html(*args, **kwargs):
    return html.fromstring(get(*args, **kwargs))


def get_xml(*args, **kwargs):
    return etree.fromstring(get(*args, **kwargs))


def get_json(*args, **kwargs):
    return json.loads(get(*args, **kwargs))


def open(url, query_params=None, post_data=None,
         get_method=None, cookies=False, oauth=False, oauth_keys=None, headers=None, **kwargs):
    if query_params is None:
        query_params = {}

    query_params.update(kwargs)

    url = prepare_url(url, query_params)

    request = urllib2.Request(url, post_data)

    if get_method is not None:
        request.get_method = lambda: get_method

    if headers is not None:
        for header_key, header_value in headers.iteritems():
            request.add_header(header_key, header_value)

    if 'User-Agent' not in request.headers:
        request.add_header('User-Agent', ua_skybot)

    if oauth:
        nonce = oauth_nonce()
        timestamp = oauth_timestamp()
        api_url, req_data = string.split(url, "?")
        unsigned_request = oauth_unsigned_request(
            nonce, timestamp, req_data, oauth_keys['consumer'], oauth_keys['access'])

        signature = oauth_sign_request("GET", api_url, req_data, unsigned_request, oauth_keys[
            'consumer_secret'], oauth_keys['access_secret'])

        header = oauth_build_header(
            nonce, signature, timestamp, oauth_keys['consumer'], oauth_keys['access'])
        request.add_header('Authorization', header)

    if cookies:
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
    else:
        opener = urllib2.build_opener()
    return opener.open(request)


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
    if isinstance(s, unicode):
        return s.encode('utf8', 'ignore')
    else:
        return str(s)


def quote_plus(s):
    return _quote_plus(to_utf8(s))


def oauth_nonce():
    return ''.join([str(random.randint(0, 9)) for i in range(8)])


def oauth_timestamp():
    return str(int(time.time()))


def oauth_unsigned_request(nonce, timestamp, req, consumer, token):
    d = {'oauth_consumer_key': consumer,
         'oauth_nonce': nonce,
         'oauth_signature_method': 'HMAC-SHA1',
         'oauth_timestamp': timestamp,
         'oauth_token': token,
         'oauth_version': '1.0'}

    k, v = string.split(req, "=")
    d[k] = v

    unsigned_req = ''

    for x in sorted(d, key=lambda key: key):
        unsigned_req += x + "=" + d[x] + "&"

    unsigned_req = quote(unsigned_req[:-1])

    return unsigned_req


def oauth_build_header(nonce, signature, timestamp, consumer, token):
    d = {'oauth_consumer_key': consumer,
         'oauth_nonce': nonce,
         'oauth_signature': signature,
         'oauth_signature_method': 'HMAC-SHA1',
         'oauth_timestamp': timestamp,
         'oauth_token': token,
         'oauth_version': '1.0'}

    header = 'OAuth '

    for x in sorted(d, key=lambda key: key):
        header += x + '="' + d[x] + '", '

    return header[:-1]


def oauth_sign_request(method, url, params, unsigned_request, consumer_secret, token_secret):
    key = consumer_secret + "&" + token_secret

    base = method + "&" + quote(url, '') + "&" + unsigned_request

    hash = hmac.new(key, base, sha1)

    signature = quote(binascii.b2a_base64(hash.digest())[:-1])

    return signature


def unescape(s):
    if not s.strip():
        return s
    return html.fromstring(s).text_content()
