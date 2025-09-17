
from util import http, hook


@hook.command()
def crypto(inp, say=None):
    fsym = inp.split(" ")[0].upper()
    price_response = http.get_json(
        "https://min-api.cryptocompare.com/data/pricemultifull", fsyms=fsym, tsyms="USD"
    )

    if price_response.get("Response") == "Error":
        return "Error: " + price_response.get(
            "Message", "An API Error Has Occured. https://min-api.cryptocompare.com/"
        )

    if not price_response["DISPLAY"].get(fsym):
        return "Error: Unable to lookup pricing for {}".format(fsym)

    values = price_response["DISPLAY"][fsym]["USD"]

    say(
        (
            "USD/{FROMSYMBOL}: \x0307{PRICE}\x0f - High: \x0307{HIGHDAY}\x0f "
            "- Low: \x0307{LOWDAY}\x0f - Volume: {VOLUMEDAY}"
            " ({VOLUMEDAYTO}) - Total Supply: {SUPPLY} - MktCap: {MKTCAP}"
        ).format(**values)
    )
