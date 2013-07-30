import random
import re
from time import strptime, strftime
from xml.sax.saxutils import unescape

from util import hook, http


@hook.api_key('twitter')
@hook.command
def twitter(inp, api_key=None):
    ".twitter <user>/<user> <n>/<id> -- " \
    "get <user>'s last/<n>th tweet/get tweet <id>"

    if not isinstance(api_key, dict) or any(key not in api_key for key in
            ('consumer', 'consumer_secret', 'access', 'access_secret')):
        return "error: api keys not set"

    getting_id = False

    if re.match(r'^\d+$', inp):
        getting_id = True
        request_url = "https://api.twitter.com/1.1/statuses/show.json?id=%s" % inp
    else:
        try:
            inp, index = re.split('\s+', inp, 1)
            index = int(index)
        except ValueError:
            index = 0
        if index < 0:
            index = 0
        if index >= 20:
            return 'error: only supports up to the 20th tweet'
        request_url = "https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=%s" % inp

    try:
        tweet = http.get_json(request_url, oauth=True, oauth_keys=api_key)
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

    if not getting_id:
        try:
            tweet = tweet[index]
        except IndexError:
            return 'error: user does not have that many tweets'

    text = tweet["text"]
    screen_name = tweet["user"]["screen_name"]
    time = tweet["created_at"]

    text = unescape(text, {'&apos;': "'", "&quot;": '"'})
    time = strftime('%Y-%m-%d %H:%M:%S', strptime(time, '%a %b %d %H:%M:%S +0000 %Y'))

    return "%s %s: %s" % (time, screen_name, text)
