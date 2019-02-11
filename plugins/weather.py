"weather, thanks to darksky and google geocoding"

from util import hook, http

GEOCODING_URL = u'https://maps.googleapis.com/maps/api/geocode/json'
DARKSKY_URL = u'https://api.darksky.net/forecast/'


def geocode_location(api_key, loc):
    try:
        parsed_json = http.get_json(GEOCODING_URL, address=loc, key=api_key)
    except IOError:
        return None

    return parsed_json


def get_weather_data(api_key, lat, long):
    query = '{key}/{lat},{long}'.format(key=api_key, lat=lat, long=long)
    url = DARKSKY_URL + query
    try:
        parsed_json = http.get_json(url)
    except IOError:
        return None

    return parsed_json


def f_to_c(temp_f):
    return (temp_f - 32) * 5 / 9


def mph_to_kph(mph):
    return mph * 1.609


@hook.api_key('google-geocoding', 'darksky')
@hook.command(autohelp=False)
def weather(inp, chan='', nick='', reply=None, db=None, api_key=None):
    """
    .weather <location> [dontsave] | @<nick> -- gets weather data from
        darksky https://darksky.net/dev
    """
    if 'google-geocoding' not in api_key and 'darksky' not in api_key:
        return None

    # this database is used by other plugins interested in user's locations,
    # like .near in tag.py
    db.execute("create table if not exists "
               "location(chan, nick, loc, lat, lon, primary key(chan, nick))")

    if inp[0:1] == '@':
        nick = inp[1:].strip()
        loc = None
        dontsave = True
    else:
        dontsave = inp.endswith(" dontsave")
        # strip off the " dontsave" text if it exists and set it back to `inp`
        # so we don't report it back to the user incorrectly
        if dontsave:
            inp = inp[:-9].strip().lower()
        loc = inp

    if not loc:  # blank line
        loc = db.execute(
            "select loc from location where chan=? and nick=lower(?)",
            (chan, nick)).fetchone()
        if not loc:
            try:
                # grab from old-style weather database
                loc = db.execute("select loc from weather where nick=lower(?)",
                                 (nick,)).fetchone()
            except db.OperationalError:
                pass    # no such table
            if not loc:
                return weather.__doc__
        loc = loc[0]

    location = geocode_location(api_key['google-geocoding'], loc)

    if not location or location.get(u'status') != u'OK':
        reply('Failed to determine location for {}'.format(inp))
        return

    geo = location.get(u'results', [{}])[0].get(u'geometry', {}).get(u'location', None)
    if not geo or u'lat' not in geo or u'lng' not in geo:
        reply('Failed to determine location for {}'.format(inp))
        return

    parsed_json = get_weather_data(api_key['darksky'], geo[u'lat'], geo[u'lng'])
    current = parsed_json.get(u'currently')

    if not current:
        reply('Failed to get weather data for {}'.format(inp))
        return

    forecast = parsed_json['daily']['data'][0]

    info = {
        u'city': location[u'results'][0][u'formatted_address'],
        u't_f': current[u'temperature'],
        u't_c': f_to_c(current[u'temperature']),
        u'h_f': forecast[u'temperatureHigh'],
        u'h_c': f_to_c(forecast[u'temperatureHigh']),
        u'l_f': forecast[u'temperatureLow'],
        u'l_c': f_to_c(forecast[u'temperatureLow']),
        u'weather': current[u'summary'],
        u'humid': int(current[u'humidity'] * 100),
        u'wind': u'Wind: {mph:.1f}mph/{kph:.1f}kph'.format(
            mph=current[u'windSpeed'],
            kph=mph_to_kph(current[u'windSpeed'])),
    }
    reply('{city}: {weather}, {t_f:.1f}F/{t_c:.1f}C'
          '(H:{h_f:.1f}F/{h_c:.1f}C L:{l_f:.1f}F/{l_c:.1f}C)'
          ', Humidity: {humid}%, {wind}'.format(**info))

    if inp and not dontsave:
        db.execute("insert or replace into "
                   "location(chan, nick, loc, lat, lon) "
                   "values (?, ?, ?, ?, ?)",
                   (chan, nick.lower(), inp, geo[u'lat'], geo[u'lng']))
        db.commit()
