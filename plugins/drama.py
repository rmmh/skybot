'''Searches Encyclopedia Dramatica and returns the first paragraph of the 
article'''

import urllib2
from util import hook
from util import BeautifulSoup

api_url = "http://encyclopediadramatica.com/api.php?action=opensearch&search=%s"
ed_url = "http://encyclopediadramatica.com/%s"

ua_header = ('User-Agent','Skybot/1.0 http://bitbucket.org/Scaevolus/skybot/')


def get_article_name(query):
   q = api_url % (urllib2.quote(query, safe=''))
   request = urllib2.Request(q)
   request.add_header(*ua_header)
   opener = urllib2.build_opener()
   try:
      results = eval(opener.open(request).read())
      if isinstance(results,list) and len(results[1]):
         return results[1][0].replace(' ','_')
   except:
      return None

@hook.command('ed')   
@hook.command
def drama(inp):
   '''.drama <phrase> -- gets first paragraph of Encyclopedia Dramatica ''' \
   '''article on <phrase>'''
   if not inp:
      return drama.__doc__
   
   article_name = get_article_name(inp)
   if not article_name:
      return 'no results found'
   
   url = ed_url % (urllib2.quote(article_name))
   request = urllib2.Request(url)
   request.add_header(*ua_header)
   opener = urllib2.build_opener()
   result = opener.open(request).read()
   
   bs = BeautifulSoup.BeautifulSoup(result)
   content = bs.find('div', {"id":"bodyContent"})
   
   for p in content.findAll('p'):
      if p.text:
         summary = ''.join(''.join(p.findAll(text=True)).splitlines())
         if len(summary) > 300:
            summary = summary[:300] + "..."
         return '%s -- %s' % (summary, url)
   return "error"
