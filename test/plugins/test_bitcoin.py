from unittest import TestCase
from mock import patch, Mock

from helpers import get_fixture_file_data
from bitcoin import bitcoin, ethereum


class TestBitcoin(TestCase):
    @patch('util.http.get_json')
    def test_bitcoin(self, mock_http_get):
        mock_http_get.return_value = get_fixture_file_data(self, 'bitcoin.json')

        say_mock = Mock()

        bitcoin('', say=say_mock)

        expected = 'USD/BTC: \x0307$6,390.67\x0f - High: \x0307$6,627.' \
                   '00\x0f - Low: \x0307$6,295.73\x0f - Volume: ' \
                   '10,329.67 BTC'
        say_mock.assert_called_once_with(expected)

    @patch('util.http.get_json')
    def test_ethereum(self, mock_http_get):
        mock_http_get.return_value = get_fixture_file_data(self, 'ethereum.json')

        say_mock = Mock()

        ethereum('', say=say_mock)

        expected = 'USD/ETH: \x0307$355.02\x0f - High: \x0307$370.43' \
                   '\x0f - Low: \x0307$350.00\x0f - Volume: ' \
                   '16,408.97 ETH'

        say_mock.assert_called_once_with(expected)