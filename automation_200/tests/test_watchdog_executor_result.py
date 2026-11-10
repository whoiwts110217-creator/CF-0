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

    def _v2_fixture(self):
        readback = {
            **self.readback,
            "watchdog_job_id": 456,
            "source_commit": "c" * 40,
        }
        decision = {
            "schema": "cf0.executor_packet_decision.v2",
            "watchdog_run_id": readback["watchdog_run_id"],
            "watchdog_run_attempt": readback["watchdog_run_attempt"],
            "watchdog_job_id": readback["watchdog_job_id"],
            "source_commit": readback["source_commit"],
            "packet_sha256": readback["packet_sha256"],
            "decision": "deferred",
            "execution_authorized": False,
        }
        record = self.with_result(content_text=MARKER + json.dumps(decision))
        return readback, decision, record

    def test_v2_provider_bind_uses_native_run_identity(self):
        readback, decision, record = self._v2_fixture()
        self.assertNotIn("executor_run_id", decision)
        matched = correlate_recorded_executor_result(readback, record)
        self.assertTrue(matched["correlated"])
        self.assertEqual(matched["executor_run_id"], "exec-4")
        self.assertEqual(matched["executor_run_id_source"], "independent_provider_record")
        self.assertEqual(matched["decision"], "deferred")
        self.assertFalse(matched["execution_authorized"])
        self.assertFalse(matched["acknowledgement_origin_verified"])
        self.assertFalse(matched["provider_origin_cryptographically_attested"])
        self.assertFalse(matched["hp_identity_attested"])

    def test_v2_rejects_extra_self_claimed_identity_and_wrong_packet(self):
        readback, decision, _ = self._v2_fixture()
        variations = (
            {"executor_run_id": "invented"},
            {"watchdog_job_id": 789},
            {"watchdog_run_id": 15},
            {"watchdog_run_attempt": 3},
            {"source_commit": "e" * 40},
            {"source_commit": "not-a-commit"},
            {"packet_sha256": "b" * 64},
            {"decision": "executed"},
            {"execution_authorized": True},
        )
        for change in variations:
            with self.subTest(change=change):
                record = self.with_result(content_text=MARKER + json.dumps({**decision, **change}))
                with self.assertRaises(ValueError):
                    correlate_recorded_executor_result(readback, record)

    def test_v2_rejects_missing_provider_or_stale_fabricated_result(self):
        readback, decision, record = self._v2_fixture()
        for bad in (
            self.with_result(content_text="No packet consumed."),
            self.with_result(content_text=MARKER + json.dumps(decision),
                             content_truncated=True),
            self.with_result(content_text=MARKER + json.dumps(decision),
                             run_id="another-run"),
        ):
            with self.subTest(result=bad["run_details"]["latest_result"]):
                with self.assertRaises(ValueError):
                    correlate_recorded_executor_result(readback, bad)

    def test_v2_missing_fields_rejected(self):
        readback, decision, _ = self._v2_fixture()
        for key in ("watchdog_job_id", "source_commit", "decision"):
            with self.subTest(key=key):
                incomplete = {name: value for name, value in decision.items() if name != key}
                record = self.with_result(content_text=MARKER + json.dumps(incomplete))
                with self.assertRaises(ValueError):
                    correlate_recorded_executor_result(readback, record)

    def test_actual_provider_native_top_level_result_is_supported(self):
        # Matches Automations.peek: latest_result is a sibling of run_details,
        # not nested within it. Do not require a fabricated model run ID.
        readback, decision, nested = self._v2_fixture()
        native = {
            "run_details": {
                "last_run": nested["run_details"]["last_run"],
            },
            "latest_result": nested["run_details"]["latest_result"],
        }
        matched = correlate_recorded_executor_result(readback, native)
        self.assertTrue(matched["recorded_completed_result_matched"])
        self.assertEqual(matched["executor_run_id_source"],
                         "independent_provider_record")
        self.assertFalse(matched["execution_authorized"])
        self.assertFalse(matched["hp_identity_attested"])

    def test_conflicting_native_and_nested_results_fail_closed(self):
        readback, decision, nested = self._v2_fixture()
        top = dict(nested["run_details"]["latest_result"])
        top["content_text"] = "A contradictory provider result"
        mixed = {
            "run_details": nested["run_details"],
            "latest_result": top,
        }
        with self.assertRaisesRegex(ValueError, "conflicting recorded"):
            correlate_recorded_executor_result(readback, mixed)

    def test_matching_duplicate_positions_are_unambiguous(self):
        readback, decision, nested = self._v2_fixture()
        duplicated = {
            "run_details": nested["run_details"],
            "latest_result": dict(nested["run_details"]["latest_result"]),
        }
        self.assertTrue(correlate_recorded_executor_result(
            readback, duplicated)["correlated"])

    def test_missing_or_null_native_result_does_not_fall_back_silently(self):
        readback, decision, nested = self._v2_fixture()
        native = {
            "run_details": {
                "last_run": nested["run_details"]["last_run"],
                "latest_result": nested["run_details"]["latest_result"],
            },
            "latest_result": None,
        }
        with self.assertRaises(ValueError):
            correlate_recorded_executor_result(readback, native)
        del native["run_details"]["latest_result"]
        with self.assertRaises(ValueError):
            correlate_recorded_executor_result(readback, native)

    def test_non_dictionary_and_missing_run_are_not_decisions(self):
        for record in (None, [], {}, {"run_details": {}}):
            with self.subTest(record=record), self.assertRaises(ValueError):
                correlate_recorded_executor_result(self.readback, record)


if __name__ == "__main__":
    unittest.main()
