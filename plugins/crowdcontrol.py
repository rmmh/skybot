# crowdcontrol.py by craisins in 2014
# Bot must have some sort of op or admin privileges to be useful

import re
import time
from util import hook

# Use "crowdcontrol" array in config
# syntax
# rule:
#   re: RegEx. regular expression to match
#   msg: String. message to display either with kick or as a warning
#   kick: Integer. 1 for True, 0 for False on if to kick user
#   ban_length: Integer. (optional) Length of time (seconds) to ban user. (-1 to never unban, 0 to not ban, > 1 for time)


@hook.regex(r'.*')
def crowdcontrol(inp, nick='', chan='', host='', bot=None, conn=None):
    inp = inp.group(0)
    for rule in bot.config.get('crowdcontrol', []):
        pattern = re.compile(rule['re'])
        if re.search(pattern, inp) is not None:
            if 'ban_length' in rule and rule['ban_length'] != 0:
                conn.cmd("MODE", [chan, "+b", host])
            if rule['kick']:
                conn.cmd('KICK', [chan, nick, rule['msg']])
            if 'ban_length' in rule and rule['ban_length'] > 0:
                time.sleep(rule['ban_length'])
                conn.cmd("MODE", [chan, "-b", host])
            if not rule['kick']:
                return rule['msg']
