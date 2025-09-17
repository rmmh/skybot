
import json
import re

from util import http, hook


MOVIE_SEARCH_URL = "https://www.rottentomatoes.com/api/private/v2.0/search/"
MOVIE_PAGE_URL = "https://www.rottentomatoes.com/m/%s"


def get_rottentomatoes_data(movie_id):
    if movie_id.startswith("/m/"):
        movie_id = movie_id[3:]

    document = http.get_html(MOVIE_PAGE_URL % movie_id)

    # JSON for the page is stored in the script with ID 'jsonLdSchema'
    # So we can pull that for tons of information.
    ld_schema_element = document.xpath("//script[@type='application/ld+json']")[0]
    ld_schema = json.loads(ld_schema_element.text_content())

    scripts = "\n".join(document.xpath("//script/text()"))
    score_info = json.loads(re.search(r"scoreInfo = (.*);", scripts).group(1))[
        "tomatometerAllCritics"
    ]

    try:
        audience_score = document.xpath(
            '//span[contains(@class, "audience") and contains(@class, "rating")]/text()'
        )[0].strip()
    except IndexError:
        audience_score = ""

    return {
        "title": ld_schema["name"],
        "critics_score": score_info["score"],
        "audience_score": audience_score,
        "fresh": score_info["freshCount"],
        "rotten": score_info["rottenCount"],
        "url": MOVIE_PAGE_URL % movie_id,
    }


def search_rottentomatoes(inp):
    results = http.get_json(MOVIE_SEARCH_URL, limit=1, q=inp)

    if not results or not results["movieCount"]:
        return None

    return results["movies"][0]["url"]


@hook.command("rt")
@hook.command
def rottentomatoes(inp):
    ".rt <title> -- gets ratings for <title> from Rotten Tomatoes"

    movie_id = search_rottentomatoes(inp)

    if not movie_id:
        return "no results"

    movie = get_rottentomatoes_data(movie_id)

    return (
        "{title} - critics: \x02{critics_score}%\x02 "
        "({fresh}\u2191{rotten}\u2193) "
        "audience: \x02{audience_score}\x02 - {url}"
    ).format(**movie)
