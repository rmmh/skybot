
import re

from util import hook, http
from urllib.error import HTTPError


@hook.command("u")
@hook.command
def urban(inp):
    """.u/.urban <phrase> -- looks up <phrase> on urbandictionary.com"""

    page = http.get_json("https://api.urbandictionary.com/v0/define", term=inp)
    defs = page["list"]

    if not defs:
        return "not found."

    out = defs[0]["word"] + ": " + defs[0]["definition"].replace("\r\n", " ")

    if len(out) > 400:
        out = out[: out.rfind(" ", 0, 400)] + "..."

    return out


# define plugin by GhettoWizard & Scaevolus
@hook.command("dictionary")
@hook.command
def define(inp):
    ".define/.dictionary <word> -- fetches definition of <word>"

    url = "http://ninjawords.com/"

    h = http.get_html(url + http.quote_plus(inp))

    definition = h.xpath(
        '//dd[@class="article"] | '
        '//div[@class="definition"] |'
        '//div[@class="example"]'
    )

    if not definition:
        return "No results for " + inp

    def format_output(show_examples):
        result = "%s: " % h.xpath('//dt[@class="title-word"]/a/text()')[0]

        correction = h.xpath('//span[@class="correct-word"]/text()')
        if correction:
            result = 'definition for "%s": ' % correction[0]

        sections = []
        for section in definition:
            if section.attrib["class"] == "article":
                sections += [[section.text_content() + ": "]]
            elif section.attrib["class"] == "example":
                if show_examples:
                    sections[-1][-1] += " " + section.text_content()
            else:
                sections[-1] += [section.text_content()]

        for article in sections:
            result += article[0]
            if len(article) > 2:
                result += " ".join(
                    "%d. %s" % (n + 1, section) for n, section in enumerate(article[1:])
                )
            else:
                result += article[1] + " "

        synonyms = h.xpath('//dd[@class="synonyms"]')
        if synonyms:
            result += synonyms[0].text_content()

        result = re.sub(r"\s+", " ", result)
        result = re.sub("\xb0", "", result)
        return result

    result = format_output(True)
    if len(result) > 450:
        result = format_output(False)

    if len(result) > 450:
        result = result[: result.rfind(" ", 0, 450)]
        result = re.sub(r"[^A-Za-z]+\.?$", "", result) + " ..."

    return result


@hook.command("e")
@hook.command
def etymology(inp):
    ".e/.etymology <word> -- Retrieves the etymology of chosen word"

    try:
        h = http.get_html(f'https://www.etymonline.com/word/{http.quote_plus(inp)}')
        etym = h.xpath('//section[starts-with(@class, "prose-lg")]/section')[0].text_content()
    except IndexError:
        return "No etymology found for " + inp
    except HTTPError:
        return "No etymology found for " + inp

    etym = etym.replace(inp, "\x02%s\x02" % inp)

    if len(etym) > 400:
        etym = etym[: etym.rfind(" ", 0, 400)] + " ..."

    return etym
