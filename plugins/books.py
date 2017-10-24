import urllib

from util import hook, http


def fetch_book(title):
    url = 'http://libgen.io/search.php?req={0}&'.format(urllib.quote_plus(title))
    params = {
        'lg_topic': 'libgen',
        'open': 0,
        'view': 'simple',
        'res': 25,
        'phrase': 1,
        'column': 'def'
    }

    results = http.get_html(url, **params)
    selector = '//table[3]/tr[2]/td[3]/a[2]/text() | //table[3]/tr[2]/td[3]/a[2]/@href'
    info = results.xpath(selector)

    title = info[1].strip()
    download_url = 'http://libgen.io/ads.php?md5=' + info[0].split('?')[1].strip('md5=')

    return {'title': title, 'url': download_url}


@hook.command('book')
def libgen(inp):
    results = fetch_book(inp)

    return "{title} -- {url}".format(**results)


if __name__ == '__main__':
    print libgen('harry potter')
