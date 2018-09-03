from time import gmtime
import re

from util import hook, http


PRE_DB_SEARCH_URL = 'https://pr3.us/search.php'
PRE_DB_RE_NOT_FOUND = re.compile('^Nothing found for: .+$')


def get_predb_release(release_name):
    timestamp = gmtime()

    try:
        # Without accept headers, the underlying
        # site falls apart for some reason
        h = http.get_html(
            PRE_DB_SEARCH_URL,
            search=release_name,
            ts=timestamp,
            pretimezone=0,
            timezone=0,
            headers={
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.5'
            }
        )
    except http.HTTPError:
        return None

    results = h.xpath("//tr")

    if not results:
        return None

    first_result = results[0]

    if PRE_DB_RE_NOT_FOUND.match(first_result.text_content()):
        return None

    section_field, name_field, _, size_field, ts_field = \
        first_result.xpath('./td')[:5]

    date, time = ts_field.text_content().split()

    return {
        'date': date,
        'time': time,
        'section': section_field.text_content(),
        'name': name_field.text_content().strip(),
        'size': size_field.text_content()
    }


@hook.command
def predb(inp):
    """.predb <query> -- searches scene releases"""

    release = get_predb_release(inp)

    if not release:
        return 'zero results'

    if release['size']:
        release['size'] = ' - %s' % release['size']

    return '{date} - {section} - {name}{size}'.format(**release)
