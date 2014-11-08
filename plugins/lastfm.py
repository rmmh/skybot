'''
The Last.fm API key is retrieved from the bot config file.
'''

from util import hook, http


api_url = "http://ws.audioscrobbler.com/2.0/?format=json"


@hook.api_key('lastfm')
@hook.command(autohelp=False)
def lastfm(inp, chan='', nick='', reply=None, api_key=None, db=None):
    ".lastfm <username> [dontsave] | @<nick> -- gets current or last played " \
        "track from lastfm"

    db.execute(
        "create table if not exists "
        "lastfm(chan, nick, user, primary key(chan, nick))"
    )

    if inp[0:1] == '@':
        nick = inp[1:].strip()
        user = None
        dontsave = True
    else:
        user = inp

        dontsave = user.endswith(" dontsave")
        if dontsave:
            user = user[:-9].strip().lower()

    if not user:
        user = db.execute(
            "select user from lastfm where chan=? and nick=lower(?)",
            (chan, nick)).fetchone()
        if not user:
            return lastfm.__doc__
        user = user[0]

    response = http.get_json(api_url, method="user.getrecenttracks",
                             api_key=api_key, user=user, limit=1)

    if 'error' in response:
        return "error: %s" % response["message"]

    if not "track" in response["recenttracks"] or \
            len(response["recenttracks"]["track"]) == 0:
        return "no recent tracks for user \x02%s\x0F found" % user

    tracks = response["recenttracks"]["track"]

    if type(tracks) == list:
        # if the user is listening to something, the tracks entry is a list
        # the first item is the current track
        track = tracks[0]
        status = 'current track'
    elif type(tracks) == dict:
        # otherwise, they aren't listening to anything right now, and
        # the tracks entry is a dict representing the most recent track
        track = tracks
        status = 'last track'
    else:
        return "error parsing track listing"

    title = track["name"]
    album = track["album"]["#text"]
    artist = track["artist"]["#text"]

    ret = "\x02%s\x0F's %s - \x02%s\x0f" % (user, status, title)
    if artist:
        ret += " by \x02%s\x0f" % artist
    if album:
        ret += " on \x02%s\x0f" % album

    reply(ret)

    if inp and not dontsave:
        db.execute(
            "insert or replace into lastfm(chan, nick, user) "
            "values (?, ?, ?)", (chan, nick.lower(), inp))
        db.commit()
