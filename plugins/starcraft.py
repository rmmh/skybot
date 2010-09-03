import json

from util import hook, http


@hook.command
def starcraft(inp):
    ".starcraft <character name> <battle.net id> [region] - returns Starcraft II statistics"
    inp = inp.split()
    charname = inp[0]
    bnetid = inp[1]
    if len(inp) == 3:
        region = inp[2]
    else:
        region = 'us'
    
    page = http.get_json('http://sc2ranks.com/api/char/%s/%s!%s.json' % (region, charname, bnetid))
    if "error" in page:
        return "No character with that Battle.net ID or name found in that region."
    
    found_val = False
    player_name = page["name"]
    
    for item in page["teams"]:
        if item["bracket"] == 1:
            found_val = True
            player_league = item["league"]
            player_division = item["division"]
            player_rank = item["division_rank"]
            player_wins = item["wins"]
            player_losses = item["losses"]
            
    if found_val == False:
        return "Player %s has not played any 1v1 games or is not ranked." % \
         (player_name)
    
    return "%s is rank %s in %s league and %s with %s wins and %s losses." % \
     (player_name, player_rank, player_league, player_division, player_wins, player_losses)

    

