from __future__ import unicode_literals

from builtins import chr
import re
import urllib.parse

from util import hook, http


@hook.api_key("wolframalpha")
@hook.command("who")
@hook.command("what")
@hook.command("where")
@hook.command("when")
@hook.command("why")
@hook.command
def ask(inp, say=None, trigger=None, nick=None, api_key=None):
    ".ask <query> -- ask wolfram a question, get an answer"

    if trigger in ["who", "what", "where", "when", "why"]:
        inp = f"{trigger} {inp}"

    base_url = "http://api.wolframalpha.com/v1/conversation.jsp"
    query = urllib.parse.quote_plus(inp)
    url = f"{base_url}?appid={api_key}&i={query}"

    response = http.get_json(url)
    result = response.get("result")

    if not result:
        say(f"Sorry, I do not know how to answer that {nick}.")

    return result


@hook.api_key("wolframalpha")
@hook.command("wa")
@hook.command
def wolframalpha(inp, api_key=None):
    ".wa/.wolframalpha <query> -- computes <query> using Wolfram Alpha"

    url = "http://api.wolframalpha.com/v2/query?format=plaintext"

    result = http.get_xml(url, input=inp, appid=api_key)

    pod_texts = []
    for pod in result.xpath("//pod"):
        title = "" if pod.attrib["title"] == "Result" else pod.attrib["title"] + ": "
        if pod.attrib["id"] == "Input":
            continue

        results = []
        for subpod in pod.xpath("subpod/plaintext/text()"):
            subpod = subpod.strip().replace("\\n", "; ")
            subpod = re.sub(r"\s+", " ", subpod)
            if subpod:
                results.append(subpod)
        if results:
            pod_texts.append(title + "|".join(results))

    ret = ". ".join(pod_texts)

    if not pod_texts:
        return "no results"

    ret = re.sub(r"\\(.)", r"\1", ret)

    def unicode_sub(match):
        return chr(int(match.group(1), 16))

    ret = re.sub(r"\\:([0-9a-z]{4})", unicode_sub, ret)

    if len(ret) > 430:
        ret = ret[: ret.rfind(" ", 0, 430)]
        ret = re.sub(r"\W+$", "", ret) + "..."

    if not ret:
        return "no results"

    return ret
