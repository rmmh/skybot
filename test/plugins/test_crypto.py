from unittest import TestCase
from mock import Mock, patch

from helpers import get_fixture_file_data
from crypto import crypto


class TestCrypto(TestCase):
    @patch('util.http.get_json')
    def test_crypto_btc_to_default(self, mock_http_get):
        mock_http_get.return_value = get_fixture_file_data(self, 'crypto_btc_to_default.json')

        expected = u'USD/\u0243: \x0307$ 6,084.30\x0f - High: ' \
                   u'\x0307$ 6,178.90\x0f - Low: \x0307$ 6,014.26' \
                   u'\x0f - Volume: \u0243 21,428.7 ' \
                   u'($ 131,067,493.3) - Total Supply: ' \
                   u'\u0243 17,202,675.0 - MktCap: $ 104.67 B'

        say_mock = Mock()
        crypto('btc', say=say_mock)

        say_mock.assert_called_once_with(expected)

    @patch('util.http.get_json')
    def test_crypto_eth_to_default(self, mock_http_get):
        mock_http_get.return_value = get_fixture_file_data(self, 'crypto_eth_to_default.json')

        expected = u'USD/\u039e: \x0307$ 315.91\x0f - High: ' \
                   u'\x0307$ 332.41\x0f - Low: \x0307$ 312.35\x0f ' \
                   u'- Volume: \u039e 163,011.9 ($ 52,513,531.9) - ' \
                   u'Total Supply: \u039e 101,251,550.4 - ' \
                   u'MktCap: $ 31.99 B'

        say_mock = Mock()
        crypto('eth', say_mock)

        say_mock.assert_called_once_with(expected)
