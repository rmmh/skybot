from unittest import TestCase

from translate import execute_operations, generate_translate_token


class TestTranslate(TestCase):
    def test_execute_operations(self):
        cases = [
            (-1835000, (4294967295, '+-3^+b+-f')),
            (60389269, (444221241, '+-a^+6')),
            (444221144, (426723, '+-a^+6'))
        ]

        for case in cases:
            self.assertEqual(case[0], execute_operations(*case[1]))

    def test_generate_token(self):
        cases = [
            ('999295.638436', ("426651.2184298043", 'Hallo!')),
            ('498909.73286', ('426651.2184298043', 'hello'))
        ]

        for case in cases:
            self.assertEqual(case[0], generate_translate_token(*case[1]))
