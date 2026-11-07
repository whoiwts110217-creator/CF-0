"""Offline receipt interpretation tests; no network or Windows GUI required."""
import unittest
import hashlib
import json
from relay.cf200_live_status import PROBE_ID, PROBE_DIGEST, probe_summary
from relay.cf_public_relay import sha


class ReceiptSummaryTests(unittest.TestCase):
    def test_probe_digest_matches_canonical_inbox(self):
        request = {"v": 1, "id": PROBE_ID, "action": "ping", "issued": 1793978096, "expires": 1793985296, "args": {}}
        canonical = json.dumps(request, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        self.assertEqual(hashlib.sha256(canonical).hexdigest(), PROBE_DIGEST)

    def setUp(self):
        self.receipt = {
            "v": 1, "id": PROBE_ID, "request_sha256": PROBE_DIGEST,
            "status": "completed", "result": {"pong": True, "protocol": 1},
        }

    def test_matching_receipt_does_not_claim_scheduler(self):
        message = probe_summary(lambda _: dict(self.receipt))
        self.assertIn("matching completed ping", message)
        self.assertIn("UNVERIFIED", message)

    def test_wrong_digest_is_not_accepted(self):
        receipt = dict(self.receipt, request_sha256="bad")
        self.assertIn("mismatched", probe_summary(lambda _: receipt))

    def test_wrong_result_is_not_accepted(self):
        receipt = dict(self.receipt, result={"pong": False, "protocol": 1})
        self.assertIn("mismatched", probe_summary(lambda _: receipt))

    def test_current_receipt_checks_response_digest(self):
        receipt = dict(self.receipt, v=2, response_sha256=sha(self.receipt["result"]))
        self.assertIn("matching completed ping", probe_summary(lambda _: receipt))
        receipt["response_sha256"] = "0" * 64
        self.assertIn("mismatched", probe_summary(lambda _: receipt))

    def test_network_error_is_not_a_negative_receipt(self):
        def fail(_):
            raise OSError("offline")
        self.assertIn("unavailable", probe_summary(fail))


if __name__ == "__main__":
    unittest.main()
