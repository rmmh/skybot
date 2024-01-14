from __future__ import unicode_literals

import random
import re
from time import strptime, strftime
from urllib.parse import quote

from util import hook, http

@hook.api_key("mastodon")
@hook.command
def mastodon(inp, api_key=None):
    ".mastodon <user>/<user> <n>/<id>/#<search>/#<search> <n> -- " "get <user>'s last/<n>th status/get status <id>/do <search>/get <n>th <search> result"
    # [TODO] add support for other domains? 
    if not isinstance(api_key, dict) or any(
        # [TODO] need to review if needed any more
        key not in api_key
        for key in ("consumer", "consumer_secret", "access", "access_secret")
    ):
        return "error: api keys not set"

    getting_id = False
    doing_search = False
    index_specified = False

    if re.match(r"^\d+$", inp):
        getting_id = True
        #https://mastodon.example/api/v1/statuses/
        request_url = "https://mastodon.social/api/v1/statuses/?id=%s" % inp
    else:
        try:
            inp, index = re.split("\s+", inp, 1)
            index = int(index)
            index_specified = True
        except ValueError:
            index = 0
        if index < 0:
            index = 0
        if index >= 20:
            return "error: only supports up to the 20th status"
        #https://mastodon.social/api/v2/search?q=boots&resolve=true&limit=5
        if re.match(r"^#", inp):
            doing_search = True
            request_url = "https://mastodon.social/api/v2/search?q=%s&resolve=true&limit=1" % quote(
                inp
            )
        else: #searching for users is the same as searching for statuses in mastodon
            request_url = (
                "https://mastodon.social/api/v2/search?q=%s&resolve=true&limit=1" 
                % inp
            )

    try:
        status = http.get_json(
            request_url, oauth=True, oauth_keys=api_key, status_mode="extended"
        )
    except http.HTTPError as e:
        errors = {
            400: "bad request (ratelimited?)",
            401: "unauthorized",
            403: "forbidden",
            404: "invalid user/id",
            500: "mastodon is broken",
            502: 'mastodon is down ("getting upgraded")',
            503: "mastodon is overloaded (lol, RoR)",
            410: "mastodon shut off api v1.",
        }
        if e.code == 404:
            return "error: invalid " + ["username", "status id"][getting_id]
        if e.code in errors:
            return "error: " + errors[e.code]
        return "error: unknown %s" % e.code

    if doing_search:
        try:
            status = status["statuses"]
            if not index_specified:
                index = random.randint(0, len(status) - 1)
        except KeyError:
            return "error: no results"

    if not getting_id:
        try:
            status = status[index]
        except IndexError:
            return "error: not that many statuses found"

    if "reblog" in status:
        rb = status["reblog"]
        rb_text = http.unescape(rb["content"]).replace("\n", " ")
        text = "Boost @%s %s" % (rb["account"]["username"], rb_text)
    else:
        # [TODO] in mastodon the content of a post is full html, this will need to be removed
        text = http.unescape(status["content"]).replace("\n", " ")
        # [TODO] there is currently no known url shortner, and therefore no needed url expansion
        #for url in status.get('entities', {}).get('urls', []):
            #new_text = text.replace(url['url'], url['expanded_url'])
            #if len(new_text) < 350:
            #    text = new_text
        for url in status.get('media_attachments', status.get('entities', {})).get('media', []):
            if url['type'] in ('video', 'image', 'gifv', 'audio'):
                try:
                    media_url = url['url']
                except KeyError:
                    continue
            # [TODO] evaluate if this is actually needed at all
            if url['url'] in text:
                new_text = text.replace(url['url'], media_url)
            else:
                new_text = text + ' ' + media_url
            if len(new_text) < 400:
                text = new_text
    account = status["account"]["username"]
    time = status["created_at"]

    time = strftime("%Y-%m-%d %H:%M:%S", strptime(time, "%a %b %d %H:%M:%S +0000 %Y"))

    return "%s \x02%s\x02: %s" % (time, account, text)
# [TODO] this only works for domains federated with mastodon.social
@hook.api_key("mastodon")
@hook.regex(r"https?://\w\.\w/@[a-zA-Z0-9_](@[a-zA-Z0-9_]+\.\w+)?/(?P<id>\d+)")
def show_tweet(match, api_key=None):
    return mastodon(match.group("id"), api_key)
