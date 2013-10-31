from util import hook, http

@hook.command
def gex(inp):
    '''.gex <from currency> <to currency> <amount> -- returns Google Exchange result'''
    ###############################################################
    ### rate exchange from : https://rate-exchange.appspot.com/ ###
    ###############################################################
    main_url = 'https://rate-exchange.appspot.com/currency?'
    query = inp.split(' ', 2)
    query_url = main_url+'from='+query[0]+'&to='+query[1]
    h = http.get_json(query_url, q=query[2])
    cur_from = h["from"]
    cur_to = h["to"]
    rate = h["rate"]
    amount = h["v"]
    if not cur_to:
        return "could not convert " + inp

    res = '%s %s to %s = %s (rate: %s)' % (cur_from, query[2], cur_to, amount, rate)
    return res
