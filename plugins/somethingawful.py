
import re

from util import hook, http


SA_THREAD_RE = r"(?i)forums\.somethingawful\.com/\S*\?(?:\S+&)?threadid=(\d+)\S*"
SA_PROFILE_RE = (
    r"(?i)forums\.somethingawful\.com/member.php\?\S+(userid|username)=([^&]+)"
)

LOGIN_URL = "https://forums.somethingawful.com/account.php"
THREAD_URL = "https://forums.somethingawful.com/showthread.php"
PROFILE_URL = "https://forums.somethingawful.com/member.php"

MATCH_OBJECT = type(re.match(r"", ""))  # Is there a nicer way to get this??

GENDER_UNICODE = {"male": "\u2642", "female": "\u2640", "porpoise": "\uE520"}

FORUM_ABBREVS = {
    "Serious Hardware / Software Crap": "SHSC",
    "The Cavern of COBOL": "CoC",
    "General Bullshit": "GBS",
    "Haus of Tech Support": "HoTS",
}


def login(user, password):
    """
    Authenticate against SomethingAwful, both storing that authentication in
    the global cookiejar and returning the relevant cookies

    :param user: your awful username for somethingawful dot com
    :param password: your awful password for somethingawful dot com
    :return: the authentication cookies for somethingawful dot com
    """

    get_sa_cookies = lambda jar: [
        c
        for c in jar
        if c.domain.endswith("forums.somethingawful.com")
        and (c.name == "bbuserid" or c.name == "bbpassword")
    ]

    http.clear_expired_cookies()
    sa_cookies = get_sa_cookies(http.get_cookie_jar())

    if len(sa_cookies) == 2:
        return sa_cookies

    post_data = {"action": "login", "username": user, "password": password}
    http.get(LOGIN_URL, cookies=True, post_data=post_data)

    sa_cookies = get_sa_cookies(http.get_cookie_jar())

    if len(sa_cookies) < 2:
        return None

    return sa_cookies


def parse_profile_html(document):
    """
    Parse an LXML document to retrieve the profile data

    :param document: the LXML document to parse
    :return: a dictionary representing the profile
    """
    username_elements = document.xpath("//*[@class='author']")
    registered_elements = document.xpath("//*[@class='registered']")
    avatar_elements = document.xpath("//*[@class='title']//img")
    info_elements = document.xpath("//*[@class='info']")
    userid_elements = document.xpath("//*[@name='userid']")

    profile = {}

    if userid_elements:
        profile["id"] = userid_elements[0].attrib["value"]

    if username_elements:
        profile["username"] = username_elements[0].text_content()

    if registered_elements:
        profile["registered"] = registered_elements[0].text_content()

    if avatar_elements:
        profile["avatar"] = (
            avatar_elements[0].attrib["src"] if avatar_elements[0].attrib["src"] else ""
        )
        profile["is_newbie"] = profile["avatar"].endswith("/images/newbie.gif")

    if info_elements:
        info_text = info_elements[0].text_content()

        post_count = re.search(r"Post Count(\d+)", info_text)
        if post_count:
            profile["post_count"] = post_count.group(1)

        post_rate = re.search(r"Post Rate([\d\.]+)", info_text)
        if post_rate:
            profile["post_rate"] = post_rate.group(1)

        last_post = re.search(r"Last Post(.+)", info_text)
        if last_post:
            profile["last_post"] = last_post.group(1)

        gender = re.search(r"claims to be a ([-a-z0-9 ]+)", info_text)
        if gender:
            profile["gender"] = gender.group(1).lower()

    if "id" in profile:
        profile["profile_link"] = http.prepare_url(
            PROFILE_URL, {"action": "getinfo", "userid": profile["id"]}
        )
    elif "username" in profile:
        profile["profile_link"] = http.prepare_url(
            PROFILE_URL, {"action": "getinfo", "username": profile["username"]}
        )

    return profile


def parse_thread_html(document):
    """
    Parse an LXML document to retrieve the thread data

    :param document: the LXML document to parse
    :return: a dictionary representing the thread
    """
    breadcrumbs_elements = document.xpath("//div[@class='breadcrumbs']//a")
    author_elements = document.xpath("//dt[contains(@class, author)]")
    last_page_elements = document.xpath("//a[@title='Last page']")

    if not breadcrumbs_elements:
        return

    if not author_elements:
        return

    if len(breadcrumbs_elements) < 2:
        return

    thread_id = int(breadcrumbs_elements[-1].attrib["href"].rsplit("=", 2)[1])

    breadcrumbs = [e.text_content() for e in breadcrumbs_elements]

    thread_title = breadcrumbs[-1]
    forum_title = breadcrumbs[-2]

    if author_elements:
        author = author_elements[0].text_content().strip()
    else:
        author = "Unknown Author"

    # Handle GBS / FYAD / E/N / etc
    if ":" in forum_title:
        forum_title = forum_title.split(":")[0].strip()

    if forum_title in FORUM_ABBREVS:
        forum_title = FORUM_ABBREVS[forum_title]

    if last_page_elements:
        post_count = int(last_page_elements[0].text_content().split(" ")[0])
    else:
        post_count = 1

    posts = {
        x.attrib["id"]: (
            x.xpath('.//dt[contains(@class, "author")]')[0].text_content(),
            x.xpath('.//*[@class="postdate"]')[0].text_content().strip("\n #?"),
            x.xpath('.//*[@class="postbody"]')[0].text_content().strip(),
        )
        for x in document.xpath('//table[contains(@class, "post")]')
    }

    return {
        "id": thread_id,
        "breadcrumbs": breadcrumbs,
        "forum_title": forum_title,
        "thread_title": thread_title,
        "author": author,
        "post_count": post_count,
        "posts": posts,
        "thread_link": http.prepare_url(THREAD_URL, {"threadid": thread_id}),
    }


