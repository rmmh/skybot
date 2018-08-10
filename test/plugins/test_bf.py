from unittest import TestCase
from bf import bf


class TestBF(TestCase):
    def test_hello(self):
        expected = 'Hello world!'
        actual = bf(
            '--[>--->->->++>-<<<<<-------]>--.>---------.>--..+++.>---'
            '-.>+++++++++.<<.+++.------.<-.>>+.'
        )

        assert expected == actual

    def test_unbalanced(self):
        expected = 'unbalanced brackets'

        actual_a = bf('[[++]]]')
        actual_b = bf('[[[++]]')

        assert expected == actual_a
        assert expected == actual_b

    def test_comment(self):
        expected = '*'
        actual = bf('[this is a comment!]++++++[>+++++++<-]>.')

        assert expected == actual

    def test_unprintable(self):
        expected = 'no printable output'
        actual = bf('+.')

        assert expected == actual

    def test_empty(self):
        expected = 'no output'
        actual = bf('+++[-]')

        assert expected == actual

    def test_exceeded(self):
        expected = 'no output [exceeded 1000 iterations]'
        actual = bf('+[>,[-]<]', 1000)

        assert expected == actual

    def test_inf_mem(self):
        expected = 'no output [exceeded 1000 iterations]'
        actual = bf('+[>[.-]+]', 1000, buffer_size=10)

        assert expected == actual

    def test_left_wrap(self):
        # eventually, wrap around and hit ourselves
        expected = 'aaaaaaa [exceeded 2000 iterations]'
        actual = bf('+[<[-' + '+' * ord('a') + '.[-]]+]', 2000, buffer_size=5)

        assert expected == actual

    def test_too_much_output(self):
        expected = 'a' * 430
        actual = bf('+' * ord('a') + '[.]')

        assert expected == actual
