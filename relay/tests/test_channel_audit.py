"""Read-only channel audit evidence tests; no real HP contact or claims."""
import unittest

from relay.cf_public_relay import make_job, sha
from relay.channel_audit import summarize


class ChannelAuditTests(unittest.TestCase):
    def setUp(self):
        self.issued = 1_790_000_000
        self.job = make_job("ping", now=self.issued)
        self.name = self.job["id"] + ".json"
        self.good = {
            "v": 1,
            "id": self.job["id"],
            "request_sha256": sha(self.job),
            "status": "completed",
            "result": {"pong": True, "protocol": 1},
        }

    def test_matching_request_and_execution_receipt(self):
        report = summarize({self.name: self.job}, {self.name: self.good}, self.issued + 90)
        self.assertEqual(report["matching_execution_receipts"], 1)
        self.assertEqual(report["mismatched_receipts"], 0)
        self.assertNotEqual(report["physical_hp_attestation"], "verified")

    def test_probe_is_not_execution_receipt(self):
        probe = {"v": 1, "id": "probe", "kind": "cf0_hp_writeback_probe",
                 "status": "received", "result": {"public_safe": True}}
        report = summarize({self.name: self.job}, {"probe.json": probe}, self.issued + 90)
        self.assertEqual(report["writeback_setup_probes"], 1)
        self.assertEqual(report["matching_execution_receipts"], 0)
        self.assertEqual(report["pending_requests"], 1)

    def test_wrong_request_hash_is_not_accepted(self):
        wrong = {**self.good, "request_sha256": "0" * 64}
        report = summarize({self.name: self.job}, {self.name: wrong}, self.issued + 90)
        self.assertEqual(report["mismatched_receipts"], 1)
        self.assertEqual(report["matching_execution_receipts"], 0)

    def test_expired_and_orphan(self):
        report = summarize({self.name: self.job}, {"unrelated.json": {"status": "completed"}},
                           self.job["expires"] + 10)
        self.assertEqual(report["expired_without_receipt"], 1)
        self.assertEqual(report["orphan_receipts"], 1)

    def test_invalid_request_does_not_count_as_match(self):
        invalid = {**self.job, "action": "shell"}
        report = summarize({self.name: invalid}, {self.name: self.good}, self.issued + 90)
        self.assertEqual(report["invalid_requests"], 1)
        self.assertEqual(report["matching_execution_receipts"], 0)


if __name__ == "__main__":
    unittest.main()
