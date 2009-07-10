"""
twitter.py: written by Scaevolus 2009
retrieves most recent tweets
"""

import re
import urllib2
from lxml import etree

from util import hook


def unescape_xml(string):
    # unescape the 5 chars that might be escaped in xml

    # gratuitously functional
    # return reduce(lambda x, y: x.replace(*y), (string,
    #     zip('&gt; &lt; &apos; &quote; &amp'.split(), '> < \' " &'.split()))

    # boring, normal
    return string.replace('&gt;', '>').replace('&lt;', '<').replace('&apos;',
                    "'").replace('&quote;', '"').replace('&amp;', '&')


@hook.command
def twitter(inp):
    ".twitter <user>/<id> - gets last tweet from <user>/gets tweet <id>"
    inp = inp.strip()
    if not inp:
        return twitter.__doc__

    getting_id = False
    if re.match('^\d+$', inp):
        getting_id = True
        url = 'http://twitter.com/statuses/show/%s.xml' % inp
    elif re.match('^\w{,15}$', inp):
        url = 'http://twitter.com/statuses/user_timeline/%s.xml?count=1' % inp
    else:
        return 'error: invalid username'

    try:
        xml = urllib2.urlopen(url).read()
    except urllib2.HTTPError, e:
        errors = {400 : 'bad request (ratelimited?)',
                401: 'tweet is private',
                404: 'invalid user/id',
                500: 'twitter is broken',
                502: 'twitter is down ("getting upgraded")',
                503: 'twitter is overloaded (lol, RoR)'}
        if e.code == 404:
            return 'error: invalid ' + ['username', 'tweet id'][getting_id]
        if e.code in errors:
            return 'error: ' + errors[e.code]
        return 'error: unknown'

    tweet = etree.fromstring(xml)

    if not getting_id:
        tweet = tweet.find('status')
        if tweet is None:
            return 'error: user has no tweets'

    return unescape_xml(': '.join(tweet.find(x).text.replace('\n','') for x in
        'created_at user/screen_name text'.split()))
