from unittest import TestCase
from mock import patch

from helpers import get_fixture_file

from skybot.plugins.cdecl import cdecl


class TestCDecl(TestCase):
    @patch('skybot.util.http.get')
    def test_cdecl(self, mock_http_get):
        mock_http_get.return_value = get_fixture_file(self, 'example.json')

        expected = '"declare x as array 3 of pointer to function returning pointer to array 5 of char"'
        actual = cdecl('char (*(*x())[5])()')

        assert expected == actual