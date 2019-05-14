from unittest import TestCase
from mock import patch

from cdecl import cdecl


class TestCDecl(TestCase):
    @patch('util.http.get')
    def test_cdecl(self, mock_http_get):
        mock_http_get.side_effect = [
            "var QUERY_ENDPOINT = \"http://foo.bar\"",
            "\"declare x as array 3 of pointer to function returning pointer to array 5 of char\""
        ]

        expected = '"declare x as array 3 of pointer to function returning pointer to array 5 of char"'
        actual = cdecl('char (*(*x())[5])()')

        assert expected == actual
