"""
TV information, written by Lurchington 2010
modified by rmmh 2010, 2013
"""

import datetime

from util import hook, http, timesince


base_url = "https://api4.thetvdb.com/v4"
_tokens = {}


def get_token(api_key):
    """Exchange a v4 API key for a token."""
    if api_key in _tokens:
        return _tokens[api_key]

    response = http.get_json(base_url + "/login", json_data={"apikey": api_key})
    token = response["data"]["token"]
    _tokens[api_key] = token
    return token


def api_get(path, api_key, **params):
    def request(token):
        return http.get_json(
            base_url + path,
            headers={"Authorization": "Bearer " + token},
            **params
        )

    token = get_token(api_key)
    try:
        return request(token)
    except http.HTTPError as error:
        if error.code != 401:
            raise

    # Tokens are valid for one month. If the cached token expires while the
    # bot is running, authenticate again and retry the request once.
    _tokens.pop(api_key, None)
    return request(get_token(api_key))


def get_episodes_for_series(seriesname, api_key):
    res = {"error": None, "ended": False, "episodes": None, "name": None}
    try:
        matches = api_get(
            "/search", api_key, query=seriesname, type="series", limit=1
        ).get("data", [])
        if not matches:
            res["error"] = "unknown tv series (using www.thetvdb.com)"
            return res

        series_id = matches[0].get("tvdb_id") or matches[0]["id"]
        series = api_get(
            "/series/%s/extended" % series_id,
            api_key,
            meta="episodes",
            short="true",
        )
        series = series["data"]
    except (http.URLError, KeyError, TypeError):
        res["error"] = "error contacting thetvdb.com"
        return res

    status = series.get("status") or {}
    status_name = status.get("name") if isinstance(status, dict) else status
    res["name"] = series.get("name") or matches[0].get("name")
    res["ended"] = status_name == "Ended"
    res["episodes"] = sorted(
        series.get("episodes") or [], key=lambda episode: episode.get("aired") or ""
    )
    return res


def get_episode_info(episode):
    episode_air_date = episode.get("aired")
    season_number = episode.get("seasonNumber")
    episode_number = episode.get("number")
    episode_name = episode.get("name")

    try:
        airdate = datetime.datetime.strptime(episode_air_date, "%Y-%m-%d").date()
        episode_num = "S%02dE%02d" % (int(season_number), int(episode_number))
    except (ValueError, TypeError):
        return None

    # in the event of an unannounced episode title, users either leave the
    # field out (None) or fill it with TBA
    if episode_name == "TBA":
        episode_name = None

    episode_desc = "%s" % episode_num
    if episode_name:
        episode_desc += " - %s" % episode_name
    return (episode_air_date, airdate, episode_desc)


@hook.command
@hook.command("tv")
@hook.api_key("tvdb")
def tv_next(inp, api_key=None):
    ".tv_next <series> -- get the next episode of <series>"
    episodes = get_episodes_for_series(inp, api_key)

    if episodes["error"]:
        return episodes["error"]

    series_name = episodes["name"]
    ended = episodes["ended"]
    episodes = episodes["episodes"]

    if ended:
        return "%s has ended." % series_name

    next_eps = []
    today = datetime.date.today()

    for episode in reversed(episodes):
        ep_info = get_episode_info(episode)

        if ep_info is None:
            continue

        (episode_air_date, airdate, episode_desc) = ep_info

        if airdate > today:
            next_eps = [
                "%s (%s) (%s)"
                % (
                    episode_air_date,
                    timesince.timeuntil(
                        datetime.datetime.strptime(episode_air_date, "%Y-%m-%d")
                    ),
                    episode_desc,
                )
            ]
        elif airdate == today:
            next_eps = ["Today (%s)" % episode_desc] + next_eps
        else:
            # we're iterating in reverse order with newest episodes last
            # so, as soon as we're past today, break out of loop
            break

    if not next_eps:
        return "there are no new episodes scheduled for %s" % series_name

    if len(next_eps) == 1:
        return "the next episode of %s airs %s" % (series_name, next_eps[0])
    else:
        next_eps = ", ".join(next_eps)
        return "the next episodes of %s: %s" % (series_name, next_eps)


@hook.command
@hook.command("tv_prev")
@hook.api_key("tvdb")
def tv_last(inp, api_key=None):
    ".tv_last <series> -- gets the most recently aired episode of <series>"
    episodes = get_episodes_for_series(inp, api_key)

    if episodes["error"]:
        return episodes["error"]

    series_name = episodes["name"]
    ended = episodes["ended"]
    episodes = episodes["episodes"]

    prev_ep = None
    today = datetime.date.today()

    for episode in reversed(episodes):
        ep_info = get_episode_info(episode)

        if ep_info is None:
            continue

        (episode_air_date, airdate, episode_desc) = ep_info

        if airdate < today:
            # iterating in reverse order, so the first episode encountered
            # before today was the most recently aired
            prev_ep = "%s (%s)" % (episode_air_date, episode_desc)
            break

    if not prev_ep:
        return "there are no previously aired episodes for %s" % series_name
    if ended:
        return "%s ended. The last episode aired %s" % (series_name, prev_ep)
    return "the last episode of %s aired %s" % (series_name, prev_ep)
