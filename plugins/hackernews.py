from util import http, hook


@hook.regex(r'(?i)https://(?:www\.)?news\.ycombinator\.com\S*id=(\d+)')
def hackernews(match):
    base_api = 'https://hacker-news.firebaseio.com/v0/item/'
    entry = http.get_json(base_api + match.group(1) + ".json")

    if entry['type'] == "story":
        return "{title} by {by} with {score} points and {descendants} comments ({url})".format(**entry)

    if entry['type'] == "comment":
        return '"{text}" -- {by}'.format(**entry)

