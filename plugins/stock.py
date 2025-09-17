#!/usr/bin/env python3

from past.utils import old_div
import re

from util import hook, http


def human_price(x):
    if x > 1e9:
        return "{:,.2f}B".format(old_div(x, 1e9))
    elif x > 1e6:
        return "{:,.2f}M".format(old_div(x, 1e6))
    return "{:,.0f}".format(x)


@hook.api_key("iexcloud")
@hook.command
def stock(inp, api_key=None):
    """.stock <symbol> [info] -- retrieves a weeks worth of stats for given symbol. Optionally displays information about the company."""

    if not api_key:
        return "missing api key"

    arguments = inp.split(" ")

    symbol = arguments[0].upper()

    try:
        quote = http.get_json(
            "https://cloud.iexapis.com/stable/stock/{symbol}/quote".format(
                symbol=symbol
            ),
            token=api_key,
        )
    except http.HTTPError:
        return "{} is not a valid stock symbol.".format(symbol)

    if (
        quote["extendedPriceTime"]
        and quote["latestUpdate"] < quote["extendedPriceTime"]
    ):
        price = quote["extendedPrice"]
        change = quote["extendedChange"]
    elif quote["latestSource"] == "Close" and quote.get("iexRealtimePrice"):
        # NASDAQ stocks don't have extendedPrice anymore :(
        price = quote["iexRealtimePrice"]
        change = price - quote["previousClose"]
    else:
        price = quote["latestPrice"]
        change = quote["change"]

    def maybe(name, key, fmt=human_price):
        if quote.get(key):
            return " | {0}: {1}".format(name, fmt(float(quote[key])))
        return ""

    response = {
        "name": quote["companyName"],
        "change": change,
        "percent_change": 100 * change / (price - change),
        "symbol": quote["symbol"],
        "price": price,
        "color": "05" if change < 0 else "03",
        "high": quote["high"],
        "low": quote["low"],
        "average_volume": maybe("Volume", "latestVolume"),
        "market_cap": maybe("MCAP", "marketCap"),
        "pe_ratio": maybe("P/E", "peRatio", fmt="{:.2f}".format),
    }

    return (
        "{name} ({symbol}) ${price:,.2f} \x03{color}{change:,.2f} ({percent_change:,.2f}%)\x03"
        + (
            " | Day Range: ${low:,.2f} - ${high:,.2f}"
            if response["high"] and response["low"]
            else ""
        )
        + "{pe_ratio}{average_volume}{market_cap}"
    ).format(**response)


if __name__ == "__main__":
    import os, sys

    for arg in sys.argv[1:]:
        print(stock(arg, api_key=os.getenv("KEY")))
