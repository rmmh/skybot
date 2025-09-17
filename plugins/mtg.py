from builtins import range
from util import hook, http
import random


def card_search(name):
    matching_cards = http.get_json(
        "https://api.magicthegathering.io/v1/cards", name=name
    )
    for card in matching_cards["cards"]:
        if card["name"].lower() == name.lower():
            return card
    return random.choice(matching_cards["cards"])


@hook.command
def mtg(inp, say=None):
    """.mtg <name> - Searches for Magic the Gathering card given <name>"""

    try:
        card = card_search(inp)
    except IndexError:
        return "Card not found."
    symbols = {
        "{0}": "0",
        "{1}": "1",
        "{2}": "2",
        "{3}": "3",
        "{4}": "4",
        "{5}": "5",
        "{6}": "6",
        "{7}": "7",
        "{8}": "8",
        "{9}": "9",
        "{10}": "10",
        "{11}": "11",
        "{12}": "12",
        "{13}": "13",
        "{14}": "14",
        "{15}": "15",
        "{16}": "16",
        "{17}": "17",
        "{18}": "18",
        "{19}": "19",
        "{20}": "20",
        "{T}": "\u27F3",
        "{S}": "\u2744",
        "{Q}": "\u21BA",
        "{C}": "\u27E1",
        "{W}": "W",
        "{U}": "U",
        "{B}": "B",
        "{R}": "R",
        "{G}": "G",
        "{W/P}": "\u03D5",
        "{U/P}": "\u03D5",
        "{B/P}": "\u03D5",
        "{R/P}": "\u03D5",
        "{G/P}": "\u03D5",
        "{X}": "X",
        "\n": " ",
    }
    results = {
        "name": card["name"],
        "type": card["type"],
        "cost": card.get("manaCost", ""),
        "text": card.get("text", ""),
        "power": card.get("power"),
        "toughness": card.get("toughness"),
        "loyalty": card.get("loyalty"),
        "multiverseid": card.get("multiverseid"),
    }

    for fragment, rep in symbols.items():
        results["text"] = results["text"].replace(fragment, rep)
        results["cost"] = results["cost"].replace(fragment, rep)

    template = ["{name} -"]
    template.append("{type}")
    template.append("- {cost} |")
    if results["loyalty"]:
        template.append("{loyalty} Loyalty |")
    if results["power"]:
        template.append("{power}/{toughness} |")
    template.append(
        "{text} | http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid={multiverseid}"
    )

    return " ".join(template).format(**results)


if __name__ == "__main__":
    print(card_search("Black Lotus"))
    print(mtg("Black Lotus"))
