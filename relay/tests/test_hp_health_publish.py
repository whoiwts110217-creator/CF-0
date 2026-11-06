import base64
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from cf_hp_health_publish import PATH, publish, sanitized

def sample():
    return dict(schema="cf0.hp_health.v1", collected_utc="2026-11-06T12:00:00+00:00", db_exists=True, receipt_count=12, ping_receipt_count=2, last_receipt_status="completed", error=None)

class Repo:
    def __init__(self, current=None):
        self.current = current
        self.calls = []
    def request(self, method, path, payload=None):
        self.calls.append((method, path, payload))
        return self.current if method == "GET" else {}

class PublisherTests(unittest.TestCase):
    def test_fixed_path(self):
        repo = Repo()
        self.assertEqual(publish(repo, sample()), "published")
        self.assertEqual(repo.calls[1][1], PATH)
        self.assertEqual(base64.b64decode(repo.calls[1][2]["content"]), sanitized(sample()))
    def test_unchanged_report_no_commit(self):
        repo = Repo(dict(sha="old", content=base64.b64encode(sanitized(sample())).decode()))
        self.assertEqual(publish(repo, sample()), "unchanged")
        self.assertEqual(len(repo.calls), 1)
    def test_extra_field_rejected(self):
        repo = Repo()
        data = sample()
        data["unexpected"] = "private"
        with self.assertRaises(ValueError):
            publish(repo, data)
        self.assertEqual(repo.calls, [])
    def test_existing_report_change_uses_sha(self):
        original = sample()
        existing = dict(sha="known-content-sha", content=base64.b64encode(sanitized(original)).decode())
        repo = Repo(existing)
        updated = sample()
        updated["receipt_count"] = 13
        self.assertEqual(publish(repo, updated), "published")
        self.assertEqual(repo.calls[1][2]["sha"], "known-content-sha")

    def test_malformed_destination_rejected(self):
        from cf_public_relay import RelayError
        repo = Repo(dict(sha="known-content-sha", content="not base64!!"))
        with self.assertRaises(RelayError):
            publish(repo, sample())
        self.assertEqual(len(repo.calls), 1)

    def test_invalid_count_rejected(self):
        data = sample()
        data["receipt_count"] = -1
        with self.assertRaises(ValueError):
            sanitized(data)

if __name__ == "__main__":
    unittest.main()
