from urllib import quote_plus
from urllib2 import urlopen
from util import hook

@hook.command('fy')
@hook.command
def fuckyeah(inp):
    ".fy <phrase> -- links to a fuck yeah noun image"
    
    host = 'http://fuckyeahnouns.com/'
    path = 'images/' + quote_plus(inp)
    timeout = 3
    
    # headers contain 'Cache-Control: public; max-age=36000' when a legitimate
    # image is found, 'Cache-Control: public; max-age=30' otherwise
    
    try:
        for header in urlopen(host + path, None, timeout).info().headers:
            if header.strip() == 'Cache-Control: public; max-age=36000':
                return host + path
        return "didn't find shit"
    except:
        return "didn't find shit"
