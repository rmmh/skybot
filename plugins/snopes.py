import urllib
import json

from util import hook, http


SNOPES_AGENT = 'Algolia for vanilla JavaScript (lite) 3.21.1;instantsearch.js 1.11.7;JS Helper 2.19.0'
SNOPES_API_KEY = '7da15c5275374261c3a4bdab2ce5d321'
SNOPES_APPLICATION_ID = 'YFRDX308ZD'
SNOPES_INDEX_NAME = 'wp_live_searchable_posts'

ALGOLIA_SEARCH_URL = 'https://{app_id}-dsn.algolia.net/1/indexes/*/queries'


def search_snopes(query):
    """
    Search the Snopes Algolia API for snopes investigations matching a query string.

    :param query: the string to search for
    :return: Returns a dictionary with keys for the claim, status, and url, or none if nothing was found
    :rtype: dict or none
    """
    search_params = {
        'query': query,
        'hitsPerPage': 1,
        'page': 0
    }

    query_params = {
        'x-algolia-agent': SNOPES_AGENT,
        'x-algolia-api-key': SNOPES_API_KEY,
        'x-algolia-application-id': SNOPES_APPLICATION_ID
    }

    post_data = {
        "requests": [
            {
                "indexName": SNOPES_INDEX_NAME,
                "params": urllib.urlencode(search_params)
            }
        ]
    }

    try:
        result = http.get_json(
            ALGOLIA_SEARCH_URL.format(app_id=SNOPES_APPLICATION_ID),
            query_params=query_params,
            post_data=json.dumps(post_data)
        )
    except http.HTTPError:
        return None

    result = result['results'][0]

    if 'hits' not in result or not result['hits']:
        return "no matching pages found"

    hit = result['hits'][0]

    return {
        'claim': hit['fact_check_title'],
        'status': hit['fact_check_rating'],
        'url': hit['permalink']
    }


@hook.command
def snopes(inp):
    """.snopes <topic> -- searches snopes for an urban legend about <topic>"""

    result = search_snopes(inp)

    return "CLAIM: \x02{claim}\x0f - STATUS: \x02{status}\x0f - {url}".format(**result)
