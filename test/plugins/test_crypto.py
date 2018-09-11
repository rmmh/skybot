from unittest import TestCase
from mock import Mock, patch

from helpers import get_fixture_file_data
from crypto import crypto, ethereum, bitcoin


class TestCrypto(TestCase):
    @patch('util.http.get_json')
    def test_crypto_btc_to_default(self, mock_http_get):
        mock_http_get.return_value = get_fixture_file_data(self, 'crypto_btc_to_default.json')

        expected = (
            u'BTC/USD: \x0307$6084.30\x0f - '
            u'High: \x0307$6541.03\x0f - '
            u'Low: \x0307$6009.51\x0f - '
            u'Volume: \x0307$2830969036.63\x0f - '
            u'Total Supply: \x0307$17202675.00\x0f - '
            u'Market Cap: \x0307$104666235502.50\x0f'
        )

        actual = crypto('btc')

        self.assertEqual(expected, actual)

    @patch('util.http.get_json')
    def test_crypto_eth_to_default(self, mock_http_get):
        mock_http_get.return_value = get_fixture_file_data(self, 'crypto_eth_to_default.json')

        expected = (
            u'ETH/USD: \x0307$315.91\x0f - '
            u'High: \x0307$363.96\x0f - '
            u'Low: \x0307$311.86\x0f - '
            u'Volume: \x0307$1086313219.92\x0f - '
            u'Total Supply: \x0307$101251550.37\x0f - '
            u'Market Cap: \x0307$31986377278.65\x0f'
        )

        actual = crypto('eth')

        self.assertEqual(expected, actual)

    @patch('util.http.get')
    def test_crypto_btc_to_btc(self, mock_http_get):
        mock_http_get.return_value = get_fixture_file_data(self, 'crypto_btc_to_btc.json')

        expected = (
            u'BTC/BTC: \x0307\u20bf1.00\x0f - '
            u'High: \x0307\u20bf1.00\x0f - '
            u'Low: \x0307\u20bf0.91\x0f - '
            u'Volume: \x0307\u20bf462329.40\x0f - '
            u'Total Supply: \x0307\u20bf17202675.00\x0f - '
            u'Market Cap: \x0307\u20bf17202675.00\x0f'
        )

        actual = crypto('btc btc')

        self.assertEqual(expected, actual)

    @patch('util.http.get')
    def test_crypto_btc_to_cad(self, mock_http_get):
        mock_http_get.return_value = get_fixture_file_data(self, 'crypto_btc_to_cad.json')

        expected = (
            u'BTC/CAD: \x0307$8608.76\x0f - '
            u'High: \x0307$8989.06\x0f - '
            u'Low: \x0307$8491.39\x0f - '
            u'Volume: \x0307$3946417367.88\x0f - '
            u'Total Supply: \x0307$17202675.00\x0f - '
            u'Market Cap: \x0307$148093700433.00\x0f'
        )

        actual = crypto('btc cad')

        self.assertEqual(expected, actual)

    @patch('util.http.get')
    def test_crypto_btc_to_eth(self, mock_http_get):
        mock_http_get.return_value = get_fixture_file_data(self, 'crypto_btc_to_eth.json')

        expected = (
            u'BTC/ETH: \x0307\u039e18.01\x0f - '
            u'High: \x0307\u039e18.90\x0f - '
            u'Low: \x0307\u039e16.98\x0f - '
            u'Volume: \x0307\u039e8270033.68\x0f - '
            u'Total Supply: \x0307\u039e17202675.00\x0f - '
            u'Market Cap: \x0307\u039e309820176.75\x0f'
        )

        actual = crypto('btc eth')

        self.assertEqual(expected, actual)

    @patch('util.http.get')
    def test_crypto_btc_to_invalid(self, mock_http_get):
        mock_http_get.return_value = get_fixture_file_data(self, 'crypto_btc_to_invalid.json')

        expected = 'Conversion of BTC to INVALID not found'
        actual = crypto('btc invalid')

        self.assertEqual(expected, actual)

    @patch('util.http.get')
    def test_crypto_invalid_to_usd(self, mock_http_get):
        mock_http_get.return_value = get_fixture_file_data(self, 'crypto_invalid_to_usd.json')

        expected = 'Conversion of INVALID to USD not found'
        actual = crypto('invalid usd')

        self.assertEqual(expected, actual)

    @patch('util.http.get')
    def test_bitcoin(self, mock_http_get):
        mock_http_get.return_value = get_fixture_file_data(self, 'crypto_btc_to_default.json')

        expected = (
            u'BTC/USD: \x0307$6084.30\x0f - '
            u'High: \x0307$6541.03\x0f - '
            u'Low: \x0307$6009.51\x0f - '
            u'Volume: \x0307$2830969036.63\x0f - '
            u'Total Supply: \x0307$17202675.00\x0f - '
            u'Market Cap: \x0307$104666235502.50\x0f'
        )

        actual = bitcoin('')

        self.assertEqual(expected, actual)

    @patch('util.http.get')
    def test_ethereum(self, mock_http_get):
        mock_http_get.return_value = get_fixture_file_data(self, 'crypto_eth_to_default.json')

        expected = (
            u'ETH/USD: \x0307$315.91\x0f - '
            u'High: \x0307$363.96\x0f - '
            u'Low: \x0307$311.86\x0f - '
            u'Volume: \x0307$1086313219.92\x0f - '
            u'Total Supply: \x0307$101251550.37\x0f - '
            u'Market Cap: \x0307$31986377278.65\x0f'
        )

        actual = ethereum('')

        self.assertEqual(expected, actual)