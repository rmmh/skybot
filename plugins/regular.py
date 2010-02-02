'''
regular.py

skybot plugin for testing regular expressions
by Ipsum
'''

import re

from util import hook


@hook.command('re')
def reg(inp):
    ".re <regex>  <string> -- matches regular expression in given <string> "\
            "(leave 2 spaces between)"

    query = inp.split("  ", 1)

    if not inp or len(query) != 2:
        return reg.__doc__

    return '|'.join(re.findall(query[0], query[1]))

