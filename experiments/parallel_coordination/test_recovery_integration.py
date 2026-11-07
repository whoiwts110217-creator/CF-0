"""Pure cross-module exercise: no GitHub write, HP contact, or registry change."""
import hashlib
import json
import unittest
from datetime import datetime, timedelta, timezone

from parallel_guard import Claim
from claim_envelope import create_only_claim_payload
from evidence_packet import BlobEvidence, git_blob_sha, inspect_packet
from reconcile_writes import WriteIntent, reconcile_writes
from recovery_review import review_interrupted_claim

NOW = datetime(2026, 11, 7, 20, tzinfo=timezone.utc)
SOURCE = "a" * 40
REQUEST_BYTES = b"synthetic action, no real HP transport"
REQUEST_SHA = hashlib.sha256(REQUEST_BYTES).hexdigest()
RECEIPT_PATH = "experiments/parallel_coordination/synthetic_receipts/integration-1.json"


def artifact(path, data):
    data = data.encode("utf-8") if isinstance(data, str) else data
    return BlobEvidence(path, git_blob_sha(data), data)


def scenario(*, receipt_status="completed", tamper_receipt=False, applied=False, hp_required=False):
    claim = Claim("CF-097", "synthetic-worker", SOURCE, ("docs/a.md", "docs/b.md"),
                  NOW + timedelta(minutes=10))
    claim_path, claim_json = create_only_claim_payload(claim, NOW)
    claim_artifact = artifact(claim_path, claim_json)
    receipt_json = json.dumps({"action_id": "integration-1", "request_sha256": REQUEST_SHA,
                               "result_status": receipt_status}, sort_keys=True).encode()
    receipt_artifact = artifact(RECEIPT_PATH, receipt_json)
    if tamper_receipt:
        receipt_artifact = BlobEvidence(RECEIPT_PATH, receipt_artifact.blob_sha,
                                        receipt_artifact.content + b" ")
    packet = inspect_packet(
        claim=claim_artifact, expected_claim_path=claim_path,
        expected_task=claim.task_id, expected_operator=claim.operator_id,
        expected_base_sha=SOURCE, expected_paths=claim.paths, now=NOW,
        receipts=(receipt_artifact,),
        expected_receipts={"integration-1": (RECEIPT_PATH, REQUEST_SHA)},
    )
    observed = {"docs/a.md": "new" if applied else "old", "docs/b.md": "old"}
    writes = reconcile_writes([WriteIntent("docs/a.md", "old", "new"),
                              WriteIntent("docs/b.md", "old", "new")], observed)
    review = review_interrupted_claim(
        expected_claim_sha=claim_artifact.blob_sha,
        observed_claim_sha=claim_artifact.blob_sha,
        expires_at=claim.expires_at, now=NOW,
        write_status=writes.status, registry_status="planned",
        receipts_accounted_for=packet.receipts_accounted_for,
        hp_required=hp_required, hp_schedule_proven=False,
    )
    return packet, writes, review


class RecoveryIntegrationTests(unittest.TestCase):
    def test_matching_packet_still_does_not_grant_release(self):
        packet, writes, review = scenario()
        self.assertEqual(packet.status, "INTEGRITY_CHECKED_ONLY")
        self.assertEqual(writes.status, "NO_APPLIED_WRITES")
        self.assertEqual(review.disposition, "REVIEW_REQUIRED")
        self.assertFalse(review.automatic_release_allowed)
        self.assertFalse(review.automatic_retry_allowed)
        self.assertFalse(review.task_verified)

    def test_tampered_receipt_holds(self):
        packet, writes, review = scenario(tamper_receipt=True)
        self.assertFalse(packet.receipts_accounted_for)
        self.assertEqual(review.disposition, "HOLD_EVIDENCE")
        self.assertIn("unreconciled_or_unknown_side_effects", review.blockers)

    def test_partial_write_halts_even_with_matched_receipt(self):
        packet, writes, review = scenario(applied=True)
        self.assertTrue(packet.receipts_accounted_for)
        self.assertEqual(writes.status, "PARTIAL")
        self.assertEqual(review.disposition, "HOLD_CONFLICT")
        self.assertFalse(review.automatic_retry_allowed)

    def test_hp_schedule_missing_prevents_release(self):
        _, _, review = scenario(hp_required=True)
        self.assertEqual(review.disposition, "HOLD_EVIDENCE")
        self.assertIn("physical_hp_evidence_missing", review.blockers)

    def test_uncertain_receipt_prevents_release(self):
        packet, _, review = scenario(receipt_status="uncertain")
        self.assertFalse(packet.receipts_accounted_for)
        self.assertEqual(review.disposition, "HOLD_EVIDENCE")


if __name__ == "__main__":
    unittest.main()
