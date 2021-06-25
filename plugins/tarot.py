"""
🔮 Spooky fortunes and assistance for witches
"""
from future.standard_library import hooks

with hooks():
    from urllib.error import HTTPError
    from urllib.parse import quote

from util import hook, http

@hook.command
def tarot(inp):
    ".tarot <cardname> -- finds a card by name"
    search = quote(inp)

    try:
        card = http.get_json(f"https://tarot-api.com/find/{search}")
    except HTTPError:
        return "The spirits are displeased."

    return card["name"] + ": " + ", ".join(card["keywords"])

@hook.command(autohelp=False)
def fortune(inp):
    """
    .fortune -- returns one random card and it's fortune
    """

    try:
        cards = http.get_json("https://tarot-api.com/draw/1")
    except HTTPError:
        return "The spirits are displeased."

    card = cards[0]

    return card["name"] + ": " + ", ".join(card["keywords"])

