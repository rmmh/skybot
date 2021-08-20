import time
import uuid
import json

from util import hook, http


def piston(language, version, content, filename=None):
    api_url = "https://emkc.org/api/v2/piston/execute"

    if not filename:
        filename = str(uuid.uuid1())

    payload = {
        "language": language,
        "version": version,
        "files": [{"name": filename, "content": content}],
        "stdin": "",
        "args": [],
        "compile_timeout": 5000,
        "run_timeout": 5000,
        "compile_memory_limit": -1,
        "run_memory_limit": -1,
    }

    headers = {"Content-Type", "application/json"}

    result = http.get_json(api_url, json_data=payload, get_methods="POST")

    if result["run"]["stderr"] != "":
        return f"Error: " + result["run"]["stderr"]

    return result["run"]["output"].replace("\n", " ")


@hook.command("py")
@hook.command("py3")
def python(inp):
    return piston("python", "3.9.4", inp)


@hook.command("py2")
def python2(inp):
    return piston("python2", "2.7.18", inp)


@hook.command("rb")
def ruby(inp):
    return piston("ruby", "3.0.1", inp)


@hook.command("ts")
def typescript(inp):
    return piston("typescript", "4.2.3", inp)


@hook.command("js")
@hook.command("node")
def javascript(inp):
    return piston("javascript", "16.3.0", inp)


@hook.command
def perl(inp):
    return piston("perl", "5.26.1", inp)


@hook.command
def php(inp):
    return piston("php", "8.0.2", inp)


@hook.command
def swift(inp):
    return piston("swift", "5.3.3", inp)


if __name__ == "__main__":
    result = piston("py", "3.9.4", "print('test')")

    print(result)
