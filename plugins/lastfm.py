from util import hook, http

api_key = ""

api_url = "http://ws.audioscrobbler.com/2.0/?format=json"

@hook.command
def lastfm(inp, nick='', say=None):
    if inp:
        user = inp
    else:
        user = nick

    response = http.get_json(api_url, method="user.getrecenttracks",
                             api_key=api_key, user=user, limit=1)

    if 'error' in response:
        if inp:  # specified a user name
            return "error: %s" % response["message"]
        else:
            return "your nick is not a LastFM account. try '.lastfm username'."

    track = response["recenttracks"]["track"]
    title = track["name"]
    album = track["album"]["#text"]
    artist = track["artist"]["#text"]

    ret = "\x02%s\x0F's last track - \x02%s\x0f" % (user, title)
    if artist:
        ret += " by \x02%s\x0f" % artist
    if album:
        ret += " on \x02%s\x0f" % album

    say(ret)
