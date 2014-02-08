from util import hook, http
from random import choice


@hook.api_key('yahoo')
@hook.command
def answer(inp, api_key=None):
    ".answer <query> -- find the answer to a question on Yahoo! Answers"

    url = "http://answers.yahooapis.com/AnswersService/V1/questionSearch"

    result = http.get_json(url,
                           query=inp,
                           search_in="question",
                           output="json",
                           appid=api_key)

    questions = result.get("all", {}).get("questions", [])
    answered = filter(lambda x: x.get("ChosenAnswer", ""), questions)

    if not answered:
        return "no results"

    chosen = choice(answered)
    answer, link = chosen["ChosenAnswer"], chosen["Link"]
    response = "%s -- %s" % (answer, link)

    return " ".join(response.split())
