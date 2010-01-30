import urllib
import re

from util import hook


re_lineends = re.compile(r'[\r\n]*')


@hook.command
def py(inp):
    ".py <prog> -- executes python code <prog>"

    if not inp:
        return py.__doc__

    res = urllib.urlopen("http://eval.appspot.com/eval?statement=%s" %
                          urllib.quote(inp, safe='')).readlines()
    if len(res) == 0:
        return
    res[0] = re_lineends.split(res[0])[0]
    if not res[0] == 'Traceback (most recent call last):':
        return res[0]
    else:
        return res[-1]
