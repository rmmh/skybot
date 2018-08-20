#!/usr/bin/env python

import re

from util import hook, http


def human_price(x):
    if x > 1e9:
        return '{:,.2f}B'.format(x / 1e9)
    elif x > 1e6:
        return '{:,.2f}M'.format(x / 1e6)
    return '{:,.0f}'.format(x)


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
    except http.HTTPError:
        return '{} is not a valid stock symbol.'.format(symbol)

    if fundamentals['open'] is None or quote['ask_price'] is None:
        return 'unknown ticker symbol %s' % inp

    if len(arguments) > 1 and arguments[1] == 'info':
        return fundamentals['description']

    # Manually "calculate" change since API does not provide it
    price = float(quote.get('last_extended_hours_trade_price') or quote['last_trade_price'])
    change = price - float(quote['adjusted_previous_close'])

    # Extract name as Upper Case Corp Name from description.
    name = ''
    m = re.match(r'^([A-Z]\S* )*', fundamentals['description'])
    if m:
        name = m.group(0)

    def maybe(name, key, fmt=human_price):
        if fundamentals.get(key):
            return ' | {0}: {1}'.format(name, fmt(float(fundamentals[key])))
        return ''

    response = {
        'name': name,
        'change': change,
        'percent_change': 100 * change / (price - change),
        'symbol': quote['symbol'],
        'price': price,
        'color': '05' if change < 0 else '03',
        'high': float(fundamentals['high']),
        'low': float(fundamentals['low']),
        'average_volume': maybe('Volume', 'average_volume'),
        'market_cap': maybe('MCAP', 'market_cap'),
        'pe_ratio': maybe('P/E', 'pe_ratio', fmt='{:.2f}'.format),
    }

    return ("{name}({symbol}) ${price:,.2f} \x03{color}{change:,.2f} ({percent_change:,.2f}%)\x03 | "
            "Day Range: ${low:,.2f} - ${high:,.2f}"
            "{pe_ratio}{average_volume}{market_cap}").format(**response)

if __name__ == '__main__':
    import sys
    for arg in sys.argv[1:]:
        print stock(arg)
