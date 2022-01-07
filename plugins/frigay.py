import datetime
import subprocess
import pytz

from util import hook

@hook.command
def frigay(inp, say=None):
    day = datetime.datetime.now(pytz.timezone('US/Mountain')).weekday()
    if day == 4:
        toilet_result = subprocess.getoutput("toilet --irc --gay -f train ' FRIGAY!'")
        for line in toilet_result.split('\n'):
            say(line)
    else:
        say("It is not Frigay...")
