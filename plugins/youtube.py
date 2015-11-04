import re
import time

from util import hook, http


youtube_re = (r'(?:youtube.*?(?:v=|/v/)|youtu\.be/|yooouuutuuube.*?id=)'
              '([-_a-z0-9]+)', re.I)

base_url = 'https://www.googleapis.com/youtube/v3/'
info_url = base_url + 'videos?part=snippet,contentDetails,statistics'
search_api_url = base_url + 'search'
video_url = 'http://youtube.com/watch?v=%s'


def get_video_description(vid_id, api_key):
    j = http.get_json(info_url, id=vid_id, key=api_key)

    if not j['pageInfo']['totalResults']:
        return

    j = j['items'][0]

    duration = j['contentDetails']['duration'].replace('PT', '').lower()

    published = time.strptime(j['snippet']['publishedAt'],
                              "%Y-%m-%dT%H:%M:%S.000Z")
    published = time.strftime("%Y.%m.%d", published)

    views = group_int_digits(j['statistics']['viewCount'], ',')
    likes = j['statistics'].get('likeCount', 0)
    dislikes = j['statistics'].get('dislikeCount', 0)
    
    out = (u'\x02{snippet[title]}\x02 - length \x02{duration}\x02 - '
           u'{likes}\u2191{dislikes}\u2193 - '
           u'\x02{views}\x02 views - '
           u'\x02{snippet[channelTitle]}\x02 on \x02{published}\x02'
          ).format(duration=duration, likes=likes, dislikes=dislikes, views=views, published=published, **j)

    # TODO: figure out how to detect NSFW videos

    return out


def group_int_digits(number, delimiter=' ', grouping=3):
    base = str(number).strip()
    builder = []
    while base:
        builder.append(base[-grouping:])
        base = base[:-grouping]
    builder.reverse()
    return delimiter.join(builder)


@hook.api_key('google')
@hook.regex(*youtube_re)
def youtube_url(match, api_key=None):
    return get_video_description(match.group(1), api_key)


@hook.api_key('google')
@hook.command('yt')
@hook.command('y')
@hook.command
def youtube(inp, api_key=None):
    '.youtube <query> -- returns the first YouTube search result for <query>'

    params = {
        'key': api_key,
        'fields': 'items(id,snippet(channelId,title))',
        'part': 'snippet',
        'type': 'video',
        'q': inp
    }

    j = http.get_json(search_api_url, **params)

    if 'error' in j:
        return 'error while performing the search'

    results = j.get("items")

    if not results:
        return 'no results found'

    vid_id = j['items'][0]['id']['videoId']

    return get_video_description(vid_id, api_key) + " - " + video_url % vid_id
