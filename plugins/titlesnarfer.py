from util import hook, http

REGEX = r"(http|https)://(www.)?(?!(www.)?twitter|(www.)?youtube|(www.)?google)[-a-zA-Z0-9@:%._\+~#=]{1,256}.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)"

@hook.regex(REGEX)
def titlesnarfer(match, say=None):
    try:
        page = http.get_html(match.group())
        title = page.find(".//title").text
        say("^ %s" % (title))
    except:
        pass
