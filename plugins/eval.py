import base64
import re
import time

from util import hook, http

languages = {
    "bash": 1,
    "basic": 3,
    "c": 4,
    "cpp": 10,
    "c++": 10,
    "csharp": 16,
    "c#": 16,
    "clj": 18,
    "clojure": 18,
    "crystal": 19,
    "elixir": 20,
    "erlang": 21,
    "go": 22,
    "haskell": 23,
    "insect": 25,
    "java": 26,
    "js": 29,
    "javascript": 29,
    "node": 29,
    "ocaml": 31,
    "octave": 32,
    "pascal": 33,
    "python": 34,
    "py": 34,
    "py3": 34,
    "python3": 34,
    "py2": 36,
    "python2": 36,
    "ruby": 38,
    "rb": 38,
    "rust": 42,
}

statuses = {x["id"]: x for x in http.get_json("https://api.judge0.com/statuses")}


def get_result(token):
    url = "https://api.judge0.com/submissions/{}".format(token)

    try:
        result = http.get_json(url, get_method="GET")
    except http.HTTPError as e:
        # Request failed, API is probably down (or dead given our luck with repl apis)
        return e

    status = result.get("status")

    if not status:
        return "Bad response from Judge0 API. Try again later."

    status_id = status["id"]
    status_description = status["description"]

    if re.match(status_description, "Error"):
        return status_description

    # Processing, try again
    if status_id in [1, 2]:
        return None

    # Accepted and completed, return result and profiler stats
    if status_id == 3:
        return "[time: {time}, memory: {memory}] >> {stdout}".format(**result)


def submit_code(language, code):
    current_try = 0
    output = None

    url = "https://api.judge0.com/submissions"

    data = {"source_code": code, "language_id": languages[language]}

    try:
        result = http.get_json(url, post_data=data, get_method="POST")
    except http.HTTPError as e:
        return e

    token = result.get("token")

    if not token:
        return "Missing submission token in response. API is probably down."

    for n in range(10):
        output = get_result(token)

        if output:
            break

        time.sleep(1.3 ** n)

    if output:
        return output

    return "API took to long to return a response. Try again later."


@hook.command("eval")
def runcode(inp, autohelp=False):
    inputs = inp.split(" ")

    supported_languages = ", ".join(sorted(languages.keys()))

    try:
        arg1, arg2 = inp.split(None, 1)
    except ValueError:
        return "eval <language> <code> - evaluate given code using language. Supported languages: {}".format(
            supported_languages
        )

    if arg1 not in languages.keys():
        return "Language not supported, supported languages: {}".format(
            supported_languages
        )

    arg2 = " ".join(inputs[1:])

    return submit_code(arg1, arg2)
