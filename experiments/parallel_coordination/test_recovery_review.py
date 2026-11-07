"""Synthetic, no-network claim recovery tests; never execute retries."""
from datetime import datetime, timedelta, timezone
import unittest
from recovery_review import review_interrupted_claim

NOW = datetime(2026, 11, 7, 20, 0, tzinfo=timezone.utc)


def check(**changes):
    options = dict(expected_claim_sha="abc123", observed_claim_sha="abc123",
                   expires_at=NOW - timedelta(seconds=1), now=NOW,
                   write_status="NO_APPLIED_WRITES", registry_status="planned",
                   receipts_accounted_for=True)
    options.update(changes)
    return review_interrupted_claim(**options)


class RecoveryReviewTests(unittest.TestCase):
    def test_expiry_requires_review(self):
        r = check()
        self.assertEqual(r.disposition, "REVIEW_REQUIRED")
        self.assertIn("expiry_does_not_transfer_authority", r.blockers)
        self.assertFalse(r.automatic_release_allowed)
        self.assertFalse(r.automatic_retry_allowed)

    def test_active_claim_cannot_release(self):
        r = check(expires_at=NOW + timedelta(seconds=120))
        self.assertIn("claim_not_expired", r.blockers)
        self.assertFalse(r.automatic_release_allowed)

    def test_missing_claim_is_conflict(self):
        self.assertEqual(check(observed_claim_sha=None).disposition, "HOLD_CONFLICT")

    def test_claim_version_changed(self):
        r = check(observed_claim_sha="different")
        self.assertEqual(r.disposition, "HOLD_CONFLICT")
        self.assertIn("claim_changed_since_snapshot", r.blockers)

    def test_partial_write_halts(self):
        self.assertEqual(check(write_status="PARTIAL").disposition, "HOLD_CONFLICT")

    def test_unknown_write_halts(self):
        self.assertEqual(check(write_status="UNKNOWN").disposition, "HOLD_CONFLICT")

    def test_conflicting_write_halts(self):
        self.assertEqual(check(write_status="CONFLICT").disposition, "HOLD_CONFLICT")

    def test_complete_files_are_not_task_verification(self):
        r = check(write_status="COMPLETE")
        self.assertFalse(r.task_verified)
        self.assertIn("completed_files_require_independent_acceptance", r.blockers)

    def test_existing_verified_task_must_not_repeat(self):
        r = check(registry_status="verified")
        self.assertIn("task_already_verified_do_not_repeat", r.blockers)
        self.assertFalse(r.automatic_retry_allowed)

    def test_unknown_registry_stops(self):
        self.assertEqual(check(registry_status="unknown").disposition, "HOLD_EVIDENCE")

    def test_unknown_receipts_stops(self):
        self.assertEqual(check(receipts_accounted_for=False).disposition, "HOLD_EVIDENCE")

    def test_missing_hp_schedule_evidence_stops(self):
        r = check(hp_required=True, hp_schedule_proven=False)
        self.assertEqual(r.disposition, "HOLD_EVIDENCE")
        self.assertIn("physical_hp_evidence_missing", r.blockers)

    def test_schedule_evidence_does_not_authorize_release(self):
        r = check(hp_required=True, hp_schedule_proven=True)
        self.assertFalse(r.automatic_release_allowed)

    def test_reject_naive_times(self):
        with self.assertRaises(ValueError):
            check(now=datetime(2026, 11, 7))
        with self.assertRaises(ValueError):
            check(expires_at=datetime(2026, 11, 7))

    def test_reject_invalid_status(self):
        with self.assertRaises(ValueError):
            check(write_status="PASS")
        with self.assertRaises(ValueError):
            check(registry_status="done")

    def test_reject_missing_sha(self):
        with self.assertRaises(ValueError):
            check(expected_claim_sha="")


if __name__ == "__main__":
    unittest.main()
