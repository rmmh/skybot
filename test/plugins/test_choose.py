from unittest import TestCase
from mock import patch

from choose import choose


class TestChoose(TestCase):
    def test_choose_one_choice(self):
        expected = 'the decision is up to you'
        actual = choose('foo')

        assert expected == actual

    def test_choose_same_thing(self):
        expected = 'foo'
        actual = choose('foo, foo, foo')

        assert expected == actual

    def test_choose_two_choices(self):
        actual = choose('foo, bar')

        assert actual in ['foo', 'bar']

    def test_choose_choices_space(self):
        expected_values = ['foo', 'bar']
        actual = choose('foo bar')

        assert actual in expected_values

    def test_choose_strips_whitespace(self):
        expected_values = ['foo', 'bar']
        actual = choose('          foo             ,'
                        '           bar             ')

        assert actual in expected_values

    @patch('random.choice')
    def test_choose_end_comma_behavior(self, mock_random_choice):
        mock_random_choice.side_effect = lambda arr: arr[0]

        expected = 'the decision is up to you'
        actual = choose('foo,')

        assert actual == expected

    @patch('random.choice')
    def test_choose_collapse_commas(self, mock_random_choice):
        # Should never be an empty string here
        mock_random_choice.side_effect = lambda arr: arr[1]

        expected = 'bar'
        actual = choose('foo,,bar')

        assert actual == expected
