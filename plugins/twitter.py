from __future__ import unicode_literals

import random
import re
from time import strptime, strftime
from urllib.parse import quote

from util import hook, http


@hook.command
def twitter(inp):
    ".twitter <id> -- get tweet <id>"

    if re.match(r"^\d+$", inp):
        request_url = "https://cdn.syndication.twimg.com/tweet-result?id=%s&lang=en" % inp
    else:
        return 'error: can only get tweets by id'

    try:
        tweet = http.get_json(request_url)
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

    print(tweet)

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
            print(url)
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


@hook.regex(r"https?://(mobile\.)?twitter.com/(#!/)?([_0-9a-zA-Z]+)/status/(?P<id>\d+)")
def show_tweet(match):
    return twitter(match.group("id"))
