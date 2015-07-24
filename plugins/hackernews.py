import unittest

from util import http, hook


@hook.regex(r'(?i)https://(?:www\.)?news\.ycombinator\.com\S*id=(\d+)')
def hackernews(match):
    base_api = 'https://hacker-news.firebaseio.com/v0/item/'
    entry = http.get_json(base_api + match.group(1) + ".json")

    if entry['type'] == "story":
    	entry['title'] = http.unescape(entry['title'])
        return u"{title} by {by} with {score} points and {descendants} comments ({url})".format(**entry)

    if entry['type'] == "comment":
	entry['text'] = http.unescape(entry['text'].replace('<p>', ' // '))
        return u'"{text}" -- {by}'.format(**entry)

class Test(unittest.TestCase):
    def news(self, inp):
        re = hackernews._hook[0][1][1]['re']
	return hackernews(re.search(inp))

    def test_story(self):
    	assert 'Desalination' in self.news('https://news.ycombinator.com/item?id=9943431')

    def test_comment(self):
    	res = self.news('https://news.ycombinator.com/item?id=9943987')
	assert 'kilowatt hours' in res
	assert 'oaktowner' in res

    def test_comment_encoding(self):
    	res = self.news('https://news.ycombinator.com/item?id=9943897')
	assert 'abominations' in res
	assert '> ' in res  # encoding
