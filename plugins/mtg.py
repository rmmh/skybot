import re

from util import hook, http


set_abbrevs = {}


def load_set_abbrevs():
    h = http.get_html('http://magiccards.info/sitemap.html')
    for link in h.xpath('//ul/li/a'):
        set_abbrevs[link.text] = link.getnext().text.upper()


@hook.command
def mtg(inp):
    ".mtg <name> -- gets information about Magic the Gathering card <name>"

    if not set_abbrevs:
        load_set_abbrevs()

    url = 'http://magiccards.info/query?v=card&s=cname'
    h = http.get_html(url, q=inp)

    name = h.find('body/table/tr/td/span/a')
    if name is None:
        return "no cards found"
    card = name.getparent().getparent().getparent()

    card_type = re.sub(r'\s+', ' ', card.find('td/p').text).strip()

    # this is ugly
    text = http.html.tostring(card.xpath("//p[@class='ctext']/b")[0])
    text = text.replace('<br>', '$')
    text = http.html.fromstring(text).text_content()
    text = re.sub(r'(\w+\s*)\$+(\s*\w+)', r'\1. \2', text)
    text = text.replace('$', ' ')
    text = re.sub(r'\(.*?\)', '', text)  # strip parenthetical explanations
    text = re.sub(r'\.(\S)', r'. \1', text)  # fix spacing

    editions = card.xpath('.//p[.//b[text() = "Editions:"]]')
    printings = editions[0].text_content()
    printings = re.search(r'(?s)Editions:(.*)Languages:', printings).group(1)
    printings = re.findall(r'\s*(.+?(?: \([^)]+\))*) \((.*?)\)',
                           ' '.join(printings.split()))

    printing_out = ', '.join('%s (%s)' % (set_abbrevs.get(x[0], x[0]),
                                          rarity_abbrevs.get(x[1], x[1]))
                             for x in printings)

    name.make_links_absolute(base_url=url)
    link = name.attrib['href']
    name = name.text_content().strip()
    text = ' '.join(text.split())

    return ' | '.join((name, card_type, text, printing_out, link))

rarity_abbrevs = {
    'Land': 'L',
    'Common': 'C',
    'Uncommon': 'UC',
    'Rare': 'R',
    'Special': 'S',
    'Mythic Rare': 'MR'}


def test_basic():
    desc = mtg('Black Lotus')
    assert 'Add three mana of any one color' in desc
    assert 'Artifact, 0' in desc
    assert 'UN (R)' in desc
