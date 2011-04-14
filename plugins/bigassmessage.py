from util import hook, http


@hook.command
def bam(inp):
    ".bam [basic|magic|heart|krugr] <message> -- creates a big ass message"

    host = 'http://bigassmessage.com/'
    path = 'BAM.php?'
    params = {'action': 'SAVE', 'theStyle': 'basic', 'theMessage': inp}

    if ' ' in inp:
        style, message = inp.split(None, 1)
        if style in ['basic', 'magic', 'heart', 'krugr']:
            params['theStyle'] = style
            params['theMessage'] = message

    response = http.get_xml(host + path, params)
    status = response.xpath('//status/text()')[0]

    if status == 'ok':
        return host + response.xpath('//msgid/text()')[0]
    else:
        return response.xpath('//message/text()')[0]
