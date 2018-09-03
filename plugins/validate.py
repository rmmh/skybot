'''
Runs a given url through the w3c validator

by Vladi
'''

from util import hook, http


VALIDATOR_URL = 'http://validator.w3.org/nu/'


def get_validation_results(url):
    document = http.get_html(VALIDATOR_URL, doc=url)

    results = document.xpath('//div[@id="results"]/ol')

    if not results:
        return None

    results = results[0]

    warnings = results.xpath('//li[contains(@class, "warning")]')
    errors = results.xpath('//li[contains(@class, "error")]')

    return {
        'warning_count': len(warnings),
        'error_count': len(errors),
        'url': VALIDATOR_URL + '?doc=' + http.quote(url),
        'status': 'valid' if not errors else 'invalid'
    }

@hook.command
def validate(inp):
    ".validate <url> -- runs url through w3c markup validator"

    if not inp.startswith('http://') and not inp.startswith('https://'):
        inp = 'http://' + inp

    return (
        "{inp} was found to be {status} with " \
        "{error_count} error(s) and " \
        "{warning_count} warning(s)." \
        " see: {url}"
    ).format(inp=inp, **get_validation_results(inp))
