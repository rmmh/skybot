from util import hook, http


@hook.command
def stock(inp):
    '''.stock <symbol> -- gets stock information'''

    url = ('http://query.yahooapis.com/v1/public/yql?format=json&'
           'env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys')

    parsed = http.get_json(url, q='select * from yahoo.finance.quotes '
                           'where symbol in ("%s")' % inp)  # heh, SQLI

    quote = parsed['query']['results']['quote']

    # if we dont get a company name back, the symbol doesn't match a company
    if quote['Change'] is None:
        return "unknown ticker symbol %s" % inp

    price = float(quote['LastTradePriceOnly'])
    change = float(quote['Change'])
    if quote['Open'] and quote['Bid'] and quote['Ask']:
        open_price = float(quote['Open'])
        bid = float(quote['Bid'])
        ask = float(quote['Ask'])
        if price < bid:
            price = bid
        elif price > ask:
            price = ask
        change = price - open_price
        quote['LastTradePriceOnly'] = "%.2f" % price
        quote['Change'] = ("+%.2f" % change) if change >= 0 else change

    if change < 0:
        quote['color'] = "5"
    else:
        quote['color'] = "3"

    quote['PercentChange'] = 100 * change / (price - change)

    ret = "%(Name)s - %(LastTradePriceOnly)s "                   \
          "\x03%(color)s%(Change)s (%(PercentChange).2f%%)\x03 "        \
          "Day Range: %(DaysRange)s " \
          "MCAP: %(MarketCapitalization)s" % quote

    return ret
