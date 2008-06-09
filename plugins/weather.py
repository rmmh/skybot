"weather, thanks to google"

import urllib, re, pickle, os
from xml.dom import minidom

WEATHER_URL = 'http://www.google.com/ig/api'

def setup(bot):
    bot.command("weather", weather, hook=r"weather (.*)")

def goog_weather(query):
	data = urllib.urlencode({'weather':query})
	url = WEATHER_URL + "?" + data
	#print url
	dom = minidom.parse(urllib.urlopen(url))

	if len(dom.getElementsByTagName('problem_cause')):
		return {'error': True}

	place = dom.getElementsByTagName('city')[0].getAttribute('data')
	temp = dom.getElementsByTagName('temp_f')[0].getAttribute('data')

	conditions = dom.getElementsByTagName('current_conditions')[0]
	condition = conditions.getElementsByTagName('condition')[0].getAttribute('data')
	wind = conditions.getElementsByTagName('wind_condition')[0].getAttribute('data')
	humidity = conditions.getElementsByTagName('humidity')[0].getAttribute('data')
	
	forecast = dom.getElementsByTagName('forecast_conditions')[0]
	high = forecast.getElementsByTagName('high')[0].getAttribute('data')
	low = forecast.getElementsByTagName('low')[0].getAttribute('data')

	return {
		'place': place,
		'temp': temp,
		'high': high,
		'low': low,
		'condition': condition,
		'wind': wind,
		'humidity': humidity
	}

def weather(bot, input):
    ".weather <location> -- queries google weather API for weather data"
    q = input.re.groups()[0]
    cond = goog_weather(q)

    if cond.has_key('error'):
        bot.reply(u'Couldn\'t fetch weather data for "%s", try using a zip/postal code' % (q))
        return

    format = u'%s %sF (%s/%s/%s) (h:%sF,l:%sF)'
    args = (cond['place'],cond['temp'],cond['condition'],cond['wind'],cond['humidity'],cond['high'],cond['low'])

    bot.reply(format.encode('utf-8') % args)
