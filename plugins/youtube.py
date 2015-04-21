import re
import time

from util import hook, http


youtube_re = (r'(?:youtube.*?(?:v=|/v/)|youtu\.be/|yooouuutuuube.*?id=)'
              '([-_a-z0-9]+)', re.I)

base_url = 'http://gdata.youtube.com/feeds/api/'
url = base_url + 'videos/%s?v=2&alt=jsonc'
search_api_url = 'https://www.googleapis.com/youtube/v3/search'
video_url = 'http://youtube.com/watch?v=%s'


def get_video_description(vid_id):
    j = http.get_json(url % vid_id)

    if j.get('error'):
        return

    j = j['data']

    out = '\x02%s\x02' % j['title']

    if not j.get('duration'):
        return out

    out += ' - length \x02'
    length = j['duration']
    if length / 3600:  # > 1 hour
        out += '%dh ' % (length / 3600)
    if length / 60:
        out += '%dm ' % (length / 60 % 60)
    out += "%ds\x02" % (length % 60)

    if 'rating' in j:
        out += ' - rated \x02%.2f/5.0\x02 (%d)' % (j['rating'],
                                                   j['ratingCount'])

    if 'viewCount' in j:
        out += ' - \x02%s\x02 views' % group_int_digits(j['viewCount'])

    upload_time = time.strptime(j['uploaded'], "%Y-%m-%dT%H:%M:%S.000Z")
    out += ' - \x02%s\x02 on \x02%s\x02' % (
                        j['uploader'], time.strftime("%Y.%m.%d", upload_time))

    if 'contentRating' in j:
        out += ' - \x034NSFW\x02'

    return out


def group_int_digits(number, delimiter=' ', grouping=3):
    base = str(number).strip()
    builder = []
    while base:
        builder.append(base[-grouping:])
        base = base[:-grouping]
    builder.reverse()
    return delimiter.join(builder)


@hook.regex(*youtube_re)
def youtube_url(match):
    return get_video_description(match.group(1))


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

    return get_video_description(vid_id) + " - " + video_url % vid_id
