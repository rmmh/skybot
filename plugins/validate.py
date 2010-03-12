'''
Runs a given url through the w3c validator and queries
	the result header for information

by Vladi
'''

import urllib

from util import hook

path = 'http://validator.w3.org/check?uri=%s'

@hook.command('val')
@hook.command
def validate(inp):
	'''.val/.validate <url> -- runs url through the w3c markup validator'''
	
	if not inp:
		return validate.__doc__
		
	if not inp.startswith('http://'):
		inp = 'http://' + inp
		
	url = path % (urllib.quote(inp))
	temp = urllib.urlopen(url).info()

	status = temp.getheader('X-W3C-Validator-Status')
	if (status == "Valid" or status == "Invalid"):
		errorcount = temp.getheader('X-W3C-Validator-Errors')
		warningcount = temp.getheader('X-W3C-Validator-Warnings')
		return "%s was validated as %s with %s errors and %s warnings. See: %s" \
			% (inp, status.lower(), errorcount, warningcount, url)
	else:
		return "Something went wrong while validating %s" % (inp)