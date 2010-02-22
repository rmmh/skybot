from util import hook
import urllib, httplib, sys

def doquery(argv):
    query=urllib.urlencode({'q':argv})

    start='<h2 class=r style="font-size:138%"><b>'
    end='</b>'

    google=httplib.HTTPConnection("www.google.com")
    google.request("GET","/search?"+query)
    search=google.getresponse()
    data=search.read()

    if data.find(start)==-1: return "Could not calculate " + argv
    else:
        begin=data.index(start)
        result=data[begin+len(start):begin+data[begin:].index(end)]
        result = result.replace("<font size=-2> </font>",",").replace(" &#215; 10<sup>","E").replace("</sup>","").replace("\xa0",",")
        return result

@hook.command
def calc(inp):
   '''.calc <term> -- returns Google Calculator result'''
   if not inp or not inp.strip():
      return calc.__doc__
   return doquery(inp)
