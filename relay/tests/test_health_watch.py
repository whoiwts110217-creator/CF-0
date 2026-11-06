"""Offline public-report classification tests; no real HP access or writes."""
import base64
import json
import unittest
import urllib.error
from datetime import datetime, timezone

from relay.health_watch import URL, classify, watch


NOW = int(datetime(2026, 11, 6, 15, 0, tzinfo=timezone.utc).timestamp())


def sample(seconds_ago=0, **changes):
    report = {
        "schema": "cf0.hp_health.v1",
        "collected_utc": datetime.fromtimestamp(
            NOW - seconds_ago, tz=timezone.utc
        ).isoformat(timespec="seconds"),
        "db_exists": True,
        "receipt_count": 28,
        "ping_receipt_count": 3,
        "last_receipt_status": "completed",
        "error": None,
    }
    report.update(changes)
    return report


def encoded(report):
    return {"encoding": "base64",
            "content": base64.b64encode(json.dumps(report).encode()).decode()}


class HealthWatchTests(unittest.TestCase):
    def test_read_only_fixed_public_path(self):
        called = []
        def read(url):
            called.append(url)
            return encoded(sample(100))
        result = watch(now=NOW, getter=read)
        self.assertEqual(called, [URL])
        self.assertEqual(result["state"], "fresh_public_report")
        self.assertEqual(result["report_age_seconds"], 100)
        self.assertEqual(result["reported_receipt_count"], 28)
        self.assertEqual(result["scheduled_origin"], "not_verified_by_public_report")
        self.assertEqual(result["seven_day_unattended"], "not_verified")

    def test_missing_report_does_not_fake_hp_heartbeat(self):
        def missing(url):
            raise urllib.error.HTTPError(url, 404, "Not Found", None, None)
        result = watch(now=NOW, getter=missing)
        self.assertEqual(result["state"], "not_published")
        self.assertNotIn("collected_utc", result)
        self.assertNotIn("reported_receipt_count", result)
        self.assertEqual(result["physical_hp_identity"], "not_attested_by_public_report")

    def test_staleness_thresholds_bound_scheduled_evidence(self):
        expected = [
            (0, "fresh_public_report"),
            (30 * 60, "fresh_public_report"),
            (45 * 60, "fresh_public_report"),
            (45 * 60 + 1, "late"),
            (2 * 60 * 60, "late"),
            (2 * 60 * 60 + 1, "stale"),
        ]
        for seconds, state in expected:
            with self.subTest(seconds=seconds):
                self.assertEqual(classify(sample(seconds), NOW)["state"], state)

    def test_future_clock_skew_not_fresh(self):
        self.assertEqual(classify(sample(-60), NOW)["state"], "fresh_public_report")
        self.assertEqual(classify(sample(-301), NOW)["state"], "future_timestamp")

    def test_reporter_error_cannot_be_labeled_healthy(self):
        examples = [
            {"error": "state_unavailable"},
            {"db_exists": False, "receipt_count": None, "ping_receipt_count": None},
            {"error": "malformed_receipt"},
        ]
        for patch in examples:
            with self.subTest(patch=patch):
                value = classify(sample(30, **patch), NOW)
                self.assertEqual(value["state"], "reported_problem")
                self.assertTrue(value["reported_problem"])

    def test_strict_schema_rejects_raw_private_information(self):
        private = sample()
        private["local_path"] = "C:/Users/hidden/private.sqlite3"
        result = watch(now=NOW, getter=lambda _: encoded(private))
        self.assertEqual(result["state"], "invalid")
        self.assertNotIn("local_path", result)
        self.assertNotIn("C:/Users", json.dumps(result))

    def test_invalid_timestamps_and_types(self):
        for patch in (
            {"collected_utc": "not-a-time"},
            {"collected_utc": "2026-11-06T15:00:00"},
            {"collected_utc": "2026-11-06T10:00:00-05:00"},
            {"receipt_count": True},
            {"ping_receipt_count": -1},
            {"db_exists": "yes"},
            {"error": "arbitrary sensitive error output"},
        ):
            with self.subTest(patch=patch):
                self.assertEqual(classify(sample(**patch), NOW)["state"], "invalid")

    def test_malformed_contents_never_dump_raw_remote_text(self):
        sensitive = "personal detail from an untrusted public file"
        cases = [
            {"encoding": "utf-8", "content": sensitive},
            {"encoding": "base64", "content": "!!!!" + sensitive},
            {"encoding": "base64", "content": base64.b64encode(b"x" * 1100).decode()},
            {"encoding": "base64", "content": base64.b64encode(b"not-json").decode()},
        ]
        for document in cases:
            with self.subTest(document=document.get("encoding")):
                result = watch(now=NOW, getter=lambda _: document)
                self.assertEqual(result["state"], "invalid")
                self.assertNotIn(sensitive, json.dumps(result))

    def test_non_404_http_failure_is_unavailable_not_missing(self):
        def restricted(url):
            raise urllib.error.HTTPError(url, 403, "Forbidden", None, None)
        self.assertEqual(watch(now=NOW, getter=restricted)["state"], "unavailable")

    def test_no_report_state_can_prove_unattended_operation(self):
        for seconds in (0, 4000, 10000, -400):
            outcome = classify(sample(seconds), NOW)
            self.assertEqual(outcome["seven_day_unattended"], "not_verified")
            self.assertEqual(outcome["physical_hp_identity"], "not_attested_by_public_report")


if __name__ == "__main__":
    unittest.main()
