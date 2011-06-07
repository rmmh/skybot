import urllib2
import json
import re
import zlib
from datetime import datetime

from util import hook


stack_re = (r'(stackoverflow|serverfault|askubuntu)\.com/questions/'
    '([0-9]+)', re.I)
api_url = 'http://api.%s.com/1.1/questions/%s'


def fuzzy_date(d):
    post_date = datetime.fromtimestamp(d)
    diff = datetime.utcnow() - post_date
    s = diff.seconds

    if diff.days > 7 or diff.days < 0:
        return d.strftime('%d %b %y')

    elif diff.days > 1:
        return 'about %s days ago.' % diff.days

    elif diff.days == 1:
        return 'about 1 day ago.'

    elif diff.seconds <= 1:
        return 'just now.'

    elif diff.seconds < 60:
        return 'about %s seconds ago.' % diff.seconds

    elif diff.seconds < 120:
        return 'about 1 minute ago.'

    elif diff.seconds < 3600:
        return 'about %s minutes ago.' % (diff.seconds/60)

    elif diff.seconds < 7200:
        return 'about an hour ago.'

    else:
        return 'about %s hours ago' % (diff.seconds/3600)


def get_stack_question(domain, question_id):
    """
    Stackapps spit out gzip'd JSON, as per:
    http://api.stackoverflow.com/1.1/usage/
    With that in mind, we have to grab the gzipped data,
    then decompress it, then load the raw string into a JSON object.
    """
    url = api_url % (domain, question_id)
    gz_page = urllib2.urlopen(url)

    #Skip over gzip header with 16+zlib.MAX_WBITS offset
    raw_json = zlib.decompress(gz_page.read(), 16 + zlib.MAX_WBITS)
    q_json = json.loads(raw_json)

    if q_json.get('error'):
        return

    q_json = q_json['questions'][0]


    out = '"\x02%s\x02" ' % q_json['title']
    if 'bounty_amount' in q_json:
        out += '\x030,12+%d\x03rep ' % q_json['bounty_amount']

    out += '- \x02%d\x02 pt%s, ' % (
            q_json['score'],
            's' if not q_json['score'] else '')

    out += '\x02%d\x02 answer%s ' % (
            q_json['answer_count'],
            's' if not q_json['answer_count'] else '' )

    out += '- asked by \x02%s\x02 ' % q_json['owner']['display_name']
    out += fuzzy_date(q_json['creation_date'])

    return out 



@hook.regex(*stack_re)
def stack_url(match):
    return get_stack_question(match.group(1),match.group(2))
