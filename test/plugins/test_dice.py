from unittest import skip, TestCase
from mock import patch

from dice import dice


class TestDice(TestCase):
    @patch('random.randint')
    def test_one_d20(self, mock_random_randint):
        mock_random_randint.return_value = 5

        expected = '5 (d20=5)'
        actual = dice('d20')

        assert expected == actual

    @skip('skip until https://github.com/rmmh/skybot/pull/187 is merged')
    @patch('random.randint')
    def test_complex_roll(self, mock_random_randint):
        mock_random_randint.side_effect = iter([1, 2, 3])

        expected = u'4 (2d20-d5+4=1, 2, -3)'
        actual = dice('2d20-d5+4')

        assert expected == actual

    def test_constant_roll(self):
        # This fails so it is "none"
        actual = dice('1234')

        assert actual is None

    @patch('random.randint')
    def test_fudge_dice(self, mock_random_randint):
        mock_random_randint.side_effect = iter([-1, 0, 1, 0, -1])

        expected = '-1 (5dF=\x034-\x0f, 0, \x033+\x0f, 0, \x034-\x0f)'
        actual = dice('5dF')

        assert expected == actual

    @patch('random.randint')
    def test_fudge_dice(self, mock_random_randint):
        mock_random_randint.side_effect = iter([-1, 0, 1, 0, -1])

        expected = '-1 (5dF=\x034-\x0f, 0, \x033+\x0f, 0, \x034-\x0f)'
        actual = dice('5dF')

        assert expected == actual