from __future__ import unicode_literals

import random

from util import hook, http


def api_get(query, key, is_image=None, num=1):
    url = (
        "https://www.googleapis.com/customsearch/v1?cx=007629729846476161907:ud5nlxktgcw"
        "&fields=items(title,link,snippet)&safe=off&nfpr=1"
        + ("&searchType=image" if is_image else "")
    )
    return http.get_json(url, key=key, q=query, num=num)


@hook.api_key("google")
@hook.command("can i get a picture of")
@hook.command("can you grab me a picture of")
@hook.command("give me a print out of")
@hook.command
def gis(inp, api_key=None):
    """.gis <term> -- finds an image using google images (safesearch off)"""

    parsed = api_get(inp, api_key, is_image=True, num=10)
    if "items" not in parsed:
        return "no images found"
    return random.choice(parsed["items"])["link"]


@hook.api_key("google")
@hook.command("g")
@hook.command
def google(inp, api_key=None):
    """.g/.google <query> -- returns first google search result"""

    parsed = api_get(inp, api_key)
    if "items" not in parsed:
        return "no results found"

    out = '{link} -- \x02{title}\x02: "{snippet}"'.format(**parsed["items"][0])
    out = " ".join(out.split())

    if len(out) > 300:
        out = out[: out.rfind(" ")] + '..."'

    return out
