import urllib2

from util import hook

@hook.command
def down(inp):
    '''.down <url> -- checks to see if the site is down'''
    inp = inp.strip()

    if not inp:
        return down.__doc__

    if 'http://' not in inp:
        inp = 'http://' + inp

    # http://mail.python.org/pipermail/python-list/2006-December/589854.html
    try:
        request = urllib2.Request(inp)
        request.get_method = lambda: "HEAD"
        http_file = urllib2.urlopen(request, timeout=10)
        head = http_file.headers
        return 'it seems to be up'
    except urllib2.URLError:
        return 'it seems to be down'
