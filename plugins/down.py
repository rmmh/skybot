import urlparse

from util import hook, http


@hook.command
def down(inp):
    '''.down <url> -- checks to see if the website is down'''

    urlp = urlparse.urlparse(inp, 'http')
    
    if urlp.scheme not in ('http', 'https'):
        return inp + " is not a valid HTTP URL"
        
    inp = "%s://%s" % (urlp.scheme, urlp.netloc)
    
    # http://mail.python.org/pipermail/python-list/2006-December/589854.html
    try:
        http.get(inp, get_method='HEAD')
        return inp + ' seems to be up'
    except http.URLError:
        return inp + ' seems to be down'
