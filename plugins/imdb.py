# IMDb lookup plugin by Ghetto Wizard (2011).

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
