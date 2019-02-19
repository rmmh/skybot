from ctypes import c_int
from decimal import Decimal
from random import shuffle
import re
from urllib import urlencode

from util import hook, http


TRANSLATE_URL = 'https://translate.google.com/translate_a/single'

LANGUAGE_ALIASES = {
    'zh': 'zh-cn',
    'jp': 'ja',
    'jpn': 'ja',
}

LANGUAGES = {
    'auto': 'Automatic',
    'af': 'Afrikaans',
    'sq': 'Albanian',
    'am': 'Amharic',
    'ar': 'Arabic',
    'hy': 'Armenian',
    'az': 'Azerbaijani',
    'eu': 'Basque',
    'be': 'Belarusian',
    'bn': 'Bengali',
    'bs': 'Bosnian',
    'bg': 'Bulgarian',
    'ca': 'Catalan',
    'ceb': 'Cebuano',
    'ny': 'Chichewa',
    'zh-cn': 'Chinese Simplified',
    'zh-tw': 'Chinese Traditional',
    'co': 'Corsican',
    'hr': 'Croatian',
    'cs': 'Czech',
    'da': 'Danish',
    'nl': 'Dutch',
    'en': 'English',
    'eo': 'Esperanto',
    'et': 'Estonian',
    'tl': 'Filipino',
    'fi': 'Finnish',
    'fr': 'French',
    'fy': 'Frisian',
    'gl': 'Galician',
    'ka': 'Georgian',
    'de': 'German',
    'el': 'Greek',
    'gu': 'Gujarati',
    'ht': 'Haitian Creole',
    'ha': 'Hausa',
    'haw': 'Hawaiian',
    'iw': 'Hebrew',
    'hi': 'Hindi',
    'hmn': 'Hmong',
    'hu': 'Hungarian',
    'is': 'Icelandic',
    'ig': 'Igbo',
    'id': 'Indonesian',
    'ga': 'Irish',
    'it': 'Italian',
    'ja': 'Japanese',
    'jw': 'Javanese',
    'kn': 'Kannada',
    'kk': 'Kazakh',
    'km': 'Khmer',
    'ko': 'Korean',
    'ku': 'Kurdish (Kurmanji)',
    'ky': 'Kyrgyz',
    'lo': 'Lao',
    'la': 'Latin',
    'lv': 'Latvian',
    'lt': 'Lithuanian',
    'lb': 'Luxembourgish',
    'mk': 'Macedonian',
    'mg': 'Malagasy',
    'ms': 'Malay',
    'ml': 'Malayalam',
    'mt': 'Maltese',
    'mi': 'Maori',
    'mr': 'Marathi',
    'mn': 'Mongolian',
    'my': 'Myanmar (Burmese)',
    'ne': 'Nepali',
    'no': 'Norwegian',
    'ps': 'Pashto',
    'fa': 'Persian',
    'pl': 'Polish',
    'pt': 'Portuguese',
    'ma': 'Punjabi',
    'ro': 'Romanian',
    'ru': 'Russian',
    'sm': 'Samoan',
    'gd': 'Scots Gaelic',
    'sr': 'Serbian',
    'st': 'Sesotho',
    'sn': 'Shona',
    'sd': 'Sindhi',
    'si': 'Sinhala',
    'sk': 'Slovak',
    'sl': 'Slovenian',
    'so': 'Somali',
    'es': 'Spanish',
    'su': 'Sundanese',
    'sw': 'Swahili',
    'sv': 'Swedish',
    'tg': 'Tajik',
    'ta': 'Tamil',
    'te': 'Telugu',
    'th': 'Thai',
    'tr': 'Turkish',
    'uk': 'Ukrainian',
    'ur': 'Urdu',
    'uz': 'Uzbek',
    'vi': 'Vietnamese',
    'cy': 'Welsh',
    'xh': 'Xhosa',
    'yi': 'Yiddish',
    'yo': 'Yoruba',
    'zu': 'Zulu'
}


def get_translate_token_initialization_vector():
    """
    Get the initialization vector string for use in the request signing phase
    of the google translate API.

    May be cached for ~4 hours

    :return: A string which represents the token initialization vector.
    """
    translate_index_page = http.get(
        'https://translate.google.com',
        headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'
        }
    )

    tkk_function_match = re.search('TKK=eval\(\'(?P<function>.*?)\(\)\)\'\);', translate_index_page)
    # ((function(){var a\x3d0000000000;var b\x3d000000000;return 000000+\x27.\x27+(a+b)})

    if not tkk_function_match:
        return None

    tkk_values_match = re.search(
        'a\\\\x3d(?P<a>-?[0-9]+);var b\\\\x3d(?P<b>-?[0-9]+);return (?P<c>[0-9]+)',
        tkk_function_match.group('function')
    )

    if not tkk_values_match:
        return None

    tkk_a = Decimal(tkk_values_match.group('a'))
    tkk_b = Decimal(tkk_values_match.group('b'))
    tkk_c = Decimal(tkk_values_match.group('c'))

    tkk = (tkk_a + tkk_b).scaleb(-10)

    tkk += tkk_c

    return tkk


