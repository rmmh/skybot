from builtins import str
import urllib.parse

from util import hook, http


@hook.command
def down(inp):
    """.down <url> -- checks to see if the website is down"""

    # urlparse follows RFC closely, so we have to check for schema existence and prepend empty schema if necessary
    if not inp.startswith("//") and "://" not in inp:
        inp = "//" + inp

    urlp = urllib.parse.urlparse(str(inp), "http")

    if urlp.scheme not in ("http", "https"):
        return inp + " is not a valid HTTP URL"

    inp = "%s://%s" % (urlp.scheme, urlp.netloc)

    # http://mail.python.org/pipermail/python-list/2006-December/589854.html
    try:
        http.get(inp, get_method="HEAD")
        return inp + " seems to be up"
    except http.URLError as error:
        return inp + " seems to be down. Error: %s" % error.reason
