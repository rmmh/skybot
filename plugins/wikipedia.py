"""Searches wikipedia and returns first sentence of article
Scaevolus 2009"""


import re

from util import hook, http


OUTPUT_LIMIT = 240  # character limit
INSTANCES = {
    "encyclopediadramatica": {
        "name": "Encyclopedia Dramatica",
        "search": "https://encyclopediadramatica.wiki/api.php",
        "regex": r"(https?://encyclopediadramatica\.wiki/index\.php/[^ ]+)",
    },
    "wikipedia_en": {
        "name": "Wikipedia",
        "search": "https://en.wikipedia.org/w/api.php",
        "regex": r"(https?://en\.wikipedia\.org/wiki/[^ ]+)",
    },
}


def search(instance, query):
    if instance not in INSTANCES:
        return

    wiki = INSTANCES[instance]
    search = http.get_json(
        wiki["search"],
        query_params={
            "action": "opensearch",
            "format": "json",
            "limit": 2,
            "search": query,
        },
    )

    print(search)

    titles = search[1]
    descriptions = search[2]
    urls = search[3]

    return (titles, descriptions, urls)


def scrape_text(url):
    h = http.get_html(url)

    title = h.xpath("string(//h1[@id='firstHeading'])")
    body = h.xpath("//div[@id='mw-content-text']/descendant-or-self::p")

    if title:
        title = title.strip()

    if body is None:
        return "Error reading the article"

    output = []

    for paragraph in body:
        text = paragraph.text_content()
        if len(text) > 4:  # skip empty paragraphs
            output.append(text)

    output = " ".join(output)

    return output, title


def command_wrapper(instance, inp):
    titles, descriptions, urls = search(instance, inp)

    if not titles:
        return "No results found."

    title = titles[0]
    url = urls[0]

    # `real_title` shows the article title after a
    # redirect. its generally longer than `title`
    print(url)
    output, real_title = scrape_text(url)

    if len(output) > OUTPUT_LIMIT:
        output = output[:OUTPUT_LIMIT] + "..."

    if title == real_title:
        return "\x02{} -\x02 {} \x02-\x02 {}".format(title, output, url)
    else:
        return "\x02{} -\x02 {} \x02-\x02 {} (redirected from {})".format(
            real_title, output, url, title
        )


def url_wrapper(instance, url):
    output, title = scrape_text(url)

    if len(output) > OUTPUT_LIMIT:
        output = output[:OUTPUT_LIMIT] + "..."

    return "\x02{} -\x02 {}".format(title, output)


@hook.command("ed")
@hook.command
def drama(inp):
    "drama <article> -- search an Encyclopedia Dramatica article"
    return command_wrapper("encyclopediadramatica", inp)


@hook.command("w")
@hook.command
def wikipedia(inp):
    "wikipedia <article> -- search a wikipedia article"
    return command_wrapper("wikipedia_en", inp)
