"""Synthetic integrity-only packet inspection; no network or HP side effects."""
import json
from datetime import datetime, timedelta, timezone
import unittest
from evidence_packet import BlobEvidence, git_blob_sha, inspect_packet

CLAIM_PATH = "experiments/parallel_coordination/claims/CF-097.json"
RECEIPT_PATH = "experiments/parallel_coordination/synthetic_receipts/action-1.json"
REQUEST = "b" * 64
BASE = "a" * 40
NOW = datetime(2026, 11, 7, 20, 0, tzinfo=timezone.utc)


def artifact(path, payload):
    data = json.dumps(payload, sort_keys=True).encode("utf-8")
    return BlobEvidence(path, git_blob_sha(data), data)


def claim():
    return artifact(CLAIM_PATH, {
        "schema": "cf0.parallel_claim_experiment.v1", "status": "pending_unverified",
        "task_id": "CF-097", "operator_id": "worker-a", "base_blob_sha": BASE,
        "release_policy": "no_automatic_reclaim_or_remote_execution",
        "paths": ["docs/a.md"], "created_at": (NOW - timedelta(minutes=1)).isoformat(),
        "expires_at": (NOW + timedelta(minutes=9)).isoformat()})


def receipt(**changes):
    payload = dict(action_id="action-1", request_sha256=REQUEST, result_status="completed")
    payload.update(changes)
    return artifact(RECEIPT_PATH, payload)


def check(**changes):
    values = dict(claim=claim(), expected_claim_path=CLAIM_PATH, expected_task="CF-097",
                  expected_operator="worker-a", expected_base_sha=BASE,
                  expected_paths=("docs/a.md",), now=NOW,
                  receipts=(receipt(),), expected_receipts={"action-1": (RECEIPT_PATH, REQUEST)})
    values.update(changes)
    return inspect_packet(**values)


class EvidencePacketTests(unittest.TestCase):
    def test_matching_packet_is_integrity_only(self):
        result = check()
        self.assertEqual(result.status, "INTEGRITY_CHECKED_ONLY")
        self.assertTrue(result.receipts_accounted_for)
        self.assertEqual(result.matched_receipt_ids, ("action-1",))
        self.assertFalse(result.automatic_retry_allowed)
        self.assertFalse(result.automatic_release_allowed)
        self.assertFalse(result.task_verified)

    def test_missing_claim_holds(self):
        self.assertIn("missing_claim_readback", check(claim=None).reasons)

    def test_tampered_claim_detected(self):
        c=claim()
        corrupted=BlobEvidence(c.path, c.blob_sha, c.content + b" ")
        self.assertIn("claim_blob_integrity_mismatch", check(claim=corrupted).reasons)

    def test_untrusted_sha_format_rejected(self):
        c=claim()
        corrupted=BlobEvidence(c.path, "wrong", c.content)
        self.assertIn("claim_invalid_blob_sha", check(claim=corrupted).reasons)

    def test_mismatched_claim_operator_holds(self):
        self.assertIn("claim_identity_or_policy_mismatch", check(expected_operator="worker-b").reasons)

    def test_mismatched_claim_task_path_rejected(self):
        with self.assertRaises(ValueError):
            check(expected_claim_path="experiments/parallel_coordination/claims/CF-098.json")

    def test_claim_scope_mismatch_holds(self):
        self.assertIn("claim_identity_or_policy_mismatch", check(expected_paths=("docs/b.md",)).reasons)

    def test_claim_expired_holds(self):
        self.assertIn("claim_time_window_invalid_or_expired", check(now=NOW + timedelta(hours=2)).reasons)

    def test_naive_now_rejected(self):
        with self.assertRaises(ValueError):
            check(now=datetime(2026, 11, 7))

    def test_tampered_receipt_detected(self):
        r=receipt()
        corrupted=BlobEvidence(r.path, r.blob_sha, r.content + b" ")
        result = check(receipts=(corrupted,))
        self.assertIn("receipt_blob_integrity_mismatch", result.reasons)
        self.assertFalse(result.receipts_accounted_for)

    def test_request_mismatch_holds(self):
        self.assertIn("receipt_request_mismatch", check(receipts=(receipt(request_sha256="c" * 64),)).reasons)

    def test_uncertain_action_holds(self):
        self.assertIn("receipt_not_completed", check(receipts=(receipt(result_status="uncertain"),)).reasons)

    def test_missing_receipt_holds(self):
        self.assertIn("missing_verified_receipt:action-1", check(receipts=()).reasons)

    def test_duplicate_receipt_path_holds(self):
        self.assertIn("duplicate_receipt_path", check(receipts=(receipt(), receipt())).reasons)

    def test_unexpected_receipt_path_holds(self):
        new=artifact("experiments/parallel_coordination/other.json", {"action_id": "action-1"})
        self.assertIn("unexpected_receipt_path", check(receipts=(new,)).reasons)

    def test_duplicate_expected_path_holds(self):
        values={"action-1": (RECEIPT_PATH, REQUEST), "action-2": (RECEIPT_PATH, REQUEST)}
        self.assertIn("duplicate_expected_receipt_path", check(expected_receipts=values).reasons)

    def test_invalid_json_holds(self):
        broken=BlobEvidence(RECEIPT_PATH, git_blob_sha(b"bad"), b"bad")
        self.assertIn("receipt_invalid_json", check(receipts=(broken,)).reasons)

    def test_git_sha_byte_exact(self):
        self.assertNotEqual(git_blob_sha(b"abc"), git_blob_sha(b"abc\n"))

    def test_blob_type_rejected(self):
        with self.assertRaises(TypeError):
            git_blob_sha("string, not bytes")

    def test_no_expected_actions_is_not_execution_authority(self):
        result=check(receipts=(), expected_receipts={})
        self.assertEqual(result.status, "INTEGRITY_CHECKED_ONLY")
        self.assertFalse(result.automatic_retry_allowed)
        self.assertFalse(result.task_verified)


if __name__ == "__main__":
    unittest.main()
