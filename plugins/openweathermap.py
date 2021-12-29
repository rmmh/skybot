"""Weather, thanks to openweathermap and google geocoding."""
from __future__ import unicode_literals

import pendulum
from datetime import datetime

from util import hook, http

GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"
OWM_URL = "https://api.openweathermap.org/data/2.5/"


def geocode_location(api_key, loc):
    """Get a geocoded location from gooogle's geocoding api."""
    try:
        parsed_json = http.get_json(GEOCODING_URL, address=loc, key=api_key)
    except IOError:
        return None

    return parsed_json


def get_current_weather_data(api_key, lat, long):
    """Get weather data from openweathermap."""
    query = f"weather?lat={lat}&lon={long}&appid={api_key}&units=imperial"
    url = OWM_URL + query
    try:
        parsed_json = http.get_json(url)
    except IOError:
        return None

    return parsed_json


def get_forecast_data(api_key, lat, long):
    """Get weather forecast data from openweathermap."""
    query = f"forecast?lat={lat}&lon={long}&appid={api_key}&units=imperial"
    url = OWM_URL + query
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


def format_forecast(u_time, conditions, temp, tzoffset):
    """format forecast for output"""
    f_time = make_dayname(u_time, tzoffset)
    f_temp = format_temp(temp)
    f_forecast = "| \x02{}\x02 :: \x02{}\x02 - {} ".format(f_time, conditions, f_temp)
    return f_forecast 
    

def format_temp(temp):
    """format temp for forecast that is a bit more sane"""
    first_digit = str(round(temp))[0]
    end_digit = str(round(temp))[-1]
    if len(str(round(temp))) > 2:
        first_digit = "10"
    if end_digit == "0" or end_digit == "1" or end_digit == "2":
        temp_mod = "Lower"
    if end_digit == "3" or end_digit == "4" or end_digit == "5" or end_digit == "6":
        temp_mod = "Mid"
    if end_digit == "7" or end_digit == "8" or end_digit == "9":
        temp_mod = "Upper"
    temp_string = "{} {}0s".format(temp_mod, first_digit)
    return temp_string


def make_dayname(utcts, tzoffset):
    """convert offset datetime to something readable"""
    ts = utcts + tzoffset

    if pendulum:
        dt = pendulum.from_timestamp(ts)
        return dt.format('dddd hA')
    return ts
    

@hook.api_key("google", "openweathermap")
@hook.command("w",autohelp=False)
@hook.command(autohelp=False)
def weather(inp, chan="", nick="", reply=None, db=None, api_key=None):
    """.weather <location> [dontsave] | @<nick> -- Get weather data."""
    if "google" not in api_key and "openweathermap" not in api_key:
        return None

    # this database is used by other plugins interested in user's locations,
    # like .near in tag.py
    db.execute(
        "create table if not exists "
        "location(chan, nick, loc, lat, lon, primary key(chan, nick))"
    )

    if inp[0:1] == "@":
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
            (chan, nick),
        ).fetchone()
        if not loc:
            return weather.__doc__
        addr, lat, lng = loc
    else:
        location = geocode_location(api_key["google"], loc)

        if not location or location.get("status") != "OK":
            reply("Failed to determine location for {}".format(inp))
            return

        geo = location.get("results", [{}])[0].get("geometry", {}).get("location", None)
        if not geo or "lat" not in geo or "lng" not in geo:
            reply("Failed to determine location for {}".format(inp))
            return

        addr = location["results"][0]["formatted_address"]
        lat = geo["lat"]
        lng = geo["lng"]

    current = get_current_weather_data(api_key["openweathermap"], lat, lng)

    if not current:
        reply("Failed to get weather data for {}".format(inp))
        return

    forecast_data = get_forecast_data(api_key["openweathermap"], lat, lng)
    
    tzoffset = forecast_data['city']['timezone']

    forecast_list = [forecast for forecast in forecast_data["list"][1::2]]

    forecast_string = ""

    for x in range(0,3):
        forecast_string += format_forecast(
            forecast_list[x]["dt"], 
            forecast_list[x]["weather"][0]["main"], 
            forecast_list[x]["main"]["temp"], 
            tzoffset
        )

    info = {
        "city": current["name"],
        "country": current["sys"]["country"],
        "t_f": current['main']["temp"],
        "t_c": f_to_c(current['main']["temp"]),
        "conditions": current["weather"][0]["description"],
        "humid": current["main"]["humidity"],
        "wind": "\x02Wind\x02: {mph:.1f}mph/{kph:.1f}kph".format(
            mph=current["wind"]["speed"], 
            kph=mph_to_kph(current["wind"]["speed"])
            ),
        # "gust":"\x02 / \x02{mph:.1f}mph/{kph:.1f}kph".format(
        #     mph=current["wind"]["gust"], 
        #     kph=mph_to_kph(current["wind"]["gust"])
        #     )
    
    }

    reply("(\x02{city}, {country}\x02) :: \x02{conditions}\x02 | " \
        "\x02Temp\x02: {t_f:.1f}F/{t_c:.1f}C | " \
        "\x02Humidity\x02: {humid}% | " \
        "{wind} ".format(**info) + forecast_string)
    

    if inp and not dontsave:
        db.execute(
            "insert or replace into "
            "location(chan, nick, loc, lat, lon) "
            "values (?, ?, ?, ?, ?)",
            (chan, nick.lower(), addr, lat, lng),
        )
        db.commit()
