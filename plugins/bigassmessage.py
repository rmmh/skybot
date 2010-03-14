from util import hook
from lxml import etree
import urllib

host = 'http://bigassmessage.com'


@hook.command
def bam(inp):

    if not inp:
        return 'you forgot something'

    inp = urllib.quote_plus(inp)
    path = '/dsx_BAM/boe.php?action=saveMsg&theStyle=magic&theMessage=' + inp
    url = host + path

    try:
        response = etree.parse(url)
        status = response.xpath('//status/text()')[0]
        if status == 'ok':
            return host + '/' + response.xpath('//msgid/text()')[0]
        else:
            return response.xpath('//message/text()')[0]
    except:
        pass