def simulate_overflow(int_value):
    """
    Simulate a 32bit integer with overflow, as if it were a Javascript integer.

    This essentially means that simulate_overflow(MAX_INT + 1) == -MAX_INT,
    where MAX_INT is 0xFFFFFFFF

    :param int_value: The input int value we want to simulate an overflow on
    :return: The simulated overflow integer.
    """
    overflow_value = 0xFFFFFFFF

    if not -overflow_value - 1 <= int_value <= overflow_value:
        int_value = (int_value + (overflow_value + 1)) % (2 * (overflow_value + 1)) - overflow_value - 1

    return c_int(int_value).value


def execute_operations(input_value, operations):
    """
    Execute operations just like the Google translate javascript `xr` function.

    Operations are character strings in chunks of 3 with the following format.

    * First character: An operation to apply, either "+" to add or "^" to XOR
    * Second character: the shift_direction to apply to derive our operand (either '+' (right) or '-' (left))
    * Third character: The amount to shift

    These are applied to the input value in order until we have applied all of them.

    :param input_value: The input number to operate on
    :param operations: The 3 character chunks of operations to apply
    :return: The output number after the operations have been applied
    """
    # This code was created based on:
    #   https://translate.google.com/translate/releases/twsfe_w_20160620_RC00/r/js/desktop_module_main.js

    for c in range(0, len(operations), 3):
        op, shift_direction, op_hex_value = list(operations[c:c+3])

        op_value = int(op_hex_value, 16)

        if '+' == shift_direction:
            op_value = input_value >> op_value if input_value >= 0 else (input_value + 0x100000000) >> op_value
            # Simulate the bitwise right-fill shift operator in python
        else:
            op_value = input_value << op_value

        op_value = simulate_overflow(op_value)

        if '+' == op:
            input_value += op_value
        else:
            input_value ^= op_value

        input_value = simulate_overflow(input_value)
    return input_value


def generate_translate_token(token_initialization, text):
    """
    Generates a signature of the input `text` using the
    `token_initialization` value.  This can be used to make
    requests against the `translate.google.com` services

    :param token_initialization: The `TKK` value retrieved from `translate.google.com`
    :param text: The text to create a signature of
    :return: The signature for making translate requests
    """
    # This is where it gets a little weird.
    # This code was created based on:
    #   https://translate.google.com/translate/releases/twsfe_w_20160620_RC00/r/js/desktop_module_main.js
    #

    # In the original code, it essentially set a variable to `&tk=`
    # and retrieves the initialization token as the first step -
    # just with a ton of obfuscation,
    #
    # Thing is, we don't care about it, so we skip ALL of that.

    token_initialization = str(token_initialization)

    token_initialization_parts = [simulate_overflow(int(i)) for i in token_initialization.split('.')]

    characters = []

    # Essentially, split up the text and prep it for running
    # against our signature algorithm.
    skip_iteration = False
    for g in range(0, len(text)):
        if skip_iteration:
            skip_iteration = False
            continue

        ordinal = ord(text[g])

        # The original code tried to do the following in a gigantic ternary.
        # It was a lot of unpack, mentally, so I first rewrote it in JS without
        # the ternary, then converted it to Python.
        #
        # if (128 > l) {
        #   e[f++] = l;
        # } else {
        #   if (2048 > l) {
        #     e[f++] = l >> 6 | 192;
        #   } else {
        #     if (55296 == (l & 64512) && g + 1 < a.length && 56320 == (a.charCodeAt(g + 1) & 64512)) {
        #       l = 65536 + ((l & 1023) << 10) + (a.charCodeAt(++g) & 1023);
        #       e[f++] = l >> 18 | 240;
        #       e[f++] = l >> 12 & 63 | 128;
        #     } else {
        #       e[f++] = l >> 12 | 224;
        #       e[f++] = l >> 6 & 63 | 128;
        #     }
        # 	}
        # 	e[f++] = l & 63 | 128;
        # }

        if 128 > ordinal:
            characters.append(ordinal)
        else:
            if 2048 > ordinal:
                characters.append(ordinal >> 6 | 192)
            else:
                next_ordinal = text[g + 1]
                if 55296 == ordinal & 64512 and g + 1 < len(text) and 56320 == next_ordinal & 64512:
                    # In the original code, the next iteration was skipped by using "++g"
                    # but we can't do that in Python.  Instead, we're opting to skip the next
                    # iteration explicitly when pulling the next character here.
                    skip_iteration = True

                    ordinal = 65536 + ((ordinal & 1023) << 10) + (next_ordinal & 1023)

                    characters.append(ordinal >> 18 | 240)
                    characters.append(ordinal >> 12 & 63 | 128)
                else:
                    characters.append(ordinal >> 12 | 224)
                    characters.append(ordinal >> 6 & 63 | 128)
            characters.append(ordinal & 63 | 128)

    result = token_initialization_parts[0]

    for ordinal in characters:
        result += ordinal
        result = execute_operations(result, '+-a^+6')

    result = execute_operations(result, "+-3^+b+-f")

    result ^= token_initialization_parts[1]

    if 0 > result:
        result = (result & 2147483647) + 2147483648

    result %= 1000000

    return str(result) + "." + str(result ^ token_initialization_parts[0])


