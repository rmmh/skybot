from unittest import TestCase

from mock import patch

from helpers import get_fixture_file_data, execute_skybot_regex
from hackernews import hackernews


class TestHackernews(TestCase):
    @patch('util.http.get_json')
    def test_story(self, mock_http_get):
        mock_http_get.return_value = get_fixture_file_data(self, '9943431.json')

        expected = u'Can Desalination Counter the Drought? by cwal37 ' \
                   u'with 51 points and 94 comments ' \
                   u'(http://www.newyorker.com/tech/elements/can-' \
                   u'desalination-counter-the-drought)'

        url = 'https://news.ycombinator.com/item?id=9943431'
        actual = execute_skybot_regex(hackernews, url)

        assert expected == actual

    @patch('util.http.get_json')
    def test_comment(self, mock_http_get):
        mock_http_get.return_value = get_fixture_file_data(self, '9943987.json')

        expected = u'"Yes, they must have meant kilowatt hours. Was ' \
                   u'there no editor?" -- oaktowner'

        url = 'https://news.ycombinator.com/item?id=9943987'
        actual = execute_skybot_regex(hackernews, url)

        assert expected == actual

    @patch('util.http.get_json')
    def test_comment_encoding(self, mock_http_get):
        mock_http_get.return_value = get_fixture_file_data(self, '9943897.json')

        expected = u'"> All told, it takes about 3460 kilowatts per ' \
                   u'acre-foot to pump water from Northern California ' \
                   u'to San Diego; Carlsbad will use about thirty per ' \
                   u'cent more energy, five thousand kilowatts per ' \
                   u'acre-foot, to desalinate ocean water and deliver ' \
                   u'it to households, according to Poseidon\u2019s ' \
                   u'report to the Department of Water Resources // ' \
                   u'These units are abominations.  Couldn\'t just ' \
                   u'say 2.8 Watts per liter vs 4.0 Watts per liter?  ' \
                   u'Or even 10.6 and 15.3 Watts per gallon?  I\'m ' \
                   u'not a metric purist, but the only advantage to ' \
                   u'using imperial units is that they are more ' \
                   u'familiar to the average American, but when does ' \
                   u'the average person deal with acre-feet?" ' \
                   u'-- alwaysdoit'

        url = 'https://news.ycombinator.com/item?id=9943897'
        actual = execute_skybot_regex(hackernews, url)

        assert expected == actual