def get_thread_by_id(credentials, id, params=None):
    """
    Get thread data via the ID of the thread

    :param credentials: the credentials to lookup with
    :param id: the ID to look up
    :return: a dictionary representing the thread
    """
    if not login(credentials["user"], credentials["password"]):
        raise ValueError("invalid login")

    thread_document = http.get_html(
        THREAD_URL,
        cookies=True,
        query_params=params or {"noseen": 1, "threadid": id, "perpage": 1},
    )

    return parse_thread_html(thread_document)


def get_profile_by_id(credentials, id):
    """
    Get profile data via the ID of a user

    :param credentials: the credentials to lookup with
    :param id: the ID to look up
    :return: a dictionary representing a profile
    """
    if not login(credentials["user"], credentials["password"]):
        raise ValueError("invalid login")

    profile_document = http.get_html(
        PROFILE_URL, cookies=True, query_params={"action": "getinfo", "userid": id}
    )

    return parse_profile_html(profile_document)


def get_profile_by_username(credentials, username):
    """
    Get profile data via the username of a user

    :param credentials: the credentials to lookup with
    :param username: the username to look up
    :return: a dictionary representing a profile
    """
    if not login(credentials["user"], credentials["password"]):
        raise ValueError("invalid login")

    profile_document = http.get_html(
        PROFILE_URL,
        cookies=True,
        query_params={"action": "getinfo", "username": username},
    )

    return parse_profile_html(profile_document)


def format_profile_response(profile, show_link=False):
    """
    Format a profile object into a response for sending out via IRC reply.

    :param profile: a dictionary with profile data from parse_profile_html
    :param show_link: whether or not to show the link to the profile
    :return: a human-readable string representation of the profile
    """
    if not profile:
        return "profile not found"

    if "gender" in profile and profile["gender"] in GENDER_UNICODE:
        profile["gender_symbol"] = GENDER_UNICODE[profile["gender"]]
    else:
        profile["gender_symbol"] = "?"

    if show_link:
        return (
            "\x02{username}\x02 ({gender_symbol}) - registered \x02{registered}\x02 - "
            "last post \x02{last_post}\x02 - {post_rate} posts per day - {profile_link}"
        ).format(**profile)
    else:
        return (
            "\x02{username}\x02 ({gender_symbol}) - registered \x02{registered}\x02 - "
            "last post \x02{last_post}\x02 - {post_rate} posts per day"
        ).format(**profile)


@hook.api_key("somethingawful")
@hook.command("profile")
def profile_username(inp, api_key=None):
    """.profile <username> - get the SomethingAwful profile for a user via their username"""
    if api_key is None or "user" not in api_key or "password" not in api_key:
        return

    profile = get_profile_by_username(api_key, inp)

    return format_profile_response(profile, show_link=True)


@hook.api_key("somethingawful")
@hook.regex(SA_PROFILE_RE)
def profile_link(inp, api_key=None):
    if api_key is None or "user" not in api_key or "password" not in api_key:
        return

    if not isinstance(inp, MATCH_OBJECT):
        inp = re.search(SA_PROFILE_RE, inp)

    if not inp:
        return

    profile_lookup_type = inp.group(1).lower()
    profile_lookup_value = inp.group(2)

    profile = None

    if profile_lookup_type == "userid":
        profile = get_profile_by_id(api_key, profile_lookup_value)
    elif profile_lookup_type == "username":
        profile = get_profile_by_username(api_key, profile_lookup_value)

    return format_profile_response(profile)


@hook.api_key("somethingawful")
@hook.regex(SA_THREAD_RE)
def thread_link(inp, api_key=None):
    if api_key is None or "user" not in api_key or "password" not in api_key:
        return

    if not isinstance(inp, MATCH_OBJECT):
        inp = re.search(SA_THREAD_RE, inp)

    if not inp:
        return

    post = None
    if "#post" in inp.group(0):
        parsed = http.urlparse(inp.group(0))
        thread = get_thread_by_id(
            api_key, inp.group(1), params=dict(http.parse_qsl(parsed.query))
        )
        post = thread["posts"].get(parsed.fragment)
        print(post)
    else:
        thread = get_thread_by_id(api_key, inp.group(1))

    if not thread:
        return

    if len(thread["thread_title"]) > 100:
        thread["thread_title"] = thread["thread_title"][0:97] + "\u2026"

    thread["post_count_word"] = "posts" if thread["post_count"] > 1 else "post"

    if post:
        author, date, content = post
        content = re.sub(r"\n+", " // ", content)
        if len(content) > 400:
            content = content[:400] + "..."
        return (
            "\x02{forum_title}\x02 > \x02{thread_title}\x02: "
            "\x02{poster}\x02 on {date}: {content}"
        ).format(poster=author, date=date, content=content, **thread)

    return (
        "\x02{forum_title}\x02 > \x02{thread_title}\x02 by \x02{author}\x02, "
        "\x02{post_count}\x02 {post_count_word}"
    ).format(**thread)
