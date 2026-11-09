"""Regression fixture based on an existing PUBLIC CF-0 legacy ping pair.

Source (main at 2026-11-07):
command_queue/inbox/1bd3a644-9b80-4d05-8cb1-7043c7853d54.json
command_queue/receipts/1bd3a644-9b80-4d05-8cb1-7043c7853d54.json
This is a public-safe fixture, not a live read or HP-origin attestation.
"""
import unittest

from actual_relay_pair import inspect_actual_relay_pair
from evidence_packet import BlobEvidence, git_blob_sha
import cf_public_relay as relay


ID = "1bd3a644-9b80-4d05-8cb1-7043c7853d54"
EXPECTED_REQUEST_DIGEST = "bdd1b0e1c0b45e1b1618c16e814fc9a606e6530bf2419978ee9c510055f8ce16"
REQUEST = {"action": "ping", "args": {}, "expires": 1793935125,
           "id": ID, "issued": 1793927925, "v": 1}
RECEIPT = {"id": ID, "request_sha256": EXPECTED_REQUEST_DIGEST,
           "result": {"pong": True, "protocol": 1}, "status": "completed", "v": 1}


def evidence(path, obj):
    raw = relay.dump(obj)
    return BlobEvidence(path=path, blob_sha=git_blob_sha(raw), content=raw)


class PublicLegacyFixtureTests(unittest.TestCase):
    def test_canonical_request_digest_matches_published_receipt(self):
        self.assertEqual(relay.sha(REQUEST), EXPECTED_REQUEST_DIGEST)

    def test_real_public_v1_pair_requires_review_not_hp_claim(self):
        result = inspect_actual_relay_pair(
            job_id=ID,
            request=evidence(f"command_queue/inbox/{ID}.json", REQUEST),
            receipt=evidence(f"command_queue/receipts/{ID}.json", RECEIPT),
        )
        self.assertEqual(result.status, "LEGACY_REVIEW_REQUIRED")
        self.assertEqual(result.request_digest, EXPECTED_REQUEST_DIGEST)
        self.assertFalse(result.physical_hp_proven)
        self.assertFalse(result.unattended_schedule_proven)
        self.assertFalse(result.automatic_retry_allowed)
        self.assertFalse(result.task_verified)

    def test_published_v1_pair_with_changed_request_is_rejected(self):
        altered = {**REQUEST, "expires": REQUEST["expires"] - 1}
        result = inspect_actual_relay_pair(
            job_id=ID,
            request=evidence(f"command_queue/inbox/{ID}.json", altered),
            receipt=evidence(f"command_queue/receipts/{ID}.json", RECEIPT),
        )
        self.assertEqual(result.status, "HOLD_EVIDENCE")


if __name__ == "__main__":
    unittest.main()
