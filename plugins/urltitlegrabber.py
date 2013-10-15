# This plugin grabs the <title> tag from a mentioned URL 
# and feeds it back to the channel

from util import hook, http, urlnorm
import re

url_re = r'([a-zA-Z]+://|www\.)[^ ]*'

@hook.regex(url_re)
def urltitlegrabber(match):
  t = ""
  title = ""
  url = urlnorm.normalize(match.group().encode('utf-8'))
  t = http.get_html(url)
  title = t.find(".//title").text.strip().replace('\t', " ").replace('\n', "")
  if title and not re.search("twitter.com", url) and not re.search("youtube.com", url):
    return "[%s]" % title