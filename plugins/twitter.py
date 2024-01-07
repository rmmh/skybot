from __future__ import unicode_literals

import math
import random
import re
import string
from time import strptime, strftime
from urllib.parse import quote

from util import hook, http


b36_alphabet = string.digits + string.ascii_lowercase

def base36(x):
    frac, x = math.modf(x)
    r = []
    x = int(x)
    f = []
    # fractional part translated from V8 DoubleToRadixCString
    delta = max(0.5 * (math.nextafter(x, x+1) - x), math.nextafter(0, 1))
    while frac >= delta:
        frac *= 36
        delta *= 36
        d = int(frac)
        f.append(d)
        frac -= d
        if frac > .5 or frac == .5 and d & 1:
            if frac + delta > 1:
                i = len(f)
                while True:
                    i -= 1
                    if i == -1:
                        x += 1
                        break
                    if f[i] + 1 < 36:
                        f[i] += 1
                        break
    f = [b36_alphabet[x] for x in f]
    while x:
        x, rem = divmod(x, 36)
        r.append(b36_alphabet[rem])

    if f:
        return ''.join(r[::-1]) + '.' + ''.join(f)
    else:
        return ''.join(r[::-1])


@hook.command
def twitter(inp):
    ".twitter <id> -- get tweet <id>"

    if re.match(r"^\d+$", inp):
        x = int(inp)/1e15*math.pi
        token = re.sub(r'0+|\.', '', base36(x))
        request_url = "https://cdn.syndication.twimg.com/tweet-result?lang=en"
    else:
        return 'error: can only get tweets by id'

    try:
        tweet = http.get_json(request_url, id=inp, token=token)
    except http.HTTPError as e:
        errors = {
            400: "bad request (ratelimited?)",
            401: "unauthorized",
            403: "forbidden",
            404: "invalid user/id",
            500: "twitter is broken",
            502: 'twitter is down ("getting upgraded")',
            503: "twitter is overloaded (lol, RoR)",
            410: "twitter shut off api v1.",
        }
        if e.code == 404:
            return "error: invalid tweet id"
        if e.code in errors:
            return "error: " + errors[e.code]
        return "error: unknown %s" % e.code

    if "retweeted_status" in tweet:
        rt = tweet["retweeted_status"]
        rt_text = http.unescape(rt["full_text"]).replace("\n", " ")
        text = "RT @%s %s" % (rt["user"]["screen_name"], rt_text)
    else:
        text = http.unescape(tweet["text"]).replace("\n", " ")
        for url in tweet.get('entities', {}).get('urls', []):
            new_text = text.replace(url['url'], url['expanded_url'])
            if len(new_text) < 350:
                text = new_text
        for url in tweet.get('mediaDetails', []) + tweet.get('entities', {}).get('media', []):
            if url.get('type') in ('video', 'animated_gif'):
                try:
                    media_url = max(url['video_info']['variants'], key=lambda x: x.get('bitrate', 0))['url']
                except KeyError:
                    continue
            elif 'media_url_https' in url:
                media_url = url['media_url_https']
            else:
                continue
            if url['url'] in text:
                new_text = text.replace(url['url'], media_url)
            else:
                new_text = text + ' ' + media_url
            if len(new_text) < 400:
                text = new_text
    screen_name = tweet["user"]["screen_name"]
    time = tweet["created_at"]

    time = strftime("%Y-%m-%d %H:%M:%S", strptime(time, "%Y-%m-%dT%H:%M:%S.000Z"))

    return "%s \x02%s\x02: %s" % (time, screen_name, text)


@hook.regex(r"https?://((mobile\.|fx|vx)?twitter|x).com/(#!/)?([_0-9a-zA-Z]+)/status/(?P<id>\d+)")
def show_tweet(match):
    return twitter(match.group("id"))
