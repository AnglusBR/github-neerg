import unittest

from github_neerg.activity import normalize_event
from github_neerg.report import render_report


class ReportTests(unittest.TestCase):
    def test_normalize_event_discards_unstable_payload(self):
        event = {
            "id": "123",
            "type": "PushEvent",
            "created_at": "2026-10-27T10:00:00Z",
            "repo": {"name": "AnglusBR/example"},
            "payload": {"size": 2, "ref": "refs/heads/main", "commits": [{"secret": "ignored"}]},
        }
        self.assertEqual(
            normalize_event(event),
            {
                "id": "123",
                "type": "PushEvent",
                "repo": "AnglusBR/example",
                "created_at": "2026-10-27T10:00:00Z",
                "ref": "refs/heads/main",
                "size": 2,
            },
        )

    def test_report_is_deterministic(self):
        events = [{
            "id": "123",
            "type": "IssuesEvent",
            "repo": "AnglusBR/example",
            "created_at": "2026-10-27T10:00:00Z",
            "action": "opened",
            "number": 7,
        }]
        first = render_report("AnglusBR", events, "daily", "2026-10-27")
        second = render_report("AnglusBR", events, "daily", "2026-10-27")
        self.assertEqual(first, second)
        self.assertIn("issue", first)
        self.assertIn("#7", first)


if __name__ == "__main__":
    unittest.main()

