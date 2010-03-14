from util import hook
from lxml import etree
import urllib


@hook.command
def bam(inp):
    ".bam [basic|magic|pepsi|jprdy] <message> -- creates a big ass message"

    if not inp:
        return bam.__doc__

    host = 'http://bigassmessage.com'
    path = '/dsx_BAM/boe.php'
    params = {'action': 'saveMsg', 'theStyle': 'basic', 'theMessage': inp}

    styles = ['basic', 'magic', 'pepsi', 'jprdy']

    for style in styles:
        if inp.startswith(style + ' '):
            params['theStyle'] = style
            params['theMessage'] = inp[len(style) + 1:]

    url = host + path + '?' + urllib.urlencode(params)

    try:
        response = etree.parse(url)
        status = response.xpath('//status/text()')[0]
        if status == 'ok':
            return host + '/' + response.xpath('//msgid/text()')[0]
        else:
            return response.xpath('//message/text()')[0]
    except:
        pass
