"""
iambuttbot.py: avidal 2009
posts everything buttbot says to the iambuttbot twitter account
"""

import urllib
import hook

@hook.command(hook=r'(.*)')
def iambuttbot(bot, input):
    if input.nick.lower() != 'buttbot': return
    
    buttbot_pass = open('iambuttbot_passwd').readlines()[0].strip()
    status = input.inp if len(input.inp) <= 140 else input.inp[:137] + "..."
    data = urllib.urlencode({"status": status})
    response = urllib.urlopen("http://iambuttbot:%s@twitter.com/statuses/update.xml" % (buttbot_pass,), data)
