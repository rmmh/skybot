'''
regular.py

skybot plugin for testing regular expressions
by Ipsum
'''

import thread
import codecs
import re

from util import hook



@hook.command('re')
def reg(bot, input):
	".re <regex>  <string> -- matches regular expression in given <string> (seperate regex and string by 2 spaces)"

	m = ""
	
	if len(input.msg) < 3:
		return reg.__doc__
		
	query = input.inp.partition("  ")
	
	
	if query[2] != "":
		r = re.compile(query[0])

		matches = r.findall(query[2])
		for match in matches:
			m += match + "|"
		
		return m.rstrip('|')
		
	else:
		return reg.__doc__