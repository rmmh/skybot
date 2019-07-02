import time

from util import hook, http


languages = {}
statuses = {}


def fetch_languages():
    lang_list = http.get_json("https://api.judge0.com/languages")
    m = {x["name"].split()[0].lower(): x["id"] for x in lang_list[::-1]}
    m.pop("text")
    m.pop("executable")
    m["python2"] = [x["id"] for x in lang_list if x["name"].startswith("Python (2")][0]
    m["py"] = m["py3"] = m["python3"] = m["python"]
    m["py2"] = m["python2"]
    m["clj"] = m["clojure"]
    m["cpp"] = m["c++"]
    m["csharp"] = m["c#"]
    m["node"] = m["js"] = m["javascript"]
    m["rb"] = m["ruby"]

    return m


def get_result(token):
    url = "https://api.judge0.com/submissions/{}".format(token)

    try:
        result = http.get_json(url)
    except http.HTTPError as e:
        # Request failed, API is probably down (or dead given our luck with repl apis)
        return e

    status = result.get("status")

    if not status:
        return "Bad response from Judge0 API. Try again later."

    status_id = status["id"]
    status_description = status["description"]

    if "Error" in status_description:
        stderr = result.get("stderr", "")

        return "{} {}".format(status_description, stderr)

    # Processing, try again
    if status_id in [1, 2]:
        return None

    # Accepted and completed, return result and profiler stats
    if status_id == 3:
        return "({time}s {memory}) {stdout}".format(**result)


def submit_code(language, code):
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


@hook.command("eval", autohelp=False)
def runcode(inp):
    global languages
    global statuses

    if not languages:
        languages = fetch_languages()

    if not statuses:
        statuses = {
            x["id"]: x for x in http.get_json("https://api.judge0.com/statuses")
        }

    inputs = inp.split(" ")

    supported_languages = ", ".join(sorted(languages.keys()))

    try:
        arg1, arg2 = inp.split(None, 1)
    except ValueError:
        return "eval <language> <code> - evaluate given code using language. Supported languages: {}".format(
            supported_languages
        )

    if arg1 not in languages:
        return "Language not supported, supported languages: {}".format(
            supported_languages
        )

    arg2 = " ".join(inputs[1:])

    return submit_code(arg1, arg2)
