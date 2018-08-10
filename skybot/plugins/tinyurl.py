from skybot.util import http
from skybot.util import hook


@hook.regex(r'(?i)http://(?:www\.)?tinyurl.com/([A-Za-z0-9\-]+)')
def tinyurl(match):
    try:
        return http.open(match.group()).url.strip()
    except http.URLError, e:
        pass
