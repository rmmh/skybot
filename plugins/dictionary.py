import re

from util import hook, http


@hook.command('u')
@hook.command
def urban(inp):
    '''.u/.urban <phrase> -- looks up <phrase> on urbandictionary.com'''
    if not inp:
        return urban.__doc__

    url = 'http://www.urbandictionary.com/define.php'
    page = http.get_html(url, term=inp)
    words = page.xpath("//td[@class='word']")
    defs = page.xpath("//div[@class='definition']")

    if not defs:
        return 'no definitions found'

    out = words[0].text_content().strip() + ': ' + ' '.join(
            defs[0].text_content().split())

    if len(out) > 400:
        out = out[:out.rfind(' ', 0, 400)] + '...'

    return out


# define plugin by GhettoWizard & Scaevolus
@hook.command('dict')
@hook.command
def define(inp):
    ".define/.dict <word> -- fetches definition of <word>"

    if not inp:
        return define.__doc__

    url = 'http://ninjawords.com/'

    h = http.get_html(url + http.quote_plus(inp))

    definition = h.xpath('//dd[@class="article"] | '
                         '//div[@class="definition"] |'
                         '//div[@class="example"]')

    if not definition:
        return 'No results for ' + inp

    def format_output(show_examples):
        result = ''

        correction = h.xpath('//span[@class="correct-word"]')
        if correction:
            result = 'definition for "%s": ' % correction[0].text

        sections = []
        for section in definition:
            if section.attrib['class'] == 'article':
                sections += [[section.text_content() + ': ']]
            elif section.attrib['class'] == 'example':
                if show_examples:
                    sections[-1][-1] += ' ' + section.text_content()
            else:
                sections[-1] += [section.text_content()]

        for article in sections:
            result += article[0]
            if len(article) > 2:
                result += ' '.join('%d. %s' % (n + 1, section)
                                    for n, section in enumerate(article[1:]))
            else:
                result += article[1] + ' '

        synonyms = h.xpath('//dd[@class="synonyms"]')
        if synonyms:
            result += synonyms[0].text_content()
    
        result = re.sub(r'\s+', ' ', result)
        result = re.sub('\xb0', '', result)
        return result

    result = format_output(True)
    if len(result) > 450:
        result = format_output(False)

    if len(result) > 450:
        result = result[:result.rfind(' ', 0, 450)]
        result = re.sub(r'[^A-Za-z]+\.?$', '', result) + ' ...'

    return result
