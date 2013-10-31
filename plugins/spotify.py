import locale

from util import hook, http

locale.setlocale(locale.LC_ALL, '')

base_url = 'http://ws.spotify.com/lookup/1/.json?uri='
track_url = base_url+'spotify:track:%s'

def get_track_description(track_id):
    trackid = track_id.split('/')[-1]
    track_url_full = track_url % (trackid)
    rj = http.get_json(track_url_full)

    track_name = str(rj['track']['name'])
    artist_name = str(rj['track']['artists'][0]['name'])
    length = rj['track']['length']
    album = str(rj['track']['album']['name'])
    track_no = str(rj['track']['track-number'])

    out = '%s by %s - length ' % (track_name, artist_name)
    if length / 3600:
        out += '%dh ' % (length/3600)
    if length / 60:
        out += '%dm '  % (length/60 % 60)
    out += '%ds '  % (length/60)
    out += '-- [Track No. %s in %s]' % (track_no, album)
    return out

@hook.regex(r'(?i)http[s]://open\.spotify\.com/track/([A-Za-z0-9]+)|http[s]://play\.spotify\.com/track/([A-Za-z0-9]+)')
def spotify_url(match):
    return get_track_description(match.group())