def make_google_translate_request(tk, text, from_language, to_language):
    """
    Make a request against google translate with the `tk` signature so we
    can translate `text` from `from_language` into `to_language`.

    :param tk: The derived signature of `text`
    :param text: Text we want to translate
    :param from_language: Language we want to translate from
    :param to_language: Language we want to translate to
    :return: A dict with a `translation` object of translated text, and the `from_language` it was translated from
    """
    # Expects multiple `dt` so we can't use standard query params generation.

    # dt is the response format.  The order you enter them make the order of the
    # array of the output document.
    #
    # valid options include:
    #
    # * at
    # * bd
    # * ex
    # * ld
    # * md
    # * qca
    # * rw
    # * rm
    # * ss
    # * t
    #
    # For this I've chosen only to bring in `t` which I think is the translation?

    query_params = [
        ('client', 't'),
        ('sl', from_language),
        ('tl', to_language),
        ('hl', from_language),
        ('dt', 't'),
        ('ie', 'UTF-8'),
        ('oe', 'UTF-8'),
        ('otf', 2),
        ('ssel', 3),
        ('tsel', 3),
        ('kc', 1),
        ('tk', tk),
        ('q', text.encode('utf-8'))
    ]

    try:
        response = http.get_json(
            u'%s?%s' % (TRANSLATE_URL, urlencode(query_params)),
            headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'
            }
        )
    except http.HTTPError:
        return None

    return {
        'translation': response[0][0][0],
        'from_language': response[2]
    }


def google_translate(text, from_language=None, to_language='en'):
    token_initialization = get_translate_token_initialization_vector()

    if not token_initialization:
        raise ValueError('error with translate API')

    tk = generate_translate_token(token_initialization, text)

    if not from_language:
        from_language = 'auto'

    response = make_google_translate_request(tk, text, from_language, to_language)

    return response


def match_language(fragment):
    fragment = fragment.lower()

    # If there is an exact language string that
    # we've picked, use that first and foremost.
    if fragment in LANGUAGES:
        return fragment

    # A few of the languages have common aliases
    # which we've included in the LANGUAGE_ALIASES
    # dictionary.  Check that next.
    if fragment in LANGUAGE_ALIASES:
        return LANGUAGE_ALIASES[fragment]

    # Do a slow search through the language pairs
    # This won't get you past an interview but it works.
    for short, full in LANGUAGES.items():
        if fragment in full.lower():
            return short

    return None


@hook.command
def translate(inp):
    """.translate [target language [source language]] <sentence> -- translates
        <sentence> from source language (default autodetect) to target
        language (default English) using Google Translate"""

    args = inp.split(' ', 2)

    # Parsing the input string is a little weird.
    # We have two potential prefix values for the translation -
    # to and from.  We ONLY allow "from" if "to" is considered a
    # matched language.
    #
    # If we made this its own function it'd be clearer for the
    # exact mechanisms taking place, but for now let's just
    # make it grossly a nested IF

    to_language = 'en'
    from_language = None

    if len(args) >= 2:
        guessed_to_language = match_language(args[0])

        if guessed_to_language:
            to_language = guessed_to_language
            args.pop(0)

            if len(args) >= 2:
                guessed_from_language = match_language(args[0])

                if guessed_from_language:
                    from_language = guessed_from_language
                    args.remove(0)

    text = ' '.join(args)

    response = google_translate(text, from_language, to_language)

    if not from_language and response['from_language'] != 'en':
        if response['from_language'] in LANGUAGES:
            response['from_language'] = LANGUAGES[response['from_language']]

        return u'Detected Language: {from_language} - {translation}'.format(**response)

    return u'{translation}'.format(**response)


def babel_generator(inp):
    languages = shuffle('ja fr de ko ru zh'.split())

    languages.append('en')

    translation = inp
    from_language = None
    for to_language in languages:
        response = google_translate(translation, from_language, to_language)
        translation = response['translation']
        from_language = to_language
        yield from_language, translation


@hook.command
def babel(inp):
    """.babel <sentence> -- translates <sentence> through multiple languages"""

    try:
        return list(babel_generator(inp))[-1][1]
    except IOError as e:
        return e


@hook.command
def babelext(inp):
    """.babelext <sentence> -- like .babel, but with more detailed output"""

    try:
        babels = list(babel_generator(inp))
    except IOError as e:
        return e

    out = u''
    for lang, text in babels:
        out += '%s:"%s", ' % (lang, text)

    if len(out) > 300:
        out = out[:150] + ' ... ' + out[-150:]

    return out
