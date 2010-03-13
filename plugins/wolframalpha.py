import re
import urllib2

from lxml import html

from util import hook


@hook.command
@hook.command('wa')
def wolframalpha(inp):
    ".wa/.wolframalpha <query> -- scrapes Wolfram Alpha's" \
            "results for <query>"

    if not inp:
        return wolframalpha.__doc__

    url = "http://www.wolframalpha.com/input/?i=%s&asynchronous=false"

    h = html.parse(url % urllib2.quote(inp, safe=''))

    pods = h.xpath("//div[@class='pod ']")

    pod_texts = []
    for pod in pods:
        heading = pod.find('h2')
        if heading is not None:
            heading = heading.text_content().strip()
            if heading.startswith('Input'):
                continue
        else:
            continue

        results = []
        for image in pod.xpath('div/div[@class="output"]/img'):
            alt = image.attrib['alt'].strip()
            alt = alt.replace('\\n', '; ')
            alt = re.sub(r'\s+', ' ', alt)
            if alt:
                results.append(alt)
        if results:
            pod_texts.append(heading + ' ' + '|'.join(results))

    ret = '. '.join(pod_texts)

    if not pod_texts:
        return 'no results'

    ret = re.sub(r'\\(.)', r'\1', ret)

    def unicode_sub(match):
        return unichr(int(match.group(1), 16))

    ret = re.sub(r'\\:([0-9a-z]{4})', unicode_sub, ret)

    if len(ret) > 430:
        ret = ret[:ret.rfind(' ', 0, 430)]
        ret = re.sub(r'\W+$', '', ret) + '...'

    if not ret:
        return 'no result'

    return ret
