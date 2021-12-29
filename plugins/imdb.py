# IMDb lookup plugin by Ghetto Wizard (2011).
from __future__ import unicode_literals

import re

from util import hook, http


# http://www.omdbapi.com/apikey.aspx
@hook.api_key("omdbapi")
@hook.command
def imdb(inp, api_key=None):
    """.imdb <movie> -- gets information about <movie> from IMDb"""

    if not api_key:
        return None

    content = http.get_json("https://www.omdbapi.com/", t=inp, apikey=api_key)

    if content["Response"] == "Movie Not Found":
        return "movie not found"
    elif content["Response"] == "True":
        content["URL"] = "http://www.imdb.com/title/%(imdbID)s" % content

        out = "\x02%(Title)s\x02 (%(Year)s) (%(Genre)s): %(Plot)s"
        if content["Runtime"] != "N/A":
            out += " \x02%(Runtime)s\x02."
        if content["imdbRating"] != "N/A" and content["imdbVotes"] != "N/A":
            out += " \x02%(imdbRating)s/10\x02 with \x02%(imdbVotes)s\x02 votes."
        out += " %(URL)s"
        return out % content
    else:
        return "unknown error"

@hook.api_key("omdbapi")
@hook.command()
def tng(inp, api_key=None, ep=None):
    ep = re.match(r"s[0-9]?[0-9]e[0-9]?[0-9]", inp, re.I)
    if ep is not None:
        season, episode = ep[0].lower().split('e')
        print(season.strip('s'), episode)
        response = http.get_json("http://www.omdbapi.com/?apikey={}&i=tt0092455&Season={}&Episode={}".format(api_key, season.strip("s"), episode))
        title = response["Title"]
        released = response["Released"]
        summary = response["Plot"]
        r_season = response["Season"]
        r_episode = response["Episode"]
        return "\x02Series\x02: TNG | \x02Title\x02: {} | \x02Summary\x02: {} | \x02Season\x02: {} - \x02Episode\x02: {} | \x02Air Date\x02: {}".format(title, summary, r_season, r_episode, released)
    # else:
    #     print(inp.lower().replace(" ", "+"))
    #     response = http.get_json("http://www.omdbapi.com/?t={}&type=episode&apikey={}".format(inp.lower().replace(" ", "+"),api_key))
    #     print("http://www.omdbapi.com/?s=%{}&type=episode&apikey={}".format(inp.lower().replace(" ", "+"),api_key))
    #     print(response)

@hook.api_key("omdbapi")
@hook.command()
def ds9(inp, api_key=None, ep=None):
    ep = re.match(r"s[0-9]?[0-9]e[0-9]?[0-9]", inp, re.I)
    if ep is not None:
        season, episode = ep[0].lower().split('e')
        print(season.strip('s'), episode)
        response = http.get_json("http://www.omdbapi.com/?apikey={}&i=tt0106145&Season={}&Episode={}".format(api_key, season.strip("s"), episode))
        title = response["Title"]
        released = response["Released"]
        summary = response["Plot"]
        r_season = response["Season"]
        r_episode = response["Episode"]
        return "\x02Series\x02: DS9 | \x02Title\x02: {} | \x02Summary\x02: {} | \x02Season\x02: {} - \x02Episode\x02: {} | \x02Air Date\x02: {}".format(title, summary, r_season, r_episode, released)