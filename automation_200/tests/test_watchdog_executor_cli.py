"""Synthetic offline tests: do not access the live owner account or Windows HP."""
import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from automation_200.watchdog_executor_cli import main, verify_documents, OUTPUT_SCHEMA
from automation_200.watchdog_readback import WORKFLOW, HANDOFF_STEP, REPO
from automation_200.watchdog_executor_result import MARKER


class ProviderVerificationCLITests(unittest.TestCase):
    def setUp(self):
        self.commit = "c" * 40
        success = {"status": "completed", "conclusion": "success"}
        self.run = {
            **success, "id": 123, "run_attempt": 1,
            "repository": {"full_name": REPO},
            "head_repository": {"full_name": REPO},
            "path": WORKFLOW, "head_branch": "main",
            "head_sha": self.commit, "event": "schedule",
        }
        self.job = {
            **success, "id": 456, "run_id": 123, "run_attempt": 1,
            "name": "audit", "head_sha": self.commit,
            "steps": [{
                **success, "name": HANDOFF_STEP,
                "started_at": "2026-11-09T06:54:54Z",
                "completed_at": "2026-11-09T06:54:54Z",
            }],
        }
        packet = {
            "schema": "cf0.work_handoff.v1",
            "source_commit": self.commit, "watchdog_event": "schedule",
            "assembled_utc": "2026-11-09T06:54:54+00:00",
            "execution_authorized": False,
            "hp": {
                "identity_attested": False,
                "scheduled_receipt_origin": "unverified",
            },
        }
        raw = json.dumps(packet, sort_keys=True, separators=(",", ":")).encode("ascii")
        self.digest = hashlib.sha256(raw).hexdigest()
        prefix = b"2026-11-09T06:54:54.8882137Z "
        self.log = (
            prefix + b"CF0_WORK_HANDOFF=" + raw + b"\n"
            + prefix + b"CF0_WORK_HANDOFF_SHA256=" + self.digest.encode("ascii") + b"\n"
        )
        self.decision = {
            "schema": "cf0.executor_packet_decision.v2",
            "watchdog_run_id": 123,
            "watchdog_run_attempt": 1,
            "watchdog_job_id": 456,
            "source_commit": self.commit,
            "packet_sha256": self.digest,
            "decision": "accepted_source_only",
            "execution_authorized": False,
        }
        self.private_id = "private-native-run-123"
        complete = "2026-11-09T06:55:00Z"
        self.provider = {
            "title": "PRIVATE do not disclose",
            "run_details": {
                "last_run": {
                    "id": self.private_id,
                    "recorded_status": "completed",
                    "completed_at": complete,
                },
                "latest_result": {
                    "run_id": self.private_id,
                    "completed_at": complete,
                    "content_truncated": False,
                    "is_failure_message": False,
                    "content_text": MARKER + json.dumps(self.decision),
                },
            },
        }

    def test_real_validator_chain_produces_only_sanitized_evidence(self):
        result = verify_documents(self.run, self.job, self.log, self.provider)
        self.assertEqual(result["schema"], OUTPUT_SCHEMA)
        self.assertEqual(result["packet_sha256"], self.digest)
        self.assertTrue(result["recorded_completed_result_matched"])
        self.assertEqual(result["executor_run_id_source"], "independent_provider_record")
        for field in ("execution_authorized", "hp_identity_attested",
                      "provider_origin_cryptographically_attested",
                      "hp_scheduled_origin_verified"):
            self.assertIs(result[field], False)
        output = json.dumps(result)
        self.assertNotIn(self.private_id, output)
        self.assertNotIn("PRIVATE do not disclose", output)
        self.assertNotIn("run_details", output)

    def test_identity_mutation_and_bad_digest_fail_closed(self):
        cases = [
            ({**self.run, "head_branch": "other"}, self.job, self.log, self.provider),
            (self.run, {**self.job, "run_attempt": 2}, self.log, self.provider),
            (self.run, self.job, self.log.replace(self.digest.encode(), b"0" * 64), self.provider),
            (self.run, self.job, self.log, {
                **self.provider,
                "run_details": {
                    **self.provider["run_details"],
                    "latest_result": {
                        **self.provider["run_details"]["latest_result"],
                        "content_truncated": True,
                    },
                },
            }),
        ]
        for run, job, log, provider in cases:
            with self.subTest(run=run.get("head_branch"), attempt=job.get("run_attempt")), self.assertRaises(ValueError):
                verify_documents(run, job, log, provider)

    def test_cli_never_prints_raw_private_result_or_id(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            (p / "run.json").write_text(json.dumps(self.run), encoding="utf-8")
            (p / "job.json").write_text(json.dumps(self.job), encoding="utf-8")
            (p / "log.txt").write_bytes(self.log)
            (p / "private.json").write_text(json.dumps(self.provider), encoding="utf-8")
            args = [
                "--run-metadata", str(p / "run.json"),
                "--job-metadata", str(p / "job.json"),
                "--job-log", str(p / "log.txt"),
                "--private-executor-result", str(p / "private.json"),
            ]
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(main(args), 0)
            self.assertEqual(json.loads(out.getvalue())["decision"], "accepted_source_only")
            self.assertNotIn(self.private_id, out.getvalue())
            self.assertNotIn("PRIVATE", out.getvalue())
            (p / "private.json").write_text("not JSON: " + self.private_id)
            err = io.StringIO()
            with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as code:
                main(args)
            self.assertEqual(code.exception.code, 2)
            self.assertIn("NOT VERIFIED", err.getvalue())
            self.assertNotIn(self.private_id, err.getvalue())


if __name__ == "__main__":
    unittest.main()
