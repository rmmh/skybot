from util import hook, http
from urllib2 import HTTPError


@hook.command
def stock(inp):
    '''.stock <symbol> [info] -- retrieves a weeks worth of stats for given symbol. Optionally displays information about the company.'''

    arguments = inp.split(' ')

    symbol = arguments[0].upper()

    try:
        fundamentals = http.get_json(
            'https://api.robinhood.com/fundamentals/{}/'.format(symbol))
        quote = http.get_json(
            'https://api.robinhood.com/quotes/{}/'.format(symbol))
    except HTTPError:
        return '{} is not a valid stock symbol.'.format(symbol)

    if fundamentals['open'] is None or quote['ask_price'] is None:
        return 'unknown ticker symbol %s' % inp

    if len(arguments) > 1 and arguments[1] == 'info':
        return fundamentals['description']

    # Manually "calculate" change since API does not provide it
    price = float(quote['last_trade_price'])
    change = price - float(quote['adjusted_previous_close'])

    response = {
        'change': change,
        'percent_change': 100 * change / (price - change),
        'market_cap': float(fundamentals['market_cap']),
        'symbol': quote['symbol'],
        'price': price,
        'color': '\x035' if change < 0 else '\x033',
        'high': float(fundamentals['high']),
        'low': float(fundamentals['low']),
        'pe_ratio': float(fundamentals['pe_ratio']),
        'average_volume': float(fundamentals['average_volume']),
    }

    return "[{symbol}] ${price:,.2f} {color}{change:,.2f} ({percent_change:,.2f}%)\x03 :: " \
        "High: ${high:,.2f} :: " \
        "Low: ${low:,.2f} :: " \
        "PE: {pe_ratio:,.2f}% :: " \
        "Volume: ${average_volume:,.2f} :: " \
        "MCAP: ${market_cap:,.2f}".format(**response)
