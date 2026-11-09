"""Public source-only watchdog producer/readback integration regression.

No GitHub write, physical HP access, task execution or scheduler attestation.
Run: python -m unittest automation_200.tests.test_watchdog_packet_roundtrip -v
"""
import hashlib
import json
import unittest
from pathlib import Path

from automation_200.watchdog_handoff import build_handoff, handoff_digest
from automation_200.watchdog_readback import (
    HANDOFF_STEP, REPO, WORKFLOW, record_readback,
)

REGISTRY = Path(__file__).resolve().parents[1] / "registry.json"
COMMIT = "a" * 40
NOW = 1794207294  # fixed UTC timestamp for reproducibility


class WatchdogPacketRoundtripTests(unittest.TestCase):
    def test_actual_registry_handoff_can_be_bound_to_exact_log_packet(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        handoff, _proposal = build_handoff(
            registry, {}, {}, commit=COMMIT, event="schedule", now=NOW
        )
        self.assertEqual(handoff["registry"]["verified"], registry["completed"])
        self.assertFalse(handoff["execution_authorized"])
        self.assertEqual(handoff["hp"]["scheduled_receipt_origin"], "unverified")

        packet = json.dumps(
            handoff, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("ascii")
        stamp = handoff["assembled_utc"]
        self.assertTrue(stamp.endswith("+00:00"))
        step_stamp = stamp.replace("+00:00", "Z")
        repo = {"full_name": REPO}
        run = {
            "id": 1234, "run_attempt": 1, "head_sha": COMMIT,
            "head_branch": "main", "path": WORKFLOW, "event": "schedule",
            "repository": repo, "head_repository": repo,
            "status": "completed", "conclusion": "success",
        }
        job = {
            "id": 5678, "run_id": 1234, "run_attempt": 1,
            "head_sha": COMMIT, "name": "audit",
            "status": "completed", "conclusion": "success",
            "steps": [{
                "name": HANDOFF_STEP, "status": "completed",
                "conclusion": "success", "started_at": step_stamp,
                "completed_at": step_stamp,
            }],
        }
        log = step_stamp.encode("ascii") + b" CF0_WORK_HANDOFF=" + packet + b"\n"
        result = record_readback(run, job, log)
        self.assertEqual(result["packet_sha256"], hashlib.sha256(packet).hexdigest())
        self.assertEqual(result["packet_sha256"], handoff_digest(handoff))
        self.assertEqual(result["watchdog_run_id"], 1234)
        self.assertEqual(result["watchdog_run_attempt"], 1)
        self.assertFalse(result["execution_authorized"])

        # Even a successfully bound packet is not an executor decision or HP proof.
        self.assertNotIn("executor_decision", result)
        self.assertNotIn("physical_hp_identity_attested", result)

    def test_different_packet_bytes_do_not_inherit_prior_digest(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        a, _ = build_handoff(registry, {}, {}, commit=COMMIT, event="push", now=NOW)
        b, _ = build_handoff(registry, {}, {}, commit=COMMIT, event="schedule", now=NOW)
        encode = lambda p: json.dumps(p, sort_keys=True, separators=(",", ":")).encode("ascii")
        self.assertNotEqual(hashlib.sha256(encode(a)).digest(),
                            hashlib.sha256(encode(b)).digest())


if __name__ == "__main__":
    unittest.main()
