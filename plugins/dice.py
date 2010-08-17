"""
dice.py: written by Scaevolus 2008, updated 2009
simulates dicerolls
"""
import re
import random

from util import hook


whitespace_re = re.compile(r'\s+')
valid_diceroll = r'^([+-]?(?:\d+|\d*d(?:\d+|F))(?:[+-](?:\d+|\d*d(?:\d+|F)))*)( .+)?$'
valid_diceroll_re = re.compile(valid_diceroll, re.I)
sign_re = re.compile(r'[+-]?(?:\d*d)?(?:\d+|F)', re.I)
split_re = re.compile(r'([\d+-]*)d?(F|\d*)', re.I)


def nrolls(count, n):
    "roll an n-sided die count times"
    if n == "F":
        return [random.randint(-1,1) for x in xrange(count)]
    if n < 2:  # it's a coin
        if count < 5000:
            return [random.randint(0, 1) for x in xrange(count)]
        else:  # fake it
            return [int(random.normalvariate(.5*count, (.75*count)**.5))]
    else:
        if count < 5000:
            return [random.randint(1, n) for x in xrange(count)]
        else:  # fake it
            return [int(random.normalvariate(.5*(1+n)*count,
                (((n+1)*(2*n+1)/6.-(.5*(1+n))**2)*count)**.5))]


@hook.command('roll')
@hook.regex(valid_diceroll, re.I)
@hook.command
def dice(inp):
    ".dice <diceroll> -- simulates dicerolls, e.g. .dice 2d20-d5+4 roll 2 " \
        "D20s, subtract 1D5, add 4"
    desc = None
    try: # if inp is a re.match object...
        (inp, desc) = inp.groups()
    except AttributeError:
        pass # we got called via hook.command, inp is already the roll
    if desc == None: (inp, desc) = valid_diceroll_re.match(inp).groups()
    desc = desc.strip()
    spec = whitespace_re.sub('', inp)
    if not valid_diceroll_re.match(spec):
        return "Invalid diceroll"
    groups = sign_re.findall(spec)

    rolls = []
    bias = 0
    for roll in groups:
        count, side = split_re.match(roll).groups()
        count = int(count) if count not in " +-" else 1
        if side.lower() == "f": # fudge dice are basically 1d3-2
                rolls += nrolls(count, "F")
        elif side == "":
            bias += count
        else:
            side = int(side)
            try:
                if count > 0:
                    rolls += nrolls(count, side)
                else:
                    rolls += [-x for x in  nrolls(abs(count), side)]
            except OverflowError:
                return "Thanks for overflowing a float, jerk >:["

    return "%s: %d (%s=%s)" % (desc,  sum(rolls)+bias, inp, str(rolls).strip("[]"))
