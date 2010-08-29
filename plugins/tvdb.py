"""
TV information, written by Lurchington 2010
"""

# python imports
import datetime

from contextlib import closing
from itertools import ifilter
from util import hook
from urllib import urlencode
from urllib2 import urlopen

# third-party-imports
from lxml import etree as ET

base_url = "http://thetvdb.com"
api_key = "D1EBA6781E2572BB"

# @hook.command
# def tv(inp):
#     return search(inp)

@hook.command
def tv_next(inp):
    """
    return the next episode of the provided seriesname
    """
    return next_episode(inp)

def search(seriesname):
    """
    search tvdb for series IDs corresponding to a provided seriesname and
    return the first series ID found
    """
    id = None
    with closing(urlopen(_query_GetSeries(seriesname))) as show_query:
        for event, element in ET.iterparse(show_query):
            if element.tag == u"Series":
                id = element.findtext("id")
                break
        return id
                    
    return None

def next_episode(seriesname):
    
    id = search(seriesname)
    if id is None:
        return "unknown tv series (using www.thetvdb.org)"
        
    with closing(_get_full_series_record(id)) as fsr:
        tree = ET.parse(fsr)
        root = tree.getroot()

    series = root.find("Series")

    status = series.findtext("Status")
    if status == u"Ended":
        #short circuit evaluation to avoid 
        #having to find episodes for a finished show
        return u"Sorry, %s is over" % series.findtext("SeriesName")
        
    next_eps = []    

    for episode in root.iterchildren("Episode", reversed=True):
        first_aired = episode.findtext("FirstAired")        
        try:
            y, m, d = map(int, first_aired.split("-"))
            airdate = datetime.date(y, m, d)
        except Exception:
            continue
        
        today = datetime.date.today()
        test = datetime.date(2010, 9, 20)
        
        episode_name = episode.findtext("EpisodeName")
        if not episode_name:
            episode_name = "No Title Yet"
        
        if airdate > today:
            next_eps = ['%s ("%s")' % (episode.findtext("FirstAired"), 
                                       episode_name)]
        elif airdate == today:
            #if today is the day of the newest episode, return it
            #along with the next episode after
            next_eps = (['Today ("%s")' % episode_name] +
                        next_eps)
 
        else:
            #we're iterating in reverse order with newest episodes last
            #so, as soon as we're past today, break out of loop
            break
            
    if not next_eps:
        return "No new episodes scheduled for %s" % series.findtext("SeriesName")
        
    return " -> ".join(next_eps)    
    
        
def _query_GetSeries(seriesname, language=None):
    """
    http://thetvdb.com/wiki/index.php/API:GetSeries
    """

    if language is None:
        data = urlencode(dict(seriesname=seriesname), doseq=True)
    else:
        data = urlencode(dict(language=language,
                                seriesname=seriesname),
                                doseq=True)

    url = _make_url(base_url, "api",
                    "GetSeries.php?%s"%data)

    return url
    
def _get_full_series_record(seriesid):
    
    url = _make_url(base_url, "api", api_key, "series", 
                    seriesid, "all", "en.xml")
    return urlopen(url)
        
    
                    
                    
    
def _make_url(url_netloc, *url_path):
    """
    Appends all parts of url_path to the given url_netloc using "/" as\
    a delimeter
    """

    url_sequence = [url_netloc]
    url_sequence.extend(url_path)

    return "/".join(url_sequence)