"""
twitter.py: written by Scaevolus 2009
retrieves most recent tweets
"""

import re
import random
import urllib2
from lxml import etree
from time import strptime, strftime

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
    ".twitter <user>/<user> <n>/<id> - gets last/<n>th tweet from <user>/gets tweet <id>"
    inp = inp.strip()
    if not inp:
        return twitter.__doc__


    url = 'http://twitter.com'
    getting_nth = False
    getting_id = False
    searching_hashtag = False
    if re.match(r'^\d+$', inp):
        getting_id = True
        url += '/statuses/show/%s.xml' % inp
    elif re.match(r'^\w{1,15}$', inp):
        url += '/statuses/user_timeline/%s.xml?count=1' % inp
    elif re.match(r'^\w{1,15}\s+\d+$', inp):
        getting_nth = True
        name, num = inp.split()
        if int(num) > 3200:
            return 'error: only supports up to the 3200th tweet'
        url += '/statuses/user_timeline/%s.xml?count=1&page=%s' % (name, num)
    elif re.match(r'^#\w{1,15}$', inp):
        url = 'http://search.twitter.com/search.atom?q=%23' + inp[1:]
        searching_hashtag = True
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

    if searching_hashtag:
        ns = '{http://www.w3.org/2005/Atom}'
        id = random.choice(tweet.findall(ns + 'entry/' + ns + 'id')).text
        id = id[id.rfind(':') + 1:]
        return twitter(id)

    if not getting_id:
        tweet = tweet.find('status')
        if tweet is None:
            if getting_nth:
                return 'error: user does not have that many tweets'
            else:
                return 'error: user has no tweets'

    time = strftime('%Y-%m-%d %H:%M:%S', 
             strptime(tweet.find('created_at').text,
               '%a %b %d %H:%M:%S +0000 %Y'))
    screen_name = tweet.find('user/screen_name').text
    text = unescape_xml(tweet.find('text').text.replace('\n', ''))

    return "%s %s: %s" % (time, screen_name, text)
