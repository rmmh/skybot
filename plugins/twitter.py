"""
twitter.py: written by Scaevolus 2009
retrieves most recent tweets
"""

import urllib
from lxml import etree

import hook


def unescape_xml(string):
    # unescape the 5 chars that might be escaped in xml

    # gratuitously functional
    # return reduce(lambda x, y: x.replace(*y), (string, 
    #     zip('&gt; &lt; &apos; &quote; &amp'.split(), '> < \' " &'.split()))

    # boring, normal
    return string.replace('&gt;', '>').replace('&lt;', '<'). \
            replace('&apos;', "'").replace('&quote;', '"').replace('&amp;', '&')

@hook.command
def twitter(input):
    ".twitter <user> - gets most recent tweet from <user>"
    if not input.strip():
        return twitter.__doc__

    url = "http://twitter.com/statuses/user_timeline/%s.xml?count=1" \
            % urllib.quote(input)
    try:
        tweet = etree.parse(url)
    except IOError:
        return 'error'

    if tweet.find('error') is not None:
        return "can't find that username"

    tweet = tweet.find('status')
    return unescape_xml(': '.join(tweet.find(x).text for x in
        'created_at user/screen_name text'.split()))
