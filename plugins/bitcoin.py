
from util import http, hook


@hook.command(autohelp=False)
def bitcoin(inp, say=None):
    ".bitcoin -- gets current exchange rate for bitcoins from Bitstamp"
    data = http.get_json("https://www.bitstamp.net/api/ticker/")
    say(
        "USD/BTC: \x0307${:,.2f}\x0f - High: \x0307${:,.2f}\x0f -"
        " Low: \x0307${:,.2f}\x0f - Volume: {:,.2f} BTC".format(
            float(data["last"]),
            float(data["high"]),
            float(data["low"]),
            float(data["volume"]),
        )
    )


@hook.command(autohelp=False)
def ethereum(inp, say=None):
    ".ethereum -- gets current exchange rate for ethereum from Bitstamp"
    data = http.get_json("https://www.bitstamp.net/api/v2/ticker/ethusd")
    say(
        "USD/ETH: \x0307${:,.2f}\x0f - High: \x0307${:,.2f}\x0f -"
        " Low: \x0307${:,.2f}\x0f - Volume: {:,.2f} ETH".format(
            float(data["last"]),
            float(data["high"]),
            float(data["low"]),
            float(data["volume"]),
        )
    )
