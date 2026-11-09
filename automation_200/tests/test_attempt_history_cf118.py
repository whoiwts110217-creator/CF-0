"""CF-118: existing journal -> bounded source-only proposal integration tests."""
import tempfile
import unittest
from pathlib import Path

from automation_200.attempt_history_cf118 import propose_from_retry_journal
from automation_200.retry_evidence import append_failure


def registry():
    tasks = [{"id": f"CF-{n:03d}", "stream": "priority_logic", "title": str(n),
              "priority": 2, "depends_on": [], "status": "verified",
              "authority": "owner-reviewed", "physical_hp_required": False}
             for n in range(1, 201)]
    tasks[117]["status"] = "planned"
    return {"tasks": tasks, "completed": 199, "target": 200}


class RetryJournalProposalTests(unittest.TestCase):
    def test_real_journal_cooldown_ceiling_and_no_execution(self):
        sample = registry()
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "attempts.jsonl"
            append_failure(path, {"CF-118"}, "CF-118", 1000)
            early = propose_from_retry_journal(sample, path, now=1001)
            self.assertEqual(early["held_counts"]["retry_cooldown"], 1)
            self.assertFalse(early["execution_authorized"])
            self.assertFalse(early["retry_journal_authenticated"])
            self.assertEqual(early["retry_journal_event_count"], 1)
            ready = propose_from_retry_journal(sample, path, now=1300)
            self.assertEqual(ready["selected"][0]["id"], "CF-118")
            append_failure(path, {"CF-118"}, "CF-118", 1400)
            append_failure(path, {"CF-118"}, "CF-118", 1600)
            exhausted = propose_from_retry_journal(sample, path, now=10000)
            self.assertEqual(exhausted["held_counts"]["retry_limit_reached"], 1)
            self.assertEqual(exhausted["selected"], [])
            self.assertEqual(exhausted["retry_journal_event_count"], 3)
            self.assertTrue(exhausted["retry_journal_last_digest"])
            self.assertFalse(exhausted["retry_journal_was_modified"])
            self.assertEqual(path.read_text().count(chr(10)), 3)

    def test_tampering_unknown_task_and_future_failure_fail_closed(self):
        sample = registry()
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "attempts.jsonl"
            append_failure(path, {"CF-118"}, "CF-118", 1000)
            original = path.read_bytes()
            with self.assertRaisesRegex(ValueError, "future"):
                propose_from_retry_journal(sample, path, now=999)
            path.write_bytes(original.replace(b'"failed_at":1000', b'"failed_at":9000'))
            with self.assertRaises(ValueError):
                propose_from_retry_journal(sample, path, now=10000)
            path.write_bytes(original)
            sample["tasks"][117]["id"] = "CF-999"
            with self.assertRaises(ValueError):
                propose_from_retry_journal(sample, path, now=1300)
            self.assertEqual(path.read_bytes(), original)

    def test_missing_journal_never_invents_attempts_or_permissions(self):
        sample = registry()
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "missing.jsonl"
            result = propose_from_retry_journal(sample, path, now=10, health_state="fresh_public_report")
            self.assertEqual(result["selected"][0]["id"], "CF-118")
            self.assertEqual(result["retry_journal_event_count"], 0)
            self.assertFalse(result["execution_authorized"])
            self.assertFalse(path.exists())
            with self.assertRaisesRegex(ValueError, "attempts"):
                propose_from_retry_journal(sample, path, now=10, attempts={})


if __name__ == "__main__":
    unittest.main()
