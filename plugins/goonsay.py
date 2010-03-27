import urllib2
import json

from util import hook

#Scaevolus: factormystic if you commit a re-enabled goonsay I'm
# going to revoke your commit access
#@hook.command
#def goonsay(inp, say=None):
#    say(' __________    /')
#    say('(--[. ]-[ .]  /')
#    say('(_______o__)')


@hook.command
@hook.command('gs')
def goonsay(inp):
    ".gs/.goonsay <id|add [message]> -- Get's the goonsay.com result for <id> "
    " or add a new :goonsay: to the database. With no args, random result."

    url = "http://goonsay.com/api/goonsays"

    req_headers = {
        'User-Agent': 'Skybot/1.0 http://bitbucket.org/Scaevolus/skybot/',
        'Content-Type': 'application/json',
    }

    q = inp.split(' ', 1)
    print q

    if len(q) == 2:
        cmd = q[0]
        args = q[1]

        if cmd == 'add':
            try:
                data = json.dumps({'text': args})
                req = urllib2.Request('%s/' % (url,), data, req_headers)
                j = json.loads(urllib2.urlopen(req).read())
            except urllib2.HTTPError, e:
                return e
            return '#%d - %s' % (j['id'], j['text'])
        else:
            return goonsay.__doc__

    if len(inp):
        try:
            req = urllib2.Request('%s/%d/' % (url, int(inp)), None,
                    req_headers)
            j = json.loads(urllib2.urlopen(req).read())
        except urllib2.HTTPError, e:
            if e.code == 410 or e.code == 404:
                return 'There is no :goonsay: by that id'
            return e
        except ValueError:
            return goonsay.__doc__
        return '#%d - %s' % (j['id'], j['text'])

    try:
        req = urllib2.Request('%s/random/' % (url,), None, req_headers)
        j = json.loads(urllib2.urlopen(req).read())
    except urllib2.HTTPError, e:
        return e

    return '#%d - %s' % (j['id'], j['text'])
