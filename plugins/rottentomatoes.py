import json
import re

from util import http, hook


MOVIE_SEARCH_URL = 'https://www.rottentomatoes.com/api/private/v2.0/search/'
MOVIE_PAGE_URL = 'https://www.rottentomatoes.com/m/%s'


def get_rottentomatoes_data(movie_id):
    if movie_id.startswith('/m/'):
        movie_id = movie_id[3:]

    document = http.get_html(
        MOVIE_PAGE_URL % movie_id
    )

    # JSON for the page is stored in the script with ID 'jsonLdSchema'
    # So we can pull that for tons of information.
    ld_schema_element = document.xpath("//script[@id='jsonLdSchema']")[0]

    ld_schema = json.loads(ld_schema_element.text_content())

    critics_score_element = document.xpath("//div[@id='scoreStats']")[0]

    fresh_rotten_match = re.search(
        'Fresh:\s+([0-9]+)\s+Rotten:\s+([0-9]+)',
        critics_score_element.text_content()
    )

    if fresh_rotten_match:
        fresh, rotten = fresh_rotten_match.groups()
    else:
        fresh, rotten = 0, 0

    audience_score_element = document.xpath("//div[@class='audience-score meter']")[0]

    audience_score_match = re.search('([0-9]+)%', audience_score_element.text_content())

    if audience_score_match:
        audience_score = audience_score_match.group(1)
    else:
        audience_score = None

    return {
        'title': ld_schema['name'],
        'critics_score': ld_schema['aggregateRating']['ratingValue'],
        'audience_score': audience_score,
        'fresh': fresh,
        'rotten': rotten,
        'url': MOVIE_PAGE_URL % movie_id
    }


def search_rottentomatoes(inp):
    results = http.get_json(
        MOVIE_SEARCH_URL,
        limit=1,
        q=inp
    )

    if not results or not results['movieCount']:
        return None

    return results['movies'][0]['url']


@hook.command('rt')
@hook.command
def rottentomatoes(inp):
    '.rt <title> -- gets ratings for <title> from Rotten Tomatoes'

    movie_id = search_rottentomatoes(inp)

    if not movie_id:
        return 'no results'

    movie = get_rottentomatoes_data(movie_id)

    return (
        u"{title} - critics: \x02{critics_score}%\x02 "
        u"({fresh}\u2191{rotten}\u2193) "
        u"audience: \x02{audience_score}%\x02 - {url}"
    ).format(**movie)
