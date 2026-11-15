"""Regression for mixed-precision GitHub watchdog timestamps (source-only)."""
import hashlib
import json
import unittest

from automation_200.watchdog_readback import record_readback, WORKFLOW
from relay.channel_audit import REPO

COMMIT = "a" * 40


def fixture(assembled, logged, started="2026-11-10T00:53:36Z", completed="2026-11-10T00:53:36Z"):
    packet = {
        "schema": "cf0.work_handoff.v1",
        "source_commit": COMMIT,
        "watchdog_event": "schedule",
        "assembled_utc": assembled,
        "execution_authorized": False,
        "hp": {"identity_attested": False, "scheduled_receipt_origin": "unverified"},
    }
    raw = json.dumps(packet, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")
    log = (logged + " CF0_WORK_HANDOFF=").encode() + raw + b"\n"
    log += (logged + " CF0_WORK_HANDOFF_SHA256=" + hashlib.sha256(raw).hexdigest() + "\n").encode()
    run = {
        "id": 101, "run_attempt": 1, "head_sha": COMMIT, "event": "schedule",
        "repository": {"full_name": REPO}, "head_repository": {"full_name": REPO},
        "path": WORKFLOW, "head_branch": "main", "status": "completed", "conclusion": "success",
    }
    job = {
        "id": 202, "run_id": 101, "run_attempt": 1, "head_sha": COMMIT,
        "name": "audit", "status": "completed", "conclusion": "success",
        "steps": [{
            "name": "Propose next source-only work under founder policy",
            "status": "completed", "conclusion": "success",
            "started_at": started, "completed_at": completed,
        }],
    }
    return run, job, log


class TimestampPrecisionTests(unittest.TestCase):
    def test_fractional_packet_and_log_same_second(self):
        args = fixture("2026-11-10T00:53:36.500Z", "2026-11-10T00:53:36.800Z")
        self.assertEqual(record_readback(*args)["watchdog_run_id"], 101)

    def test_adjacent_earlier_second_rejected(self):
        args = fixture("2026-11-10T00:53:35.999Z", "2026-11-10T00:53:36Z")
        with self.assertRaisesRegex(ValueError, "outside"):
            record_readback(*args)

    def test_adjacent_later_second_rejected(self):
        args = fixture("2026-11-10T00:53:36Z", "2026-11-10T00:53:37.001Z")
        with self.assertRaisesRegex(ValueError, "outside"):
            record_readback(*args)

    def test_same_second_inverted_fraction_accepted_at_step_precision(self):
        args = fixture("2026-11-10T00:53:36.800Z", "2026-11-10T00:53:36.500Z")
        self.assertEqual(record_readback(*args)["watchdog_run_id"], 101)


if __name__ == "__main__":
    unittest.main()
