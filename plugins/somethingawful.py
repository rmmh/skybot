from util import hook, http


thread_re = r"(?i)forums\.somethingawful\.com/\S+threadid=(\d+)"
showthread = "http://forums.somethingawful.com/showthread.php?noseen=1"


def login(user, password):
    http.jar.clear_expired_cookies()
    if any(cookie.domain == 'forums.somethingawful.com' and
           cookie.name == 'bbuserid' for cookie in http.jar):
        if any(cookie.domain == 'forums.somethingawful.com' and
               cookie.name == 'bbpassword' for cookie in http.jar):
            return
        assert("malformed cookie jar")
    user = http.quote(user)
    password = http.quote(password)
    http.get("http://forums.somethingawful.com/account.php", cookies=True,
        post_data="action=login&username=%s&password=%s" % (user, password))


@hook.regex(thread_re)
def forum_link(inp, bot=None):
    if 'sa_user' not in bot.config or \
       'sa_password' not in bot.config:
        return

    login(bot.config['sa_user'], bot.config['sa_password'])

    thread = http.get_html(showthread, threadid=inp.group(1), perpage='1',
                           cookies=True)

    breadcrumbs = thread.xpath('//div[@class="breadcrumbs"]//a/text()')

    if not breadcrumbs:
        return

    thread_title = breadcrumbs[-1]
    forum_title = forum_abbrevs.get(breadcrumbs[-2], breadcrumbs[-2])

    poster = thread.xpath('//dt[contains(@class, author)]//text()')[0]

    # 1 post per page => n_pages = n_posts
    num_posts = thread.xpath('//a[@title="last page"]/@href')

    if not num_posts:
        num_posts = 1
    else:
        num_posts = int(num_posts[0].rsplit('=', 1)[1])

    return '\x02%s\x02 > \x02%s\x02 by \x02%s\x02, %s post%s' % (
            forum_title, thread_title, poster, num_posts,
            's' if num_posts > 1 else '')


forum_abbrevs = {
    'Serious Hardware / Software Crap': 'SHSC',
    'The Cavern of COBOL': 'CoC',
    'General Bullshit': 'GBS',
    'Haus of Tech Support': 'HoTS'
}
