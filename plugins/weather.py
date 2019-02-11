"""Weather, thanks to darksky and mapbox geocoding."""

from util import hook, http

DARKSKY_URL = u'https://api.darksky.net/forecast/'
GEOCODING_URL = u'https://api.mapbox.com/geocoding/v5/mapbox.places/{search_text}.json'


def geocode_location(api_key, loc):
    """Get a geocoded location from gooogle's geocoding api."""
    try:
        parsed_json = http.get_json(GEOCODING_URL.format(search_text=loc), access_token=api_key)
    except IOError:
        return None

    return parsed_json


def get_weather_data(api_key, lat, long):
    """Get weather data from darksky."""
    query = '{key}/{lat},{long}'.format(key=api_key, lat=lat, long=long)
    url = DARKSKY_URL + query
    try:
        parsed_json = http.get_json(url)
    except IOError:
        return None

    return parsed_json


def f_to_c(temp_f):
    """Convert F to C."""
    return (temp_f - 32) * 5 / 9


def mph_to_kph(mph):
    """Convert mph to kph."""
    return mph * 1.609


@hook.api_key('mapbox', 'darksky')
@hook.command(autohelp=False)
def weather(inp, chan='', nick='', reply=None, db=None, api_key=None):
    """.weather <location> [dontsave] | @<nick> -- Get weather data."""
    if 'mapbox' not in api_key and 'darksky' not in api_key:
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
            "select loc, lat, lon from location where chan=? and nick=lower(?)",
            (chan, nick)).fetchone()
        if not loc:
            return weather.__doc__
        addr, lat, lng = loc
    else:
        location = geocode_location(api_key['mapbox'], loc)

        if not location:
            reply('Failed to determine location for {}'.format(inp))
            return

        geo = location.get(u'features', [{}])[0].get(u'center', None)
        if not geo or len(geo) != 2:
            reply('Failed to determine location for {}'.format(inp))
            return

        addr = location.get(u'features', [{}])[0].get(u'place_name', None)
        lng = geo[0]
        lat = geo[1]

    parsed_json = get_weather_data(api_key['darksky'], lat, lng)
    if not parsed_json:
        reply('Failed to get weather data for {}'.format(inp))
        return

    current = parsed_json.get(u'currently')

    if not current:
        reply('Failed to get weather data for {}'.format(inp))
        return

    forecast = parsed_json['daily']['data'][0]

    info = {
        'city': addr,
        't_f': current[u'temperature'],
        't_c': f_to_c(current[u'temperature']),
        'h_f': forecast[u'temperatureHigh'],
        'h_c': f_to_c(forecast[u'temperatureHigh']),
        'l_f': forecast[u'temperatureLow'],
        'l_c': f_to_c(forecast[u'temperatureLow']),
        'weather': current[u'summary'],
        'humid': int(current[u'humidity'] * 100),
        'wind': u'Wind: {mph:.1f}mph/{kph:.1f}kph'.format(
            mph=current[u'windSpeed'],
            kph=mph_to_kph(current[u'windSpeed'])),
        'forecast': parsed_json.get('hourly', {}).get('summary', ''),
    }
    reply(u'{city}: {weather}, {t_f:.1f}F/{t_c:.1f}C'
          '(H:{h_f:.1f}F/{h_c:.1f}C L:{l_f:.1f}F/{l_c:.1f}C)'
          ', Humidity: {humid}%, {wind} \x02{forecast}\x02'.format(**info))

    if inp and not dontsave:
        db.execute("insert or replace into "
                   "location(chan, nick, loc, lat, lon) "
                   "values (?, ?, ?, ?, ?)",
                   (chan, nick.lower(), addr, lat, lng))
        db.commit()
