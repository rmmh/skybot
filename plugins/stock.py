import random

from util import hook, http


@hook.command
def stock(inp):
    '''.stock <symbol> -- returns information on a stock symbol'''

    url = 'http://www.google.com/ig/api?stock=%s'

    parsed = http.get_xml(url, stock=inp)

    if len(parsed) != 1:
        raise IOError('Error using the stock API')

    # Stuff the results in a dict for easy string formatting
    results = {}
    for elm in parsed.find("finance"):
        results[elm.tag] = elm.get("data")

    # if we dont get a company name back, the symbol doesnt match a company
    if results['company'] == "":
        return "Unknown ticker symbol %s" % inp

    if results['change'][1] == '-':
        results['color'] = "5"
    else:
        results['color'] = "3"

    format_str = "%(company)s - %(last)s %(currency)s "                   \
                  "\x03%(color)s%(change)s (%(perc_change)s)\x03 "        \
                  "as of %(trade_timestamp)s (delayed %(delay)s minutes)"

    return format_str % results
