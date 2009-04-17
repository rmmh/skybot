"""
twitter.py: written by Scaevolus 2009
retrieves most recent tweets
"""

import urllib
from lxml import etree

import hook

@hook.command
def twitter(bot, input):
    ".twitter <user> - gets most recent tweet from <user>"
    if not input.inp.strip():
        return twitter.__doc__

    url = "http://twitter.com/statuses/user_timeline/%s.xml?count=1" \
            % urllib.quote(input.inp)
    try:
        tweet = etree.parse(url)
    except IOError:
        return 'RoR: XTREME scalability (twitter gave an error)'

    if tweet.find('error') is not None:
        return "can't find that username"
    
    tweet = tweet.find('status')
    bot.say(': '.join(tweet.find(x).text for x in 
        'created_at user/screen_name text'.split()))
