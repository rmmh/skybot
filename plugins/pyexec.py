import urllib
import re

re_lineends = re.compile(r'[\r\n]*')

#command
def py(input):
    res = urllib.urlopen("http://eval.appspot.com/eval?statement=%s" %
                          urllib.quote(input.strip(),safe='')).readlines()
    if len(res) == 0:
        return
    res[0] = re_lineends.split(res[0])[0]
    if not res[0] == 'Traceback (most recent call last):':
        return res[0]
    else:
        return res[-1]
