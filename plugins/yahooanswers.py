from util import hook, http
from random import choice

@hook.command
def answer(inp, bot=None):
    ".answer <query> -- find the answer to a question on Yahoo! Answers"

    url = "http://answers.yahooapis.com/AnswersService/V1/questionSearch"
    app_id = bot.config.get("api_keys", {}).get("yahoo", None)

    if app_id is None:
        return "error: yahoo appid not set"

    result = http.get_json(url,
                query=inp,
                search_in="question",
                output="json",
                appid=app_id)

    questions = result.get("all", {}).get("questions", [])
    answered = filter(lambda x: x.get("ChosenAnswer", ""), questions)

    if not answered:
        return "no results"

    chosen = choice(answered)
    answer, link = chosen["ChosenAnswer"], chosen["Link"]
    response = "%s -- %s" % (link, answer)

    return " ".join(response.split())

