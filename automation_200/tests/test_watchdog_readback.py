import hashlib
import json
import unittest

from automation_200 import watchdog_readback as readback


class WatchdogReadbackTests(unittest.TestCase):
    def setUp(self):
        commit = "a" * 40
        repository = {"full_name": readback.REPO}
        success = {"status": "completed", "conclusion": "success"}
        self.run = {
            **success, "id": 123, "run_attempt": 1, "repository": repository,
            "head_repository": repository, "path": readback.WORKFLOW,
            "head_branch": "main", "head_sha": commit, "event": "schedule",
        }
        self.step = {
            **success, "name": readback.HANDOFF_STEP,
            "started_at": "2026-11-09T06:54:54Z", "completed_at": "2026-11-09T06:54:54Z",
        }
        self.job = {
            **success, "id": 456, "name": "audit", "run_id": 123, "run_attempt": 1,
            "head_sha": commit, "steps": [self.step],
        }
        self.packet = {
            "schema": "cf0.work_handoff.v1", "source_commit": commit, "watchdog_event": "schedule",
            "assembled_utc": "2026-11-09T06:54:54+00:00", "execution_authorized": False,
            "hp": {"identity_attested": False, "scheduled_receipt_origin": "unverified"},
            "next_source_proposals": ["CF-119"],
        }

    def packet_bytes(self, **changes):
        return json.dumps({**self.packet, **changes}, sort_keys=True, separators=(",", ":")).encode("ascii")

    def log_line(self, packet=None):
        raw = self.packet_bytes() if packet is None else packet
        return b"2026-11-09T06:54:54.8882137Z CF0_WORK_HANDOFF=" + raw + b"\r\n"

    def test_binds_exact_bytes_and_ignores_shell_echoes(self):
        log = b"2026-11-09T06:54:54.2Z sed -n 's/^CF0_WORK_HANDOFF=//p'\n" + self.log_line()
        self.assertEqual(readback.record_readback(self.run, self.job, log), {
            "schema": "cf0.work_handoff_readback.v1",
            "watchdog_run_id": 123, "watchdog_run_attempt": 1, "watchdog_job_id": 456,
            "watchdog_event": "schedule", "source_commit": "a" * 40,
            "packet_assembled_utc": "2026-11-09T06:54:54+00:00",
            "packet_sha256": hashlib.sha256(self.packet_bytes()).hexdigest(),
            "execution_authorized": False,
        })

    def test_requires_the_exact_successful_job_attempt_and_main_workflow(self):
        log = self.log_line()
        for run, job in (
            ({**self.run, "head_branch": "feature"}, self.job),
            ({**self.run, "path": ".github/workflows/other.yml"}, self.job),
            ({**self.run, "head_repository": {"full_name": "another/repo"}}, self.job),
            (self.run, {**self.job, "run_attempt": 2}),
            (self.run, {**self.job, "run_id": 999}),
            (self.run, {**self.job, "conclusion": "failure"}),
            (self.run, {**self.job, "steps": [{**self.step, "conclusion": "skipped"}]}),
        ):
            with self.subTest(run=run, job=job), self.assertRaises(ValueError):
                readback.record_readback(run, job, log)

    def test_rejects_missing_duplicate_ambiguous_and_oversized_packets(self):
        raw = self.packet_bytes()
        for log in (
            b"",
            self.log_line() * 2,
            self.log_line(raw.replace(b'{', b'{"execution_authorized":false,', 1)),
            self.log_line(b" " + raw),
            self.log_line(b" " * (readback.MAX_PACKET_BYTES + 1)),
            b"x" * (readback.MAX_LOG_BYTES + 1),
        ):
            with self.subTest(size=len(log)), self.assertRaises(ValueError):
                readback.record_readback(self.run, self.job, log)

    def test_rejects_packet_source_time_and_authority_drift(self):
        for changes in (
            {"source_commit": "b" * 40},
            {"watchdog_event": "push"},
            {"assembled_utc": "2026-11-09T06:54:55+00:00"},
            {"assembled_utc": "2026-11-09T06:54:54"},
            {"execution_authorized": True},
            {"hp": {"identity_attested": True, "scheduled_receipt_origin": "unverified"}},
            {"hp": {"identity_attested": False, "scheduled_receipt_origin": "verified"}},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                readback.record_readback(self.run, self.job, self.log_line(self.packet_bytes(**changes)))

    def test_rejects_time_window_and_identity_edge_cases(self):
        log = self.log_line()
        cases = (
            ({**self.run, "id": True}, self.job, log),
            ({**self.run, "run_attempt": 0}, self.job, log),
            ({**self.run, "head_sha": "A" * 40}, self.job, log),
            (self.run, {**self.job, "id": True}, log),
            (self.run, {**self.job, "steps": [{**self.step, "started_at": "2026-11-09T06:54:55Z"}]}, log),
            (self.run, {**self.job, "steps": [{**self.step, "completed_at": "2026-11-09T06:54:53Z"}]}, log),
            (self.run, {**self.job, "steps": [{**self.step, "started_at": "2026-11-09T06:54:54"}]}, log),
            (self.run, {**self.job, "steps": [{**self.step, "completed_at": "2026-11-09T06:54:54+01:00"}]}, log),
            (self.run, self.job, b"2026-11-09T06:54:55.8882137Z CF0_WORK_HANDOFF=" + self.packet_bytes() + b"\\n"),
        )
        for run, job, packet_log in cases:
            with self.subTest(run_id=run.get("id"), job_id=job.get("id"), log=packet_log[:48]):
                with self.assertRaises(ValueError):
                    readback.record_readback(run, job, packet_log)
