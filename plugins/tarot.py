"""
🔮 Spooky fortunes and assistance for witches
"""
from util import hook, http
from urllib.error import HTTPError

@hook.command
def tarot(inp):
    ".tarot <cardname> -- finds a card by name"

    try:
        card = http.get_json("https://tarot-api.com/find/{search}", search=inp)
    except HTTPError:
        return "the spirits are displeased."


    return card["name"] + ": " + ", ".join(card["keywords"])

@hook.command(autohelp=False)
def fortune(inp):
    """
    .fortune -- returns one random card and it's fortune
    """

    try:
        cards = http.get_json("https://tarot-api.com/draw/1")
    except HTTPError:
        return "the spirits are displeased."

    card = cards[0]

    return card["name"] + ": " + ", ".join(card["keywords"])
