'''
Runs a given url through the w3c validator

by Vladi
'''

import urllib
import urllib2

from util import hook


@hook.command('val')
@hook.command('valid')
@hook.command
def validate(inp):
    '''.val/.valid/.validate <url> -- runs url through w3c markup validator'''

    if not inp:
        return validate.__doc__

    if not inp.startswith('http://'):
        inp = 'http://' + inp

    url = 'http://validator.w3.org/check?uri=%s' % urllib.quote(inp, '')
    info = dict(urllib2.urlopen(url).info())

    print info
    status = info['x-w3c-validator-status'].lower()
    if status in ("valid", "invalid"):
        errorcount = info['x-w3c-validator-errors']
        warningcount = info['x-w3c-validator-warnings']
        return "%s was found to be %s with %s errors and %s warnings." \
                " see: %s" % (inp, status, errorcount, warningcount, url)
