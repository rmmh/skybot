from __future__ import unicode_literals
import random

from util import hook, http

FRINKIAC_SEARCH_URL = "https://frinkiac.com/api/search"
FRINKIAC_CAPTIONS_URL = "https://frinkiac.com/api/caption"
FRINKIAC_SITE_URL = "https://frinkiac.com/caption"


def get_frames(query):
    try:
        content = http.get_json(FRINKIAC_SEARCH_URL, q=query)
    except IOError:
        return None

    return content


def get_caption(episode, timestamp):
    try:
        content = http.get_json(FRINKIAC_CAPTIONS_URL, e=episode, t=timestamp)
    except IOError:
        return None

    return content


def find_mention(subtitles, query):
    for subtitle in subtitles:
        content = subtitle['Content'].lower()
        if query.lower() in content:
            return subtitle

    return None


@hook.command('simpsons')
@hook.command()
def frinkiac(inp):
    """.frinkiac <query> -- Get a frame from The Simpsons."""
    frames = get_frames(inp)

    if frames is None or len(frames) == 0:
        return 'no results'

    frame = frames[random.randint(0, len(frames)-1)]

    episode = frame['Episode']
    timestamp = frame['Timestamp']

    caption = get_caption(episode, timestamp)
    url = '{}/{}/{}'.format(FRINKIAC_SITE_URL, episode, timestamp)

    subtitles = caption['Subtitles']
    if len(subtitles) == 0:
        return '{} - {}'.format(episode, url)

    subtitle = find_mention(subtitles, inp)

    if subtitle is None:
        subtitle = subtitles[random.randint(0, len(subtitles)-1)]

    return '{} - {} {} '.format(subtitle['Content'], episode, url)


@hook.regex(r"(?i)https://frinkiac\.com/(caption|img)/S(\d{2})E(\d{2})/(\d+)")
def frinkiac_lookup(match):
    season_episode = 'S{}E{}'.format(match.group(2), match.group(3))
    timestamp = match.group(4)

    caption = get_caption(season_episode, timestamp)

    episode = caption['Episode']
    title = episode['Title']

    return '{} - {}'.format(season_episode, title)
