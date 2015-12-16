"weather, thanks to wunderground"

from util import hook, http


@hook.api_key('wunderground')
@hook.command(autohelp=False)
def weather(inp, chan='', nick='', reply=None, db=None, api_key=None):
    ".weather <location> [dontsave] | @<nick> -- gets weather data from " \
        "Wunderground http://wunderground.com/weather/api"

    if not api_key:
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

    params = [http.quote(p.strip()) for p in loc.split(',')]

    loc = params[0]
    state = ''

    # Try to interpret the query based on the number of commas.
    # Two commas might be city-state  city-country, or lat-long pair
    if len(params) == 2:

        state = params[1]

        # Check to see if a lat, long pair is being passed. This could be done
        # more completely with regex, and converting from DMS to decimal
        # degrees. This is nice and simple, however.
        try:
            float(loc)
            float(state)

            loc = loc + ',' + state
            state = ''
        except ValueError:
            state += '/'

    # Assume three commas is a city-state-country triplet. Discard the state
    # portion because that's what the API expects
    elif len(params) == 3:
        loc = params[0]
        state = params[2] + '/'

    url = 'http://api.wunderground.com/api/'
    query = '{key}/geolookup/conditions/forecast/q/{state}{loc}.json' \
            .format(key=api_key, state=state, loc=loc)
    url += query

    try:
        parsed_json = http.get_json(url)
    except IOError:
        return 'Could not get data from Wunderground'

    info = {}
    if 'current_observation' not in parsed_json:
        resp = 'Could not find weather for {inp}. '.format(inp=inp)

        # In the case of no observation, but results, print some possible
        # location matches
        if 'results' in parsed_json['response']:
            resp += 'Possible matches include: '
            results = parsed_json['response']['results']

            for place in results[:6]:
                resp += '{city}, '.format(**place)

                if place['state']:
                    resp += '{state}, '.format(**place)

                if place['country_name']:
                    resp += '{country_name}; '.format(**place)

            resp = resp[:-2]

        reply(resp)
        return

    obs = parsed_json['current_observation']
    sf = parsed_json['forecast']['simpleforecast']['forecastday'][0]
    info['city'] = obs['display_location']['full']
    info['t_f'] = obs['temp_f']
    info['t_c'] = obs['temp_c']
    info['weather'] = obs['weather']
    info['h_f'] = sf['high']['fahrenheit']
    info['h_c'] = sf['high']['celsius']
    info['l_f'] = sf['low']['fahrenheit']
    info['l_c'] = sf['low']['celsius']
    info['humid'] = obs['relative_humidity']
    info['wind'] = 'Wind: {mph}mph/{kph}kph' \
        .format(mph=obs['wind_mph'], kph=obs['wind_kph'])
    reply('{city}: {weather}, {t_f}F/{t_c}C'
          '(H:{h_f}F/{h_c}C L:{l_f}F/{l_c}C)'
          ', Humidity: {humid}, {wind}'.format(**info))

    lat = float(obs['display_location']['latitude'])
    lon = float(obs['display_location']['longitude'])

    if inp and not dontsave:
        db.execute("insert or replace into "
                   "location(chan, nick, loc, lat, lon) "
                   "values (?, ?, ?, ?, ?)",
                   (chan, nick.lower(), inp, lat, lon))
        db.commit()
