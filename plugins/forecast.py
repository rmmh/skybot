"4-day weather forecast, thanks to google"

from util import hook, http

@hook.command(autohelp=False)
def forecast(inp, nick='', server='', reply=None, db=None):
    ".forecast <location> [dontsave] -- gets weather forecast data from Google"

    loc = inp

    dontsave = loc.endswith(" dontsave")
    if dontsave:
        loc = loc[:-9].strip().lower()

    db.execute("create table if not exists weather(nick primary key, loc)")

    if not loc:  # blank line
        loc = db.execute("select loc from weather where nick=lower(?)",
                            (nick,)).fetchone()
        if not loc:
            return weather.__doc__
        loc = loc[0]

    w = http.get_xml('http://www.google.com/ig/api', weather=loc)
    w = w.find('weather')

    if w.find('problem_cause') is not None:
        return "Couldn't fetch weather data for '%s', try using a zip or " \
                "postal code." % inp

    info = dict((e.tag, e.get('data')) for e in w.find('current_conditions'))
    info['city'] = w.find('forecast_information/city').get('data')

    forecast_string = "%s: " % info['city']

    for e in w.findall('forecast_conditions'):
	    day = e.find('day_of_week').get('data')
	    high = e.find('high').get('data')
	    low = e.find('low').get('data')
	    forecast_string += "%s: %sF/%sF, " % (day, high, low)

    reply(forecast_string[:-2])

    if inp and not dontsave:
        db.execute("insert or replace into weather(nick, loc) values (?,?)",
                     (nick.lower(), loc))
        db.commit()
