from util import http, hook

@hook.command(autohelp=False)
def fml(inp):
    try:
        r = http.get_json('https://q.beanteam.org/api/fml/random')
        return "{} | \x02Agreed\x02: {} - \x02Deserved\x02: {}".format(r["text"], r["your_life_sucks"], r["you_deserved_it"])
    except:
        pass

@hook.command(autohelp=False)
def marx(inp):
    try:
        response = http.get_json('https://q.beanteam.org/api/marx/random')
        return "{} | \x02Source\x02: {} \x02Year\x02: {}".format(response['quote'], response['source'], response['year'])
    except:
        pass

@hook.command(autohelp=False)
def trotsky(inp):
    try:
        response = http.get_json('https://q.beanteam.org/api/trotsky/random')
        return "{} | \x02Source\x02: {} \x02Year\x02: {}".format(response['quote'], response['source'], response['year'])
    except:
        pass

@hook.command(autohelp=False)
def engels(inp):
    try:
        response = http.get_json('https://q.beanteam.org/api/engels/random')
        return "{} | \x02Source\x02: {} \x02Year\x02: {}".format(response['quote'], response['source'], response['year'])
    except:
        pass