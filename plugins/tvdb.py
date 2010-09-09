"""
TV information, written by Lurchington 2010
modified by rmmh 2010
"""

import datetime
from contextlib import closing
from urllib2 import URLError
from zipfile import ZipFile

from lxml import etree
from util import hook, http

# StringIO fallback method from: http://effbot.org/librarybook/cstringio.htm
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

base_url = "http://thetvdb.com/api/"
api_key = "469B73127CA0C411"

def get_zipped_xml(*args, **kwargs):
    try:
        path = kwargs.pop("path")
    except KeyError:
        raise KeyError("must specify a path for the zipped file to be read")
    
    with closing(StringIO(http.get(*args, **kwargs))) as zip_buffer:
        return etree.parse(ZipFile(zip_buffer, "r").open(path))

@hook.command
def tv_next(inp):
    ".tv_next <series> -- get the next episode of <series> from thetvdb.com"

    # http://thetvdb.com/wiki/index.php/API:GetSeries
    try:
        query = http.get_xml(base_url + 'GetSeries.php', seriesname=inp)
    except URLError:
        return "error contacting thetvdb.com"
        
    series_id = query.xpath('//seriesid/text()')

    if not series_id:
        return "unknown tv series (using www.thetvdb.com)"

    series_id = series_id[0]

    try:
        series = get_zipped_xml(base_url + '%s/series/%s/all/en.zip' %
                                    (api_key, series_id), path="en.xml")
    except URLError:    
        return "error contacting thetvdb.com"
                              
    series_name = series.xpath('//SeriesName/text()')[0]

    if series.xpath('//Status/text()')[0] == 'Ended':
        return '%s has ended.' % series_name

    next_eps = []
    today = datetime.date.today()

    for episode in reversed(series.xpath('//Episode')):
        first_aired = episode.findtext("FirstAired")
        try:
            airdate = datetime.date(*map(int, first_aired.split('-')))
        except (ValueError, TypeError):
            continue

        episode_name = episode.findtext("EpisodeName") or "No Title Yet"
        episode_num = "S%02dE%02d" % (int(episode.findtext("SeasonNumber")),
                                      int(episode.findtext("EpisodeNumber")))
        episode_desc = '%s "%s"' % (episode_num, episode_name)

        if airdate > today:
            next_eps = ['%s (%s)' % (first_aired, episode_desc)]
        elif airdate == today:
            next_eps = ['Today (%s)' % episode_desc] + next_eps
        else:
            #we're iterating in reverse order with newest episodes last
            #so, as soon as we're past today, break out of loop
            break

    if not next_eps:
        return "there are no new episodes scheduled for %s" % series_name

    if len(next_eps) == 1:
        return "the next episode of %s airs %s" % (series_name, next_eps[0])
    else:
        next_eps = ', '.join(next_eps)
        return "the next episodes of %s: %s" % (series_name, next_eps)
