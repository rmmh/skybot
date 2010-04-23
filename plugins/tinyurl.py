from util import hook, http


@hook.regex(r'(?i)http://(?:www\.)?tinyurl.com/([A-Za-z0-9\-]+)')
def tinyurl(match):
    try:
        return http.open(match.group()).url.strip()
    except http.URLError, e:
        pass
