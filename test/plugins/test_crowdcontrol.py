from collections import namedtuple
from unittest import TestCase
from mock import Mock, patch, call

from helpers import execute_skybot_regex
from crowdcontrol import crowdcontrol

class TestCrowdcontrol(TestCase):
    def call_crowd_control(self, input, called=None, rules=None):
        mock_names = ['kick', 'ban', 'unban', 'reply']

        mocks = {}

        for name in mock_names:
            mocks[name] = Mock(name=name)

        config = { 'crowdcontrol': rules } if rules else {}
        bot = namedtuple('Bot', 'config')(config=config)

        execute_skybot_regex(crowdcontrol, input, bot=bot, **mocks)

        return mocks

    def test_no_rules(self):
        mocks = self.call_crowd_control('Hello world!')

        for m in mocks.values():
            m.assert_not_called()

    def test_no_matches(self):
        mocks = self.call_crowd_control(
            'Hello world!',
            rules=[{'re': 'No match'}]
        )

        for m in mocks.values():
            m.assert_not_called()

    def test_match_no_action(self):
        mocks = self.call_crowd_control(
            'Hello world!',
            rules=[{'re': 'Hello'}]
        )

        for m in mocks.values():
            m.assert_not_called()

    def test_match_only_msg(self):
        mocks = self.call_crowd_control(
            'Hello world!',
            rules=[{'re': 'Hello', 'msg': 'Hello!'}]
        )

        for n, m in mocks.items():
            if n == 'reply':
                m.assert_called_once_with('Hello!')
            else:
                m.assert_not_called()

    def test_match_ban_forever_no_kick(self):
        mocks = self.call_crowd_control(
            'Hello world!',
            rules=[{'re': 'Hello', 'ban_length': -1}]
        )

        for n, m in mocks.items():
            if n == 'ban':
                m.assert_called_once()
            else:
                m.assert_not_called()

    def test_match_kick_no_ban(self):
        mocks = self.call_crowd_control(
            'Hello world!',
            rules=[{'re': 'Hello', 'kick': 1}]
        )

        for n, m in mocks.items():
            if n == 'kick':
                m.assert_called_once()
            else:
                m.assert_not_called()

    def test_match_kick_with_msg(self):
        mocks = self.call_crowd_control(
            'Hello world!',
            rules=[{'re': 'Hello', 'kick': 1, 'msg': 'Hello!'}]
        )

        for n, m in mocks.items():
            if n == 'kick':
                m.assert_called_once_with(reason='Hello!')
            else:
                m.assert_not_called()

    def test_match_kick_ban_forever(self):
        mocks = self.call_crowd_control(
            'Hello world!',
            rules=[{'re': 'Hello', 'kick': 1, 'ban_length': -1}]
        )

        for n, m in mocks.items():
            if n == 'kick' or n == 'ban':
                m.assert_called_once()
            else:
                m.assert_not_called()

    @patch('time.sleep')
    def test_match_ban_only_time_limit(self, mock_time_sleep):

        mocks = self.call_crowd_control('Hello world!', rules=[{'re': 'Hello', 'ban_length': 5}])

        mock_time_sleep.assert_called_once_with(5)

        for n, m in mocks.items():
            if n == 'ban' or n == 'unban':
                m.assert_called_once()
            else:
                m.assert_not_called()

    @patch('time.sleep')
    def test_match_kick_ban_time_limit(self, mock_time_sleep):

        mocks = self.call_crowd_control('Hello world!', rules=[{'re': 'Hello', 'kick': 1, 'ban_length': 5}])

        mock_time_sleep.assert_called_once_with(5)

        for n, m in mocks.items():
            if n == 'kick' or n == 'ban' or n == 'unban':
                m.assert_called_once()
            else:
                m.assert_not_called()

    def test_match_multiple_rules_in_order(self):
        mocks = self.call_crowd_control(
            'Hello world!',
            rules=[
                {'re': 'Hello', 'msg': '1'},
                {'re': 'Fancy', 'msg': '2'},
                {'re': '[wW]orld', 'msg': '3'}
            ]
        )

        for n, m in mocks.items():
            if n == 'reply':
                m.assert_has_calls([call('1'), call('3')])
            else:
                m.assert_not_called()
