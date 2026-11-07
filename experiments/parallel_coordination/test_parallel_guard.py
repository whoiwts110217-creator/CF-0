"""Synthetic, no-network regression tests for coordination preconditions."""
import unittest
from datetime import datetime, timedelta, timezone

from parallel_guard import Claim, ConflictError, require_unique_receipt, validate_proposal


NOW = datetime(2026, 11, 7, 12, tzinfo=timezone.utc)


def claim(task="CF-101", operator="worker-a", sha="abc", paths=("docs/a.md",), delta=60):
    return Claim(task, operator, sha, paths, NOW + timedelta(seconds=delta))


class ParallelGuardTests(unittest.TestCase):
    def test_valid_independent_proposal(self):
        validate_proposal(claim(), current_sha="abc", now=NOW)

    def test_stale_sha_rejected(self):
        with self.assertRaisesRegex(ConflictError, "stale_source"):
            validate_proposal(claim(), current_sha="new-sha", now=NOW)

    def test_same_task_other_worker_rejected(self):
        with self.assertRaisesRegex(ConflictError, "task_claimed"):
            validate_proposal(claim(), current_sha="abc", now=NOW,
                              active_claims=(claim(operator="worker-b", paths=("docs/b.md",)),))

    def test_same_path_other_task_rejected(self):
        with self.assertRaisesRegex(ConflictError, "path_claimed"):
            validate_proposal(claim(), current_sha="abc", now=NOW,
                              active_claims=(claim(task="CF-102", operator="worker-b"),))

    def test_nonoverlapping_claim_allowed(self):
        validate_proposal(claim(), current_sha="abc", now=NOW,
                          active_claims=(claim(task="CF-102", operator="worker-b",
                                               paths=("docs/b.md",)),))

    def test_expired_peer_does_not_lock(self):
        validate_proposal(claim(), current_sha="abc", now=NOW,
                          active_claims=(claim(operator="worker-b", delta=-1),))

    def test_expired_self_rejected(self):
        with self.assertRaisesRegex(ConflictError, "expired_claim"):
            validate_proposal(claim(delta=-1), current_sha="abc", now=NOW)

    def test_verified_task_rejected(self):
        with self.assertRaisesRegex(ConflictError, "already_verified"):
            validate_proposal(claim(), current_sha="abc", now=NOW,
                              verified_task_ids=frozenset({"CF-101"}))

    def test_duplicate_receipt_rejected(self):
        with self.assertRaisesRegex(ConflictError, "action_already_recorded"):
            require_unique_receipt("request-123", {"request-123": "completed"})

    def test_new_receipt_allowed(self):
        require_unique_receipt("request-124", {"request-123": "completed"})

    def test_naive_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            claim(delta=1).__class__("CF-101", "worker-a", "abc",
                                      ("docs/a.md",), datetime(2026, 11, 7))

    def test_unsafe_path_rejected(self):
        with self.assertRaises(ValueError):
            claim(paths=("../secret",))


if __name__ == "__main__":
    unittest.main()
