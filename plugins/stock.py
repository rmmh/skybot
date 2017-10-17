from util import hook, http
import csv

def get_stock_info(symbol):
    # The YQL API is broken.. Some of the YQL web nodes work, others don't.

    csv_url = 'http://finance.yahoo.com/d/quotes.csv'

    columns = {
        'Name': 'n',
        'Ask': 'a',
        'Bid': 'b',
        'Open': 'o',
        'DaysRange': 'm',
        'LastTradePriceOnly': 'l1',
        'Change': 'c1',
        'MarketCapitalization': 'j1',
    }

    result = http.get(csv_url, s=symbol, f=''.join(columns.values()))

    reader = csv.reader(result.split("\n"), delimiter=',')
    line = reader.next()
    quote = dict(zip(columns.keys(), line))

    return quote

@hook.command
def stock(inp):
    '''.stock <symbol> -- gets stock information'''

    quote = get_stock_info(inp)

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
