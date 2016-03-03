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

    try:
        card = card_search(inp)[0]
    except IndexError:
        return "Card not found."

    results = {
        "name": card["name"],
        "types": ", ".join(t.capitalize() for t in card["types"]),
        "cost": card["cost"],
        "text": card["text"].rstrip(),
        "multiverse_id": card["editions"][0]["multiverse_id"],
    }
    
    return "{name} - {cost} | {types} - {text} | http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid={multiverse_id}".format(**results)


if __name__ == "__main__":
    print card_search("black lotus")

