#!/usr/bin/python
"weather, thanks to google"

import urllib
from lxml import etree

import hook

@hook.command
def weather(bot, input):
    ".weather <location> -- queries the google weather API for weather data"

    if not input.inp.strip(): # blank line
        return "welp"

    data = urllib.urlencode({'weather':input.inp.encode('utf-8')})
    url = 'http://www.google.com/ig/api?' + data
    w = etree.parse(url).find('weather')

    if w.find('problem_cause') is not None:
        return "Couldn't fetch weather data for '%s', try using a zip or " \
                "postal code." % input.inp
   
    info = dict((e.tag, e.get('data')) for e in w.find('current_conditions'))
    info['city'] = w.find('forecast_information/city').get('data')
    info['high'] = w.find('forecast_conditions/high').get('data')
    info['low'] = w.find('forecast_conditions/low').get('data')

    return '%(city)s: %(condition)s, %(temp_f)sF/%(temp_c)sC (H:%(high)sF, ' \
            'L:%(low)sF), %(humidity)s, %(wind_condition)s.' % info
