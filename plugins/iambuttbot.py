"""
iambuttbot.py: avidal 2009
posts everything buttbot says to the iambuttbot twitter account
"""

import urllib
import hook

@hook.command(hook=r'(.*)', prefix=False)
def iambuttbot(bot, input):
    if input.nick.lower() != 'buttbot': 
        return

    password = open('iambuttbot_password').readlines()[0].strip()
    status = input.inp if len(input.inp) <= 140 else input.inp[:137] + "..."
    data = urllib.urlencode({"status": status})
    url = 'http://iambuttbot:%s@twitter.com/statuses/update.xml' % password
    response = urllib.urlopen(url, data)
