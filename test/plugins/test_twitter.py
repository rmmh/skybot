import unittest
from unittest import TestCase


from mock import patch

from helpers import get_fixture_file_data, execute_skybot_regex
from twitter import show_tweet, twitter


class TestTwitter(TestCase):
    @patch("util.http.get_json")
    def test_tweet_regex(self, mock_http_get):
        mock_http_get.return_value = get_fixture_file_data(
            self, "1014260007771295745.json"
        )

        expected = (
            u"2018-07-03 21:30:04 \x02jk_rowling\x02: "
            u"hahahahahahahahahahahahahahahahahahahahaha"
            u"hahahahahahahahahahahahahahahahahahahahaha"
            u"hahahahahahahahahahahahahahahahahahahahaha"
            u"hahahaha "
            u"*draws breath* "
            u"hahahahahahahahahahahahahahahahahahahahaha"
            u"hahahahahahahahahahahahahahahahahahahahaha"
            u"hahahahahahahahahahahahahahahahahahahahaha"
            u"haha "
            u"https://x.com/realDonaldTrump/status/1014257237945176071"
        )

        url = "https://twitter.com/jk_rowling/status/1014260007771295745"
        actual = execute_skybot_regex(show_tweet, url)

        assert expected == actual

    @unittest.skip("tweet lookup by username is not supported")
    @patch("util.http.get_json")
    def test_twitter_username_no_tweet_number(self, mock_http_get):
        mock_http_get.return_value = get_fixture_file_data(
            self, "user_loneblockbuster.json"
        )

        expected = (
            u"2018-08-16 17:38:52 \x02loneblockbuster\x02: "
            u"We had the motto \"When you're here you're "
            u'family" before Olive Garden but like '
            u"everything else it was taken away "
            u"from us."
        )

        actual = twitter("loneblockbuster")

        assert expected == actual

    @unittest.skip("tweet lookup by username is not supported")
    @patch("util.http.get_json")
    def test_twitter_username_with_tweet_number(self, mock_http_get):
        mock_http_get.return_value = get_fixture_file_data(
            self, "user_loneblockbuster.json"
        )

        expected = (
            u"2018-07-24 19:30:59 \x02loneblockbuster\x02: "
            u"We never would have planted the ferns out "
            u"front if we knew we'd get so many death threats."
        )

        actual = twitter("loneblockbuster 10")

        assert expected == actual

    @unittest.skip("tweet lookup by hashtag is not supported")
    @patch("random.randint")
    @patch("util.http.get_json")
    def test_twitter_hashtag_no_tweet_number(self, mock_http_get, mock_random_randint):
        mock_http_get.return_value = get_fixture_file_data(self, "hashtag_nyc.json")

        # This plugin chooses a random value.
        # I chose this value randomly by rolling a D20.
        mock_random_randint.return_value = 6

        expected = (
            u"2018-08-17 20:19:56 \x02The_Carl_John\x02: "
            u"RT @ItVisn How many records can your "
            u"company afford to lose? https://t.co/iJzFYtJmCh "
            u"Be proactive and Protect Your Business "
            u"#CyberSecurity #DataProtection "
            u"#DataBreaches #SmallBusiness #Tech "
            u"#Data #NYC #Technology #DarkWeb #Ransomware "
            u"#Malware #Phishing #Business "
            u"https://t.co/xAJVRhjOww"
        )

        actual = twitter("#NYC")

        assert expected == actual

    @unittest.skip("tweet lookup by hashtag is not supported")
    @patch("util.http.get_json")
    def test_twitter_hashtag_with_tweet_number(self, mock_http_get):
        mock_http_get.return_value = get_fixture_file_data(self, "hashtag_nyc.json")

        expected = (
            u"2018-08-17 20:19:32 \x02Kugey\x02: "
            u"I know for sure that life is beautiful "
            u"around the world... \u2022 \u2022 Here "
            u"is yet another iconic piece of the "
            u"NYC skyline... \u2022 \u2022 #nyc "
            u"#photography #streetphotography "
            u"#urbanphotography\u2026 "
            u"https://t.co/bq9i0FZN89"
        )

        actual = twitter("#NYC 10")

        assert expected == actual
