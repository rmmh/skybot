from time import strftime
from datetime import datetime

from util import hook, http

@hook.regex(r"(?P<scheme>https)?://(?P<domain>[.a-zA-Z_\-0-9]+)/(#!/)?(@\w+)(@[a-zA-Z0-9._\-]+)?/(?P<id>\d+)")
def show_toot(match):
    scheme = match.group("scheme")
    domain = match.group("domain")
    id = match.group("id")
    request_url = f"{scheme}://{domain}/api/v1/statuses/{id}"
    toot = http.get_json(request_url)
    time = toot["created_at"]
    time = datetime.fromisoformat(time.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
    username = toot["account"]["username"]
    text = http.unescape(toot["content"].replace("</p>", " ").strip())
    media = ""
    for attachment in toot["media_attachments"]:
        if attachment["remote_url"]:
            media = media + " " + attachment["remote_url"]
        else:
            media = media + " " + attachment["url"]
    media = media.strip()
    
    return f"{time} \x02{username}\x02: {text} {media}".strip()
