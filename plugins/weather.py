"weather, thanks to google"

from lxml import etree
import urllib

from util import hook


@hook.command
def weather(bot, input):
    ".weather <location> [dontsave] -- queries the google weather API for weather data"
    loc = input.inp

    dontsave = loc.endswith(" dontsave")
    if dontsave:
        loc = loc[:-9].strip().lower()

    conn = bot.get_db_connection(input.server)
    conn.execute("create table if not exists weather(nick primary key, loc)")

    if not loc: # blank line
        loc = conn.execute("select loc from weather where nick=lower(?)",
                            (input.nick,)).fetchone()
        if not loc:
            return weather.__doc__
        loc = loc[0]

    data = urllib.urlencode({'weather': loc.encode('utf-8')})
    url = 'http://www.google.com/ig/api?' + data
    w = etree.parse(url).find('weather')

    if w.find('problem_cause') is not None:
        return "Couldn't fetch weather data for '%s', try using a zip or " \
                "postal code." % input.inp

    info = dict((e.tag, e.get('data')) for e in w.find('current_conditions'))
    info['city'] = w.find('forecast_information/city').get('data')
    info['high'] = w.find('forecast_conditions/high').get('data')
    info['low'] = w.find('forecast_conditions/low').get('data')

    input.reply('%(city)s: %(condition)s, %(temp_f)sF/%(temp_c)sC (H:%(high)sF'\
            ', L:%(low)sF), %(humidity)s, %(wind_condition)s.' % info)

    if input.inp and not dontsave:
        conn.execute("insert or replace into weather(nick, loc) values (?,?)",
                     (input.nick.lower(), loc))
        conn.commit()
