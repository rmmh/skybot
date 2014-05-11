# crowdcontrol.py by craisins in 2014
# Bot must have some sort of op or admin privileges to be useful

import re
import time
from util import hook

rules = []
# syntax
# rule:
#   re: RegEx. regular expression to match
#   msg: String. message to display either with kick or as a warning
#   kick: Boolean. True/False on if to kick user
#   ban_length: Integer. (optional) Length of time (seconds) to ban user. (-1 to never unban, 0 to not ban, > 1 for time)

# rules = [
#     {
#         "re": r'^data:image/(bmp|gif|jpg|jpeg|png|svg);base64,',
#         "msg": "Please don't paste base64 images. You've been banned for 60 seconds.",
#         "kick": True,
#         "ban_length": 60
#     }
# ]

@hook.regex(r'.*')
def crowdcontrol(inp, nick='', chan='', host='', conn=None):
    inp = inp.group(0)
    for rule in rules:
        if re.search(rule['re'], inp) is not None:
            if 'ban_length' in rule and rule['ban_length'] != 0:
                conn.cmd("MODE " + chan + " +b " + host)
            if rule['kick']:
                conn.cmd("KICK " + chan + " " + nick + " :" + rule['msg'])
            if 'ban_length' in rule and rule['ban_length'] > 0:
                time.sleep(rule['ban_length'])
                conn.cmd("MODE " + chan + " -b " + host)
            if not rule['kick']:
                return rule['msg']