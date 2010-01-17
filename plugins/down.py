import urllib2
import urlparse

from util import hook

@hook.command
def down(inp):
    '''.down <url> -- checks to see if the site is down'''

    if not inp:
        return down.__doc__

    if 'http://' not in inp:
        inp = 'http://' + inp

    inp = 'http://' + urlparse.urlparse(inp).netloc

    # http://mail.python.org/pipermail/python-list/2006-December/589854.html
    try:
        request = urllib2.Request(inp)
        request.get_method = lambda: "HEAD"
        http_file = urllib2.urlopen(request)
        head = http_file.read()
        return inp + ' seems to be up'
    except urllib2.URLError:
        return inp + ' seems to be down'
