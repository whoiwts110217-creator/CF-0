"""Read-only, offline tests: no ChatGPT action, HP operation or fake revenue."""
import json
import unittest

from automation_200.watchdog_executor_result import (
    MARKER, correlate_recorded_executor_result,
)


class RecordedExecutorTests(unittest.TestCase):
    def setUp(self):
        self.readback = {
            "schema": "cf0.work_handoff_readback.v1", "watchdog_run_id": 13,
            "watchdog_run_attempt": 1, "packet_sha256": "a" * 64,
            "packet_assembled_utc": "2026-11-09T23:17:38+00:00",
            "execution_authorized": False,
        }
        self.ack = {
            "schema": "cf0.executor_packet_decision.v1",
            "watchdog_run_id": 13, "watchdog_run_attempt": 1,
            "packet_sha256": "a" * 64, "executor_run_id": "exec-4",
            "decision": "deferred", "execution_authorized": False,
        }
        self.record = {"run_details": {
            "last_run": {"id": "exec-4", "recorded_status": "completed",
                         "completed_at": "2026-11-09T23:47:54Z"},
            "latest_result": {"run_id": "exec-4", "content_truncated": False,
                              "is_failure_message": False,
                              "completed_at": "2026-11-09T23:47:54Z",
                              "content_text": MARKER + json.dumps(self.ack)},
        }}

    def with_result(self, **overrides):
        return {"run_details": {
            **self.record["run_details"],
            "latest_result": {**self.record["run_details"]["latest_result"],
                              **overrides},
        }}

    def test_exact_recorded_match_is_non_authorizing(self):
        result = correlate_recorded_executor_result(self.readback, self.record)
        self.assertTrue(result["correlated"])
        self.assertTrue(result["recorded_completed_result_matched"])
        self.assertEqual(result["decision"], "deferred")
        self.assertFalse(result["acknowledgement_origin_verified"])
        self.assertFalse(result["provider_origin_cryptographically_attested"])
        self.assertFalse(result["hp_identity_attested"])
        self.assertFalse(result["execution_authorized"])

    def test_actual_missing_marker_remains_unverified(self):
        with self.assertRaises(ValueError):
            correlate_recorded_executor_result(
                self.readback, self.with_result(content_text="87/200 checked")
            )

    def test_invalid_result_provenance_rejected(self):
        for change in (
            {"run_id": "another"}, {"content_truncated": True},
            {"is_failure_message": True},
            {"completed_at": "2026-11-09T23:47:53Z"},
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                correlate_recorded_executor_result(
                    self.readback, self.with_result(**change))
        for change in ({"id": "another"}, {"recorded_status": "failed"}):
            task = {"run_details": {
                **self.record["run_details"],
                "last_run": {**self.record["run_details"]["last_run"],
                             **change},
            }}
            with self.subTest(change=change), self.assertRaises(ValueError):
                correlate_recorded_executor_result(self.readback, task)

    def test_source_packet_and_recorded_run_mismatch_rejected(self):
        for patch in (
            {"packet_sha256": "b" * 64},
            {"watchdog_run_attempt": 2},
            {"executor_run_id": "someone-else"},
            {"execution_authorized": True},
        ):
            content = MARKER + json.dumps({**self.ack, **patch})
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                correlate_recorded_executor_result(
                    self.readback, self.with_result(content_text=content))

    def test_duplicate_or_ambiguous_markers_rejected(self):
        line = self.record["run_details"]["latest_result"]["content_text"]
        for text in (
            line + "\n" + line,
            MARKER + '{"schema":"x","schema":"y"}',
            MARKER + "not-json",
            "  " + line,
            "",
            "x" * 120001,
            MARKER + "{" + "x" * 4096 + "}",
        ):
            with self.subTest(text=text[:48]), self.assertRaises(ValueError):
                correlate_recorded_executor_result(
                    self.readback, self.with_result(content_text=text))

    def test_bad_timestamps_and_future_packet_rejected(self):
        for stamp in (
            "2026-11-09T23:17:38",
            "2026-11-09T23:17:38+01:00",
            "2026-11-10T03:17:38Z",
        ):
            with self.subTest(stamp=stamp), self.assertRaises(ValueError):
                correlate_recorded_executor_result(
                    {**self.readback, "packet_assembled_utc": stamp},
                    self.record,
                )

    def test_non_dictionary_and_missing_run_are_not_decisions(self):
        for record in (None, [], {}, {"run_details": {}}):
            with self.subTest(record=record), self.assertRaises(ValueError):
                correlate_recorded_executor_result(self.readback, record)


if __name__ == "__main__":
    unittest.main()
