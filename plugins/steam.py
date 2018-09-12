import re
from cookielib import Cookie
from util import hook, http


@hook.regex(r'steamcommunity.com/(profiles)/([0-9]+)')
@hook.regex(r'steamcommunity.com/(id)/([A-Za-z0-9]+)')
def link_steam_user(match):
    if match.group(1) == 'profiles':
        url = 'http://steamcommunity.com/profiles/%d' % match.group(2)
    elif match.group(1) == 'id':
        url = 'http://steamcommunity.com/id/%s' % match.group(2)
    else:
        return None

    try:
        doc = http.get_html(url)
    except http.HTTPError:
        return None

    persona_name_elements = doc.find_class('actual_persona_name')
    persona_level_elements = doc.find_class('persona_level')

    if len(persona_name_elements) > 0:
        name = persona_name_elements[0].text_content().strip()
    else:
        name = 'Unknown'

    if len(persona_level_elements) > 0:
        level = persona_level_elements[0].text_content().strip()
    else:
        level = 'Unknown Level'

    game_status_elements = doc.find_class('profile_in_game_header')
    game_name_elements = doc.find_class('profile_in_game_name')

    if len(game_status_elements) > 0:
        game_status = game_status_elements[0].text_content().strip()

        if len(game_name_elements) > 0:
            game_name = game_name_elements[0].text_content().strip()

            if game_status == 'Currently Offline':
                game_status = game_name

            if game_status == 'Currently In-Game':
                game_status = 'Playing %s' % game_name

    message = "\x02%s\x02 - %s - %s" % (name, game_status, level)

    bans = doc.find_class('profile_ban')

    if (len(bans) > 0):
        bans = bans[0].text_content().split('|')[0].strip()

        message += " - \x0304%s" % bans

    return message


@hook.regex(r'store.steampowered.com/app/([0-9]+)')
def link_steam_app(match):
    # Cookie(
    #    version, name, value, port, port_specified, domain, domain_specified,
    #    domain_initial_dot, path, path_specified, secure, expiry, comment, comment_url, rest)
    age_gate_cookie = Cookie(
        None, 'birthtime', '473403601', '80', '80', 'store.steampowered.com', 'store.steampowered.com',
        None, '/', '/', False, '2147483600', None, None, None, None
    )

    mature_content_cookie = Cookie(
        None, 'mature_content', '1', '80', '80', 'store.steampowered.com', 'store.steampowered.com',
        None, '/', '/', False, '2147483600', None, None, None, None
    )

    http.jar.set_cookie(age_gate_cookie)
    http.jar.set_cookie(mature_content_cookie)

    try:
        doc = http.get_html(
            'http://store.steampowered.com/app/%d' % int(match.group(1)),
            cookies=True
        )
    except http.HTTPError:
        return None

    try:
        title = doc.find_class('apphub_AppName')[0].text_content().strip()
    except:
        return 'Nothing found'

    try:
        rating = doc.find_class('game_review_summary')[0].text_content().strip()
    except:
        rating = 'Unknown'

    price = 'Unknown'

    game_purchase_elements = doc.find_class('game_area_purchase_game_wrapper')

    if len(game_purchase_elements) > 0:
        discount_price_elements = game_purchase_elements[0].find_class('discount_final_price')
        game_purchase_price = game_purchase_elements[0].find_class('game_purchase_price')

        if len(discount_price_elements) > 0:
            original_price_elements = game_purchase_elements[0].find_class('discount_original_price')
            discount_percent_elements = game_purchase_elements[0].find_class('discount_pct')

            discount_price = discount_price_elements[0].text_content().strip()

            if len(original_price_elements) > 0:
                full_price = original_price_elements[0].text_content().strip()
            else:
                full_price = 'something'

            if len(discount_percent_elements) > 0:
                discount_percent = discount_percent_elements[0].text_content().strip()
            else:
                discount_percent = 'A'

            price = '\x0307%s\x0f (%s discount off %s)' % (discount_price, discount_percent, full_price)
        elif len(game_purchase_price) > 0:
            price = game_purchase_price[0].text_content().strip()

    # Limit to only 5 tags
    tags_elements = doc.find_class('app_tag')[0:5]

    tags = [tag.text_content().strip() for tag in tags_elements if not 'add_button' in tag.get('class')]

    if len(tags) > 0:
        tags = ' - %s' % (', '.join(tags))
    else:
        tags = ''

    return '\x02%s\x02 - %s - User rating is %s%s' % (title, price, rating, tags)


@hook.command
def steam(inp):
    try:
        doc = http.get_html(
            'http://store.steampowered.com/search',
            cookies=True,
            term=inp
        )
    except http.HTTPError as e:
        return None

    search_result_elements = doc.find_class('search_result_row')

    if len(search_result_elements) == 0:
        return 'app not found'

    app_url = search_result_elements[0].attrib['href'].strip()

    match = re.search(r'store.steampowered.com/app/([0-9]+)', app_url)

    if not match:
        return None

    return '%s - https://store.steampowered.com/app/%d' % (link_steam_app(match), int(match.group(1)))
