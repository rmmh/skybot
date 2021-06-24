"""
🔮 Spooky fortunes and assistance for witches
"""
from util import hook, http

@hook.command
def tarot(inp):
    ".tarot <cardname> -- finds a card by name"

    try:
        card = http.get_json(
            "https://tarot-api.com/find/{search}".format(
                search=inp
            )
        )
    except http.HTTPError:
        return "the spirits are displeased."


    return card["name"] + ": " + ", ".join(card["keywords"])


def fortune():
    ".fortune -- returns one random card and it's fortune"

    try:
        cards = http.get_json("https://tarot-api.com/draw/1")
    except http.HTTPError:
        return "the spirits are displeased."

    card = cards[0]

    return card["name"] + ": " + ", ".join(card["keywords"])