from unittest import TestCase

from github import format_event, ghevent, git


class TestGithubFormat(TestCase):
    def test_only_git_is_command(self):
        # All user-facing commands should be under `.git ...`.
        assert hasattr(git, "_hook")
        assert not hasattr(ghevent, "_hook")

    def test_push_event(self):
        event = {
            "type": "PushEvent",
            "actor": {"login": "alice"},
            "repo": {"name": "octo-org/octo-repo"},
            "payload": {
                "ref": "refs/heads/main",
                "size": 2,
                "before": "1111111111111111111111111111111111111111",
                "head": "abcdef0123456789012345678901234567890123",
            },
        }
        out = format_event(event)
        assert out.startswith("[octo-repo] alice pushed 2 commit(s)")
        assert "to main" in out
        assert "https://github.com/octo-org/octo-repo/compare/" in out

    def test_pull_request_event(self):
        event = {
            "type": "PullRequestEvent",
            "actor": {"login": "bob"},
            "repo": {"name": "octo-org/octo-repo"},
            "payload": {
                "action": "opened",
                "pull_request": {
                    "number": 12,
                    "title": "Fix CI",
                    "html_url": "https://github.com/octo-org/octo-repo/pull/12",
                },
            },
        }
        out = format_event(event)
        assert out.startswith("[octo-repo] bob opened PR #12")
        assert "\"Fix CI\"" in out
        assert "https://github.com/octo-org/octo-repo/pull/12" in out

    def test_fallback(self):
        event = {"type": "UnknownEvent", "actor": {"login": "carol"}, "repo": {"name": "x/y"}}
        out = format_event(event)
        assert "[y] carol did UnknownEvent in x/y" == out
