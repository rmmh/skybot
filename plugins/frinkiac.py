from __future__ import unicode_literals

from util import hook, http

MORBOTRON_URL = "https://morbotron.com"
FRINKIAC_URL = "https://frinkiac.com"
MASTEROFALLSCIENCE_URL = "https://masterofallscience.com"

SEARCH_ENDPOINT = "/api/search"
CAPTIONS_ENDPOINT = "/api/caption"
LINK_URL = "/caption"


def get_frames(site_root, query):
    try:
        url = site_root + SEARCH_ENDPOINT
        content = http.get_json(url, q=query)
    except IOError:
        return None

    return content


def get_caption(site_root, episode, timestamp):
    try:
        url = site_root + CAPTIONS_ENDPOINT
        content = http.get_json(url, e=episode, t=timestamp)
    except IOError:
        return None

    return content


def get_response(site_root, input):
    frames = get_frames(site_root, input)

    if frames is None or len(frames) == 0:
        return 'no results'

    frame = frames[0]

    episode = frame['Episode']
    timestamp = frame['Timestamp']

    caption = get_caption(site_root, episode, timestamp)
    url = '{}/{}/{}'.format(site_root + LINK_URL, episode, timestamp)

    subtitles = caption['Subtitles']
    if len(subtitles) == 0:
        return '{} - {}'.format(episode, url)

    subtitle = ' '.join(s['Content'] for s in subtitles)

    return '{} - {} {} '.format(subtitle, episode, url)


@hook.command('simpsons')
@hook.command()
def frinkiac(inp):
    """.frinkiac <query> -- Get a frame from The Simpsons."""
    return get_response(FRINKIAC_URL, inp)


@hook.command('futurama')
@hook.command()
def morbotron(inp):
    """.morbotron <query> -- Get a frame from Futurama."""
    return get_response(MORBOTRON_URL, inp)


@hook.command('morty')
@hook.command('rick')
@hook.command()
def rickandmorty(inp):
    """.rickandmorty <query> -- Get a frame from Rick and Morty."""
    return get_response(MASTEROFALLSCIENCE_URL, inp)


@hook.regex(r"(?i)https://(frinkiac|morbotron|masterofallscience)\.com"
            r"/(caption|img)/S(\d{2})E(\d{2})/(\d+)")
def lookup(match):
    domain = match.group(1)

    season_episode = 'S{}E{}'.format(match.group(3), match.group(4))
    timestamp = match.group(5)

    urls = {
        'frinkiac': FRINKIAC_URL,
        'morbotron': MORBOTRON_URL,
        'masterofallscience': MASTEROFALLSCIENCE_URL
    }

    site_root = urls[domain]
    caption = get_caption(site_root, season_episode, timestamp)

    episode = caption['Episode']
    episode_key = episode['Key']
    title = episode['Title']

    subtitles = caption['Subtitles']
    if len(subtitles) == 0:
        return '{} - {}'.format(episode_key, title)

    subtitle = ' '.join(s['Content'] for s in subtitles)

    return '{} - {}'.format(subtitle, episode_key)
