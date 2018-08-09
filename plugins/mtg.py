from util import hook, http
import unittest


def card_search(name):
    results = http.get_json('http://api.magicthegathering.io/v1/cards', name=name, pageSize=1)

    if not 'cards' in results or len(results['cards']) == 0:
        return None

    return results['cards'][0]


@hook.command
def mtg(inp):
    '''.mtg <name> - Searches for Magic the Gathering card given <name>'''

    card = card_search(inp)

    if not card:
        return 'Card not found.'

    symbols = {
        '{0}': '0', 
        '{1}': '1', 
        '{2}': '2', 
        '{3}': '3', 
        '{4}': '4', 
        '{5}': '5', 
        '{6}': '6', 
        '{7}': '7', 
        '{8}': '8', 
        '{9}': '9', 
        '{10}': '10', 
        '{11}': '11', 
        '{12}': '12', 
        '{13}': '13', 
        '{14}': '14', 
        '{15}': '15', 
        '{16}': '16', 
        '{17}': '17', 
        '{18}': '18', 
        '{19}': '19', 
        '{20}': '20',
        '{T}': u'\u27F3', 
        '{S}': u'\u2744', 
        '{Q}': u'\u21BA', 
        '{C}': u'\u27E1', 
        '{W}': 'W', 
        '{U}': 'U', 
        '{B}': 'B', 
        '{R}': 'R', 
        '{G}': 'G',
        '{W/P}': u'\u03D5', 
        '{U/P}': u'\u03D5', 
        '{B/P}': u'\u03D5', 
        '{R/P}': u'\u03D5', 
        '{G/P}': u'\u03D5',
        '{X}': 'X',
        '\n': ' ',
    }

    results = {
        'name': card.get('name'),
        'types': ', '.join(t.capitalize() for t in card.get('types', [])),
        'cost': card.get('manaCost', '{0}').strip(),
        'text': card.get('text', 'No Description').strip(),
        'power': card.get('power'),
        'toughness': card.get('toughness'),
        'loyalty': card.get('loyalty'),
        'multiverse_id': card.get('multiverseid'),
    }

    if 'supertypes' in card and card['supertypes']:
        results['supertypes'] = ', '.join(card['supertypes']).title()

    if 'subtypes' in card and card['subtypes']:
        results['subtypes'] = ', '.join(card['subtypes']).title()

    for fragment, rep in symbols.items():
        results['text'] = results['text'].replace(fragment, rep)
        results['cost'] = results['cost'].replace(fragment, rep)

    if results['cost'] == '0':
        results['cost'] = 'No Cost'

    template = ['{name} -']

    if 'supertypes' in results:
        template.append('{supertypes} >')
    template.append('{types}')
    if 'subtypes' in results:
        template.append('> {subtypes}')
    template.append('- {cost} |')
    if results['loyalty']:
        template.append('{loyalty} Loyalty |')
    if results['power'] and results['toughness']:
        template.append('{power}/{toughness} |')
    template.append('{text} | http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid={multiverse_id}')

    return u' '.join(template).format(**results)


class MTGTest(unittest.TestCase):
    def test_black_lotus(self):
        assert mtg('Black Lotus') == u'Black Lotus - Artifact - No Cost | \u27F3, Sacrifice Black Lotus: Add ' \
                                     u'three mana of any one color. | ' \
                                     u'http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=382866'

    def test_underground_sea(self):
        assert mtg('Underground Sea') == u'Underground Sea - Land : Island, Swamp - No Cost | ' \
                                         u'(\u27F3: Add U or B.) | ' \
                                         u'http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=383142'

    def test_mana_breach(self):
        assert mtg('Mana Breach') == u'Mana Breach - Enchantment - 2U | Whenever a player casts a spell, that ' \
                                     u'player returns a land they control to its owner\'s hand. | ' \
                                     u'http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=6078'


if __name__ == '__main__':
    unittest.main()
