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

    def test_unchanged_metrics_within_30_minutes_skip_commit(self):
        old = sample()
        repo = Repo(dict(sha="old", content=base64.b64encode(sanitized(old)).decode()))
        new = sample()
        new["collected_utc"] = "2026-11-06T12:05:00+00:00"
        self.assertEqual(publish(repo, new), "unchanged")
        self.assertEqual(len(repo.calls), 1)

    def test_heartbeat_after_30_minutes_publishes(self):
        old = sample()
        repo = Repo(dict(sha="old", content=base64.b64encode(sanitized(old)).decode()))
        new = sample()
        new["collected_utc"] = "2026-11-06T12:30:00+00:00"
        self.assertEqual(publish(repo, new), "published")
        self.assertEqual(repo.calls[1][2]["sha"], "old")

    def test_changed_metrics_publish_immediately(self):
        old = sample()
        repo = Repo(dict(sha="old", content=base64.b64encode(sanitized(old)).decode()))
        new = sample()
        new["receipt_count"] += 1
        new["collected_utc"] = "2026-11-06T12:01:00+00:00"
        self.assertEqual(publish(repo, new), "published")

    def test_invalid_previous_timestamp_cannot_suppress(self):
        old = sample()
        old["collected_utc"] = "invalid"
        repo = Repo(dict(sha="old", content=base64.b64encode(
            __import__("json").dumps(old).encode()).decode()))
        self.assertEqual(publish(repo, sample()), "published")

    def test_non_utf8_previous_report_fails_open_to_new_publication(self):
        repo = Repo(dict(sha="old", content=base64.b64encode(bytes([255,254])).decode()))
        self.assertEqual(publish(repo, sample()), "published")
        self.assertEqual(repo.calls[1][2]["sha"], "old")

    def test_non_base64_previous_report_still_rejected(self):
        from cf_public_relay import RelayError
        repo = Repo(dict(sha="old", content="%%%%"))
        with self.assertRaises(RelayError):
            publish(repo, sample())
        self.assertEqual(len(repo.calls), 1)

    def test_ping_count_exceeding_total_rejected_before_network(self):
        data = sample()
        data["receipt_count"] = 2
        data["ping_receipt_count"] = 3
        repo = Repo()
        with self.assertRaisesRegex(ValueError, "inconsistent_health_counts"):
            publish(repo, data)
        self.assertEqual(repo.calls, [])

    def test_last_receipt_status_must_match_row_count(self):
        for patch in (
            {"receipt_count": 12, "last_receipt_status": None},
            {"receipt_count": 0, "ping_receipt_count": 0, "last_receipt_status": "completed"},
        ):
            with self.subTest(patch=patch):
                data = sample()
                data.update(patch)
                repo = Repo()
                with self.assertRaisesRegex(ValueError, "inconsistent_health_last_receipt"):
                    publish(repo, data)
                self.assertEqual(repo.calls, [])

    def test_invalid_padding_rejected_with_safe_error_without_write(self):
        from cf_public_relay import RelayError
        repo = Repo(dict(sha="old", content="a"))
        with self.assertRaisesRegex(RelayError, "^health_destination_invalid$") as caught:
            publish(repo, sample())
        self.assertTrue(caught.exception.__suppress_context__)
        self.assertEqual(len(repo.calls), 1)

    def test_oversized_untrusted_destination_rejected_without_decode_or_write(self):
        from cf_public_relay import RelayError
        repo = Repo(dict(sha="old", content="A" * 8193))
        with self.assertRaisesRegex(RelayError, "^health_destination_invalid$"):
            publish(repo, sample())
        self.assertEqual(len(repo.calls), 1)

    def test_invalid_count_rejected(self):
        data = sample()
        data["receipt_count"] = -1
        with self.assertRaises(ValueError):
            sanitized(data)

if __name__ == "__main__":
    unittest.main()
