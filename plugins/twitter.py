import random
import re
from time import strptime, strftime
from util import hook, http

@hook.command
def twitter(inp, bot=None):
    ".twitter <user>/<id> -- get <user>'s last tweet/get tweet <id>"

    api_keys = {}
    api_keys['consumer'] = bot.config.get("api_keys", {}).get("twitter_consumer", None)
    api_keys['consumer_secret'] = bot.config.get("api_keys", {}).get("twitter_consumer_secret", None)
    api_keys['access'] = bot.config.get("api_keys", {}).get("twitter_access", None)
    api_keys['access_secret'] = bot.config.get("api_keys", {}).get("twitter_access_secret", None)
    
    for k in api_keys:
        if api_keys[k] is None:
            return "error: api keys not set"

    getting_id = False

    if re.match(r'^\d+$', inp):
        getting_id = True
        request_url = "https://api.twitter.com/1.1/statuses/show.json?id=%s" % inp
    else:
        request_url = "https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=%s" % inp
    
    try:
        tweet = http.get_json(request_url, oauth=True, oauth_keys=api_keys)
    except http.HTTPError, e:
        errors = {400: 'bad request (ratelimited?)',
                401: 'unauthorized',
                403: 'forbidden',
                404: 'invalid user/id',
                500: 'twitter is broken',
                502: 'twitter is down ("getting upgraded")',
                503: 'twitter is overloaded (lol, RoR)',
                410: 'twitter shut off api v1.' }
        if e.code == 404:
            return 'error: invalid ' + ['username', 'tweet id'][getting_id]
        if e.code in errors:
            return 'error: ' + errors[e.code]
        return 'error: unknown %s' % e.code

    if getting_id:
        text = tweet["text"]
        screen_name = tweet["user"]["screen_name"]
        time = tweet["created_at"]
    else:
        text = tweet[0]["text"]
        screen_name = tweet[0]["user"]["screen_name"]
        time = tweet[0]["created_at"]
    
    text = text.replace('&gt;', '>').replace('&lt;', '<').replace('&apos;',"'").replace('&quote;', '"').replace('&amp;', '&')
    time = strftime('%Y-%m-%d %H:%M:%S', strptime(time, '%a %b %d %H:%M:%S +0000 %Y'))

    return "%s %s: %s" % (time, screen_name, text)

