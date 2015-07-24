import re
import urlparse

from util import http, hook


base_api = 'https://hacker-news.firebaseio.com/v0/item/'


def get_by_id(id):
    url = base_api + id + ".json?print=pretty"

    try:
        return http.get_json(url)
    except ValueError:
        return None


@hook.regex(r'(?i)https://(?:www\.)?news\.ycombinator\.com(?:/.+)?')
def hackernews(match):
    parsed = urlparse.urlparse(match.group())
    id = urlparse.parse_qs(parsed.query)['id'][0]
    entry = get_by_id(id)

    if not entry:
        return

    if entry['type'] == "story":
        return "{title} by {by} with {score} points and {descendants} comments ({url})".format(**entry)

    if entry['type'] == "comment":
        return '"{text}" -- {by}'.format(**entry)

