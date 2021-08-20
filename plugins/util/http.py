from future.standard_library import hooks

from lxml import etree, html

import binascii
import collections
import hmac
import json
import random
import time

from hashlib import sha1

from builtins import str
from builtins import range

try:
    from http.cookiejar import CookieJar
except:
    from future.backports.http.cookiejar import CookieJar

with hooks():
    import urllib.request, urllib.parse, urllib.error

    from urllib.parse import (
        quote,
        unquote,
        urlencode,
        urlparse,
        parse_qsl,
        quote_plus as _quote_plus,
    )
    from urllib.error import HTTPError, URLError


ua_skybot = "Skybot/1.0 https://github.com/rmmh/skybot"
ua_firefox = (
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.6) "
    "Gecko/20070725 Firefox/2.0.0.6"
)
ua_internetexplorer = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)"


def get_cookie_jar():
    if not hasattr(get_cookie_jar, "memo"):
        get_cookie_jar.memo = CookieJar()

    return get_cookie_jar.memo


def clear_expired_cookies():
    get_cookie_jar().clear_expired_cookies()


def get(*args, **kwargs):
    return open(*args, **kwargs).read().decode("utf-8")


def get_html(*args, **kwargs):
    return html.fromstring(open(*args, **kwargs).read())


def get_xml(*args, **kwargs):
    return etree.fromstring(open(*args, **kwargs).read())


def get_json(*args, **kwargs):
    return json.loads(open(*args, **kwargs).read())


def open(
    url,
    query_params=None,
    post_data=None,
    json_data=None,
    get_method=None,
    cookies=False,
    oauth=False,
    oauth_keys=None,
    headers=None,
    **kwargs
):
    if query_params is None:
        query_params = {}

    query_params.update(kwargs)

    url = prepare_url(url, query_params)

    if post_data and isinstance(post_data, collections.Mapping):
        post_data = urllib.parse.urlencode(post_data)
        post_data = post_data.encode("UTF-8")

    if json_data and isinstance(json_data, dict):
        post_data = json.dumps(json_data).encode("utf-8")

    request = urllib.request.Request(url, post_data)

    if json_data:
        request.add_header("Content-Type", "application/json")

    if get_method is not None:
        request.get_method = lambda: get_method

    if headers is not None:
        for header_key, header_value in headers.items():
            request.add_header(header_key, header_value)

    if "User-Agent" not in request.headers:
        request.add_header("User-Agent", ua_skybot)

    if oauth:
        nonce = oauth_nonce()
        timestamp = oauth_timestamp()
        api_url, req_data = url.split("?")
        unsigned_request = oauth_unsigned_request(
            nonce, timestamp, req_data, oauth_keys["consumer"], oauth_keys["access"]
        )

        signature = oauth_sign_request(
            "GET",
            api_url,
            req_data,
            unsigned_request,
            oauth_keys["consumer_secret"],
            oauth_keys["access_secret"],
        )

        header = oauth_build_header(
            nonce, signature, timestamp, oauth_keys["consumer"], oauth_keys["access"]
        )
        request.add_header("Authorization", header)

    if cookies:
        opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(get_cookie_jar())
        )
    else:
        opener = urllib.request.build_opener()

    return opener.open(request)


def prepare_url(url, queries):
    if queries:
        scheme, netloc, path, query, fragment = urllib.parse.urlsplit(str(url))

        query = dict(urllib.parse.parse_qsl(query))
        query.update(queries)
        query = urllib.parse.urlencode(
            dict((to_utf8(key), to_utf8(value)) for key, value in query.items())
        )

        url = urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))

    return url


def to_utf8(s):
    if isinstance(s, str):
        return s.encode("utf8", "ignore")
    else:
        return str(s)


def quote_plus(s):
    return _quote_plus(to_utf8(s))


def oauth_nonce():
    return "".join([str(random.randint(0, 9)) for i in range(8)])


def oauth_timestamp():
    return str(int(time.time()))


def oauth_unsigned_request(nonce, timestamp, req, consumer, token):
    d = {
        "oauth_consumer_key": consumer,
        "oauth_nonce": nonce,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": timestamp,
        "oauth_token": token,
        "oauth_version": "1.0",
    }

    d.update(urllib.parse.parse_qsl(req))

    request_items = d.items()

    # TODO: Remove this when Python 2 is no longer supported.
    # some of the fields are actual string and others are
    # a wrapper of str for the python 3 migration.
    # Convert them all so that they sort correctly.
    request_items = [(str(k), str(v)) for k, v in request_items]

    return quote(urllib.parse.urlencode(sorted(request_items, key=lambda key: key[0])))


def oauth_build_header(nonce, signature, timestamp, consumer, token):
    d = {
        "oauth_consumer_key": consumer,
        "oauth_nonce": nonce,
        "oauth_signature": signature,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": timestamp,
        "oauth_token": token,
        "oauth_version": "1.0",
    }

    header = "OAuth "

    for x in sorted(d, key=lambda key: key[0]):
        header += x + '="' + d[x] + '", '

    return header[:-1]


def oauth_sign_request(
    method, url, params, unsigned_request, consumer_secret, token_secret
):
    key = consumer_secret + "&" + token_secret
    key = key.encode("utf-8", "replace")

    base = method + "&" + quote(url, "") + "&" + unsigned_request
    base = base.encode("utf-8", "replace")

    hash = hmac.new(key, base, sha1)

    signature = quote(binascii.b2a_base64(hash.digest())[:-1])

    return signature


def unescape(s):
    if not s.strip():
        return s
    return html.fromstring(s).text_content()
