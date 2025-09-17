
import json
import re

from util import hook, http


SEARCH_URL = (
    "https://yfrdx308zd-dsn.algolia.net/1/indexes/wp_live_searchable_posts/query"
    "?x-algolia-application-id=YFRDX308ZD&x-algolia-api-key=7da15c5275374261c3a4bdab2ce5d321"
)


@hook.command
def snopes(inp):
    ".snopes <topic> -- searches snopes for an urban legend about <topic>"

    params = {"params": http.urlencode({"query": inp, "hitsPerPage": 5})}
    results = http.get_json(SEARCH_URL, post_data=json.dumps(params).encode("utf8"))[
        "hits"
    ]

    if not results:
        return "no matching pages found"

    post = results[0]
    for post in results:
        if post["post_type"] == "fact_check":
            return fmt(post)


def fmt(post):
    permalink = post["permalink"]

    if "fact_check_claim" in post:
        claim = post["fact_check_claim"]
        if post["taxonomies"].get("fact_check_category") == ["Fake News"]:
            status = "Fake News"
        else:
            status = post["taxonomies"]["fact_check_rating"][0]
    else:
        content = post["content"]
        m = re.search(r"(?:Claim|Glurge|Legend|FACT CHECK): (.*)", content)
        if m:
            claim = m.group(1).strip()
        else:
            claim = content.split("\n")[0]
            print("???", claim)
        if claim == "Claim":
            print("!!!", content)
        m = re.search(
            r"FALSE|TRUE|MIXTURE|UNDETERMINED|CORRECTLY ATTRIBUTED|(?<=Status:).*",
            content,
        )
        if m:
            status = m.group(0)
        else:
            status = "???"

    claim = re.sub(
        r"[\s\xa0]+", " ", http.unescape(claim)
    ).strip()  # compress whitespace
    status = re.sub(r"[\s\xa0]+", " ", http.unescape(status)).title().strip()

    if len(claim) > 300:
        claim = claim[:300] + "..."

    return "Claim: {0} Status: {1} {2}".format(claim, status, permalink)


if __name__ == "__main__":
    a = http.get_json(
        SEARCH_URL,
        post_data=json.dumps(
            {"params": http.urlencode({"query": "people", "hitsPerPage": 1000})}
        ).encode("utf8"),
    )
    print(len(a["hits"]))
    try:
        for x in a["hits"]:
            if x["post_type"] == "fact_check":
                f = fmt(x)
                print(f)
                assert len(f) < 400
    except AttributeError:
        print(x["permalink"])
        print(x["content"])
        raise
