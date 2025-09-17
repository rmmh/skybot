
# metacritic.com scraper

import re
from urllib.error import HTTPError

from util import hook, http

SCORE_CLASSES = {
    "\x0304": ["negative", "bad", "score_terrible", "score_unfavorable"],
    "\x0308": ["mixed", "forty", "fifty", "score_mixed"],
    "\x0303": [
        "sixtyone",
        "seventyfive",
        "good",
        "positive",
        "score_favorable",
        "score_outstanding",
    ],
}


def get_score_color(element_classes):
    for (color, score_classes) in SCORE_CLASSES.items():
        for score_class in score_classes:
            if score_class in element_classes:
                return color


@hook.command("mc")
def metacritic(inp):
    ".mc [all|movie|tv|album|x360|ps3|pc|gba|ds|3ds|wii|vita|wiiu|xone|ps4] <title> -- gets rating for" " <title> from metacritic on the specified medium"

    # if the results suck, it's metacritic's fault

    args = inp.strip()

    game_platforms = (
        "x360",
        "ps3",
        "pc",
        "gba",
        "ds",
        "3ds",
        "wii",
        "vita",
        "wiiu",
        "xone",
        "ps4",
    )
    all_platforms = game_platforms + ("all", "movie", "tv", "album")

    try:
        plat, title = args.split(" ", 1)
        if plat not in all_platforms:
            # raise the ValueError so that the except block catches it
            # in this case, or in the case of the .split above raising the
            # ValueError, we want the same thing to happen
            raise ValueError
    except ValueError:
        plat = "all"
        title = args

    cat = "game" if plat in game_platforms else plat

    title_safe = http.quote_plus(title)

    url = "http://www.metacritic.com/search/%s/%s/results" % (cat, title_safe)

    print(url)

    try:
        doc = http.get_html(url)
    except HTTPError:
        return "error fetching results"

    # get the proper result element we want to pull data from

    result = None

    if not doc.find_class("query_results"):
        return "no results found"

    # if they specified an invalid search term, the input box will be empty
    if doc.get_element_by_id("primary_search_box").value == "":
        return "invalid search term"

    if plat not in game_platforms:
        # for [all] results, or non-game platforms, get the first result
        result = doc.find_class("result first_result")[0]

        # find the platform, if it exists
        result_type = result.find_class("result_type")
        if result_type:

            # if the result_type div has a platform div, get that one
            platform_div = result_type[0].find_class("platform")
            if platform_div:
                plat = platform_div[0].text_content().strip()
            else:
                # otherwise, use the result_type text_content
                plat = result_type[0].text_content().strip()

    else:
        # for games, we want to pull the first result with the correct
        # platform
        results = doc.find_class("result")
        for res in results:
            result_plat = res.find_class("platform")[0].text_content().strip()
            if result_plat == plat.upper():
                result = res
                break

    if not result:
        return "no results found"

    # get the name, release date, and score from the result
    product_title_element = result.find_class("product_title")[0]

    review = {
        "platform": plat.upper(),
        "title": product_title_element.text_content().strip(),
        "link": "http://metacritic.com"
        + product_title_element.find("a").attrib["href"],
    }

    try:
        score_element = result.find_class("metascore_w")[0]

        review["score"] = score_element.text_content().strip()

        review["score_color"] = get_score_color(score_element.classes)
    except IndexError:
        review["score"] = "unknown"

    return "[{platform}] {title} - \x02{score_color}{score}\x0f - {link}".format(
        **review
    )
