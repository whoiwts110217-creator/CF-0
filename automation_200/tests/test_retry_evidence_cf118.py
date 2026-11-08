"""Offline CF-118 journal tests; no HP or network access."""
import json
from unittest.mock import patch
import tempfile
import unittest
from pathlib import Path

from automation_200.retry_evidence import append_failure, read_events


class RetryEvidenceTests(unittest.TestCase):
    def test_append_reload_and_detect_tamper(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "attempts.jsonl"
            allowed = {"CF-118", "CF-119"}
            append_failure(path, allowed, "CF-118", 1000)
            append_failure(path, allowed, "CF-118", 1001)
            append_failure(path, allowed, "CF-119", 1002)
            events, attempts = read_events(path, allowed)
            self.assertEqual(len(events), 3)
            self.assertEqual(attempts["CF-118"], {"failures": 2, "failed_at": 1001})
            lines = path.read_text().splitlines()
            altered = json.loads(lines[0])
            altered["failed_at"] = 999
            lines[0] = json.dumps(altered)
            path.write_text("\n".join(lines) + "\n")
            with self.assertRaises(ValueError):
                read_events(path, allowed)

    def test_reject_invalid_ids_times_and_regression(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "attempts.jsonl"
            ids = {"CF-118"}
            for task, stamp in (("UNKNOWN", 1000), ("CF-118", True), ("CF-118", -1)):
                with self.assertRaises(ValueError):
                    append_failure(path, ids, task, stamp)
            self.assertFalse(path.exists())
            append_failure(path, ids, "CF-118", 1000)
            with self.assertRaises(ValueError):
                append_failure(path, ids, "CF-118", 999)
            self.assertEqual(read_events(path, ids)[1]["CF-118"]["failures"], 1)

    def test_replace_failure_preserves_prior_journal(self):
        # Simulated interruption at the atomic replacement boundary.
        # The existing journal must survive and temporary files be removed.
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "attempts.jsonl"
            ids = {"CF-118"}
            append_failure(path, ids, "CF-118", 1000)
            before = path.read_bytes()
            with patch("automation_200.retry_evidence.os.replace", side_effect=OSError("simulated interruption")):
                with self.assertRaisesRegex(OSError, "simulated interruption"):
                    append_failure(path, ids, "CF-118", 1001)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(read_events(path, ids)[1]["CF-118"]["failures"], 1)
            self.assertEqual(list(Path(root).glob(".retry-journal-*")), [])
            append_failure(path, ids, "CF-118", 1002)
            self.assertEqual(read_events(path, ids)[1]["CF-118"]["failures"], 2)

    def test_reject_truncated_or_unknown_records(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "attempts.jsonl"
            path.write_text('{"task":"CF-118"}\n')
            with self.assertRaises(ValueError):
                read_events(path, {"CF-118"})
            with self.assertRaises(ValueError):
                append_failure(path, {"CF-118"}, "CF-118", 1000)


if __name__ == "__main__":
    unittest.main()
