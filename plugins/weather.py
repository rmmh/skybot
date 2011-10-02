"weather, thanks to google"

from util import hook, http

def fetch(inp, nick='', server='', reply=None, db=None, forecast=None):
    
    loc = inp

    dontsave = loc.endswith(" dontsave")
    if dontsave:
        loc = loc[:-9].strip().lower()

    db.execute("create table if not exists weather(nick primary key, loc)")

    if not loc:  # blank line
        loc = db.execute("select loc from weather where nick=lower(?)",
                            (nick,)).fetchone()
        if not loc:
            if forecast is not None:
                return forecast.__doc__
            else:
                return weather.__doc__

        loc = loc[0]

    w = http.get_xml('http://www.google.com/ig/api', weather=loc)
    w = w.find('weather')

    if w.find('problem_cause') is not None:
        return "Couldn't fetch weather data for '%s', try using a zip or " \
                "postal code." % inp

    if forecast is not None:
        info = dict((e.tag, e.get('data')) for e in w.find('current_conditions'))
        info['city'] = w.find('forecast_information/city').get('data')
        reply_string = "%s: " % info['city']
        for e in w.findall('forecast_conditions'):
            day = e.find('day_of_week').get('data')
            high = e.find('high').get('data')
            low = e.find('low').get('data')
            reply_string += "%s: %sF/%sF, " % (day, high, low)
        reply_string = reply_string[:-2]
    else:
        info = dict((e.tag, e.get('data')) for e in w.find('current_conditions'))
        info['city'] = w.find('forecast_information/city').get('data')
        info['high'] = w.find('forecast_conditions/high').get('data')
        info['low'] = w.find('forecast_conditions/low').get('data')
        reply_string = '%(city)s: %(condition)s, %(temp_f)sF/%(temp_c)sC (H:%(high)sF'', L:%(low)sF), %(humidity)s, %(wind_condition)s.' % info
	
    reply(reply_string)

    if inp and not dontsave:
        db.execute("insert or replace into weather(nick, loc) values (?,?)",
                     (nick.lower(), loc))
        db.commit()

@hook.command(autohelp=False)
def weather(inp, nick='', server='', reply=None, db=None):
    ".weather <location> [dontsave] -- gets weather data from Google"

    fetch(inp, nick, server, reply, db)

@hook.command(autohelp=False)
def forecast(inp, nick='', server='', reply=None, db=None):
    ".forecast <location> [dontsave] -- gets weather forecast data from Google"

    fetch(inp, nick, server, reply, db, True)
