from __future__ import unicode_literals

from util import http, hook


API_FIELD_TRANSLATION = {
    'FROMSYMBOL': 'coin',
    'TOSYMBOL': 'currency',
    'PRICE': 'last',
    'HIGH24HOUR': 'high',
    'LOW24HOUR': 'low'
}


CURRENCY_SYMBOLS = {
    'USD': u'$',
    'CAD': u'$',
    'ETH': u'\u039E',
    'BTC': u'\u20BF',
    'RUB': u'\u20BD',
    'JPY': u'\u00A5',
    'CNY': u'\u00A5',
    'EUR': u'\u20AC',
    'AZN': u'\u20BC',
    'ILS': u'\u20AA',
    'THB': u'\u0E3F',
    'KRW': u'\u20A9',
    'KPW': u'\u20A9',
    'VND': u'\u20AB',
    'SEK': u'kr',
    'ZAR': u'R'
}


def get_coin_price(coin, price_basis):
    """
    Get the coin price against a basis price system, eg BTC to USD.

    :param coin: the cryptocurrency currency to check
    :param price_basis: the price basis to check against
    :return: a dictionary which includes the coin price, symbols,
             and other stats, or none if something doesn't exist
    :rtype: dict or none
    """
    coin = coin.upper()
    price_basis = price_basis.upper()

    response = http.get_json(
        'https://min-api.cryptocompare.com/data/pricemultifull',
        query_params={
            'fsyms': coin,
            'tsyms': price_basis
        }
    )

    if not response or 'RAW' not in response:
        return None

    raw_coin_price = response['RAW'][coin.upper()][price_basis.upper()]

    coin_price = {API_FIELD_TRANSLATION[k]: v for k, v in raw_coin_price.items() if k in API_FIELD_TRANSLATION}

    if coin_price['currency'] in CURRENCY_SYMBOLS:
        coin_price['symbol'] = CURRENCY_SYMBOLS[coin_price['currency']]
    else:
        coin_price['symbol'] = '%s ' % coin_price['currency']

    return coin_price


@hook.command(autohelp=False)
def crypto(inp):
    """
    .crypto [coin] [price-basis] -
    get the price of a given coin against an optional price basis
    """
    coin, currency = (inp.split(' ', 1) + [None] * 2)[:2]
    coin = (coin or 'BTC').upper()
    currency = (currency or 'USD').upper()

    response = get_coin_price(coin, currency)

    if response is None:
        return (
            "Conversion of {coin:s} to {currency:s} not found"
        ).format(coin=coin, currency=currency)

    return (
        u"{coin:s}/{currency:s}: \x0307{symbol:s}{last:.2f}\x0f - "
        u"High: \x0307{symbol:s}{high:.2f}\x0f - "
        u"Low: \x0307{symbol:s}{low:.2f}\x0f"
    ).format(**response)

@hook.command(autohelp=False)
def bitcoin(inp):
    """.bitcoin -- gets current exchange rate for bitcoin to USD"""
    return crypto('BTC USD')

@hook.command(autohelp=False)
def ethereum(inp):
    """.ethereum -- gets current exchange rate for ethereum to USD"""
    return crypto('ETH USD')
