"""Offline CF-118 journal tests; no HP or network access."""
import json
import hashlib
import subprocess
import sys
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

    def test_concurrent_processes_preserve_every_failure(self):
        # Separate interpreters exercise the OS lock, not merely a thread lock.
        # Each worker appends twice; interleaving must not lose either update.
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "attempts.jsonl"
            script = (
                "import sys\n"
                "from automation_200.retry_evidence import append_failure\n"
                "for _ in range(2):\n"
                "    append_failure(sys.argv[1], {'CF-118'}, 'CF-118', 1000)\n"
            )
            workers = [
                subprocess.Popen(
                    [sys.executable, "-c", script, str(path)],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                )
                for _ in range(3)
            ]
            for worker in workers:
                stdout, stderr = worker.communicate(timeout=20)
                self.assertEqual(worker.returncode, 0, stderr.decode("utf-8", errors="replace"))
            events, attempts = read_events(path, {"CF-118"})
            self.assertEqual(len(events), 6)
            self.assertEqual(attempts["CF-118"]["failures"], 6)
            self.assertEqual([event["failures"] for event in events], list(range(1, 7)))

    def test_corrupted_snapshot_never_overwritten(self):
        # Fail closed: a malformed existing journal must survive an append attempt.
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "attempts.jsonl"
            allowed = {"CF-118"}
            append_failure(path, allowed, "CF-118", 1000)
            valid = path.read_bytes()
            for corrupted in (valid[:-8], bytes([255, 254, 0]), b'{"task":"CF-118"}' + bytes([10])):
                path.write_bytes(corrupted)
                with self.assertRaises((ValueError, UnicodeError)):
                    append_failure(path, allowed, "CF-118", 1001)
                self.assertEqual(path.read_bytes(), corrupted)
            path.write_bytes(valid)
            append_failure(path, allowed, "CF-118", 1001)
            self.assertEqual(read_events(path, allowed)[1]["CF-118"]["failures"], 2)

    def test_reject_unterminated_or_blank_line_without_mutation(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "attempts.jsonl"
            allowed = {"CF-118"}
            append_failure(path, allowed, "CF-118", 1000)
            valid = path.read_bytes()
            newline = bytes([10])
            for corrupted in (valid.rstrip(newline), valid + newline, newline + valid):
                path.write_bytes(corrupted)
                with self.assertRaises(ValueError):
                    read_events(path, allowed)
                with self.assertRaises(ValueError):
                    append_failure(path, allowed, "CF-118", 1001)
                self.assertEqual(path.read_bytes(), corrupted)
            path.write_bytes(valid)
            append_failure(path, allowed, "CF-118", 1001)
            self.assertEqual(read_events(path, allowed)[1]["CF-118"]["failures"], 2)

    def test_reject_valid_hash_with_missing_first_failure(self):
        # A correctly hashed record cannot invent a prior local failure.
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "attempts.jsonl"
            body = {"task": "CF-118", "failures": 2, "failed_at": 1000,
                    "previous": "0" * 64}
            digest = hashlib.sha256(json.dumps(body, sort_keys=True,
                separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()
            path.write_text(json.dumps(dict(body, digest=digest)) + "\n", encoding="utf-8")
            original = path.read_bytes()
            with self.assertRaises(ValueError):
                read_events(path, {"CF-118"})
            with self.assertRaises(ValueError):
                append_failure(path, {"CF-118"}, "CF-118", 1001)
            self.assertEqual(path.read_bytes(), original)

    def test_duplicate_json_key_rejected_even_with_valid_digest(self):
        # JSON parsers ordinarily keep the final duplicate key, which would
        # let a correctly hashed but ambiguous journal record be accepted.
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "attempts.jsonl"
            allowed = {"CF-118"}
            append_failure(path, allowed, "CF-118", 1000)
            valid = path.read_bytes()
            record = json.loads(valid.decode("ascii"))
            # Duplicate task field with identical value preserves the digest.
            ambiguous = valid.replace(b'"task":"CF-118"', b'"task":"CF-118","task":"CF-118"', 1)
            self.assertNotEqual(ambiguous, valid)
            path.write_bytes(ambiguous)
            with self.assertRaisesRegex(ValueError, "duplicate"):
                read_events(path, allowed)
            with self.assertRaisesRegex(ValueError, "duplicate"):
                append_failure(path, allowed, "CF-118", 1001)
            self.assertEqual(path.read_bytes(), ambiguous)
            path.write_bytes(valid)
            append_failure(path, allowed, "CF-118", 1001)
            self.assertEqual(read_events(path, allowed)[1]["CF-118"]["failures"], 2)

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
