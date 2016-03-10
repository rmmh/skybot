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

    for valid_edition in range(len(card["editions"])):
        if card["editions"][valid_edition]["multiverse_id"] != 0 :
            break
    
    #symbols = {'{T}' : u'\u27F3' , '{S}' : u'\u2744' , '{Q}' : u'\u21BA', '\n' : ' ' , '{' : '', '}' : ''} 
    symbols = {
    #    '{0}'   : u'\u24EA' , 
    #    '{1}'   : u'\u2460' , 
    #    '{2}'   : u'\u2461' , 
    #    '{3}'   : u'\u2462' , 
    #    '{4}'   : u'\u2463' , 
    #    '{5}'   : u'\u2464' , 
    #    '{6}'   : u'\u2465' , 
    #    '{7}'   : u'\u2466' , 
    #    '{8}'   : u'\u2467' , 
    #    '{9}'   : u'\u2468' , 
    #    '{10}'   : u'\u2469' , 
    #    '{11}'   : u'\u246A' , 
    #    '{12}'   : u'\u246B' , 
    #    '{13}'   : u'\u246C' , 
    #    '{14}'   : u'\u246D' , 
    #    '{15}'   : u'\u246E' , 
    #    '{16}'   : u'\u246F' , 
    #    '{17}'   : u'\u2470' , 
    #    '{18}'   : u'\u2471' , 
    #    '{19}'   : u'\u2472' , 
    #    '{20}'   : u'\u2473' , 
        '{0}'   : '0' , 
        '{1}'   : '1' , 
        '{2}'   : '2' , 
        '{3}'   : '3' , 
        '{4}'   : '4' , 
        '{5}'   : '5' , 
        '{6}'   : '6' , 
        '{7}'   : '7' , 
        '{8}'   : '8' , 
        '{9}'   : '9' , 
        '{10}'   : '10' , 
        '{11}'   : '11' , 
        '{12}'   : '12' , 
        '{13}'   : '13' , 
        '{14}'   : '14' , 
        '{15}'   : '15' , 
        '{16}'   : '16' , 
        '{17}'   : '17' , 
        '{18}'   : '18' , 
        '{19}'   : '19' , 
        '{20}'   : '20' , 
        '{T}'   : u'\u27F3' , 
        '{S}'   : u'\u2744' , 
        '{Q}'   : u'\u21BA' , 
        '{C}'   : u'\u27E1' , 
        '{W}'   : 'W' , 
        '{U}'   : 'U' , 
        '{B}'   : 'B' , 
        '{R}'   : 'R' , 
        '{G}'   : 'G' , 
        '{W/P}' : u'\u03A6' , 
        '{U/P}' : u'\u03A6' , 
        '{B/P}' : u'\u03A6' , 
        '{R/P}' : u'\u03A6' , 
        '{G/P}' : u'\u03A6' ,
        '\n' : ' ' ,
    }
    results = {
        "name": card["name"],
        "types": ", ".join(t.capitalize() for t in card["types"]),
        "cost": card["cost"],
        "text": card["text"],
        "multiverse_id": card["editions"][valid_edition]["multiverse_id"],
    }
    for str,rep in symbols.items():
        new_text = results["text"].replace(str,rep)
        new_cost = results["cost"].replace(str,rep)
        results["text"] = new_text
        results["cost"] = new_cost

    return u"{name} - {types} - {cost} | {text} | http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid={multiverse_id}".format(**results)


if __name__ == "__main__":
    print card_search("Black Lotus")
    print mtg("Black Lotus")
