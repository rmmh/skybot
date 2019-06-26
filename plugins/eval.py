import base64
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


def get_result(token):
    url = "https://api.judge0.com/submissions/{}".format(token)

    try:
        result = http.get_json(url, get_method="GET")
    except http.HTTPError as e:
        return None

    status = result.get("status", {"id": 2})
    status_id = status["id"]

    # Processing, try again
    if status_id not in [3, 6, 11]:
        return None

    # Compilation error
    if status_id == 6:
        return "compilation error: {}".format(result["compile_output"])

    # Runtime error
    if status_id == 11:
        return "runtime error: {}".format(result["stderr"])

    if status_id == 3:
        return "[time: {time}, memory: {memory}] >> {stdout}".format(**result)


def submit_code(language, code):
    current_try = 0
    output = None

    url = "https://api.judge0.com/submissions?base64_encoded=true"

    encoded_code = base64.b64encode(code.encode())

    data = {"source_code": encoded_code, "language_id": languages[language]}

    try:
        result = http.get_json(url, post_data=data, get_method="POST")
    except http.HTTPError as e:
        return e

    token = result.get("token")

    if not token:
        return "Missing submission token in response. API is probably down."

    while current_try <= 5:
        time.sleep(1)

        output = get_result(token)

        if output:
            break

        current_try += 1

    if output:
        return output

    return "API took to long to return a response. Try again later."


@hook.command("eval")
def runcode(inp):
    inputs = inp.split(" ")

    arg1 = inputs[0]

    if arg1 not in languages.keys():
        return "Language not supported, supported languages: {}".format(
            ", ".join(languages.keys())
        )

    arg2 = " ".join(inputs[1:])

    return submit_code(arg1, arg2)
