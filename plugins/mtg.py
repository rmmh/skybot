import urllib

from util import hook, http


def card_search(query):
    base_url = "https://api.deckbrew.com"
    name = urllib.quote_plus(query)
    search_url = base_url + "/mtg/cards?name=" + name

    return http.get_json(search_url)


@hook.command
def mtg(inp, say=None):
    '''.mtg <name> - Searches for Magic the Gathering card given <name>
    '''

    card = card_search(inp)[0]

    if not card:
        return "Card not found."

    results = {
        "name": card["name"],
        "colors": ", ".join([c.capitalize() for c in card.get("colors", ("None",))]),
        "types": ", ".join(t.capitalize() for t in card["types"]),
        "cost": card["cost"],
        "text": card["text"],
        "formats": ", ".join([f.capitalize() for f in card["formats"]]),
        "price": "$"+card["editions"][0]["price"].get("average", "0"),
        "url": card["editions"][0]["store_url"],
    }

    return "{name} | {text} | Cost: {cost} | Colors: {colors} | Types: {types} | Formats: {formats} | {price} | {url}".format(**results)


if __name__ == "__main__":
    print card_search("black lotus")

