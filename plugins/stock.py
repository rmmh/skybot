from util import hook, http
from urllib2 import HTTPError


@hook.command
def stock(inp):
    symbol = inp.split(' ')[0].upper()

    try:
        fundamentals = http.get_json('https://api.robinhood.com/fundamentals/{}/'.format(symbol))
        quote = http.get_json('https://api.robinhood.com/quotes/{}/'.format(symbol))
    except HTTPError:
        return '{} is not a valid stock symbol.'.format(symbol)

    if fundamentals['open'] is None or quote['ask_price'] is None:
        return 'unknown ticker symbol %s' % inp

    if inp.split(' ')[1] == 'info':
        return fundamentals['description']

    # Manually "calculate" change since API does not provide it
    price = float(quote['last_trade_price'])
    change = float(quote['last_trade_price']) - float(quote['adjusted_previous_close'])

    # Can come back as null
    dividend_yield = float(fundamentals['dividend_yield']) if fundamentals['dividend_yield'] else 0

    response = {
        'change': '{:,.2f}'.format(change) if change >= 0 else change,
        'percent_change': '{:.2f}'.format(100 * change / (price - change)),
        'market_cap': '{:,.2f}'.format(float(fundamentals['market_cap'])),
        'dividend_yield': '{:,.2f}'.format(dividend_yield),
        'symbol': quote['symbol'],
        'price': '{:,.2f}'.format(price),
        'color': '\x035' if change < 0 else '\x033'
    }

    return "[{symbol}] ${price} {color}{change} ({percent_change}%)\x03 :: Dividend Yield: ${dividend_yield} " \
           ":: MCAP: ${market_cap}".format(**response)
