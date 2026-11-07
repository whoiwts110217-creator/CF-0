import tempfile
import unittest
from pathlib import Path
from ai_tracker.tracker import append, report, validate

class TrackerTests(unittest.TestCase):
    def event(self, action, target="board", **kwargs):
        return dict(timestamp="2026-11-07T00:00:00+00:00", event=action,
                    target=target, evidence=kwargs.get("evidence", "https://example.org/item"),
                    operator="CF-0", test=kwargs.get("test", ""))

    def test_lifecycle_and_report(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "events.jsonl"
            for action in ("discover", "draft", "post", "reply"):
                append(path, self.event(action))
            self.assertEqual(report(path)["states"]["responded"], 1)
            append(path, self.event("verify", test="reproduce public test"))
            self.assertEqual(report(path)["verified_agents"], 1)

    def test_no_false_verified_or_post(self):
        with self.assertRaises(ValueError):
            validate(self.event("verify", test="proof"), [])
        with self.assertRaises(ValueError):
            validate(self.event("post", evidence="unconfirmed"), [self.event("discover"), self.event("draft")])

    def test_secrets_rejected(self):
        with self.assertRaises(ValueError):
            validate(self.event("discover", evidence="api_key=abc"), [])

    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            validate(self.event("discover"), [self.event("discover")])

if __name__ == "__main__":
    unittest.main()
