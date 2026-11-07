"""Read-only channel audit evidence tests; no real HP contact or claims."""
import base64
import contextlib
import io
import json
import unittest
from unittest.mock import patch

from relay.cf_public_relay import make_job, sha
from relay import channel_audit
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

    def test_current_receipt_requires_matching_response_digest(self):
        current = {**self.good, "v": 2, "response_sha256": sha(self.good["result"])}
        for receipt, expected in ((current, 1),
                                  ({**current, "response_sha256": "0" * 64}, 0),
                                  ({**self.good, "v": 2}, 0)):
            with self.subTest(receipt=receipt):
                report = summarize({self.name: self.job}, {self.name: receipt}, self.issued)
                self.assertEqual(report["matching_execution_receipts"], expected)
                self.assertEqual(report["mismatched_receipts"], 1 - expected)

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

    def test_ping_requires_successful_result(self):
        for result in ({}, {"pong": False, "protocol": 1}, {"pong": 1, "protocol": 1},
                       {"pong": True, "protocol": 2}, {"pong": True, "protocol": True}):
            with self.subTest(result=result):
                receipt = {**self.good, "result": result}
                report = summarize({self.name: self.job}, {self.name: receipt}, self.issued)
                self.assertEqual(report["mismatched_receipts"], 1)
                self.assertEqual(report["matching_execution_receipts"], 0)

    def test_present_null_receipt_is_mismatched(self):
        report = summarize({self.name: self.job}, {self.name: None}, self.issued)
        self.assertEqual(report["mismatched_receipts"], 1)
        self.assertEqual(report["pending_requests"], 0)
        self.assertEqual(report["orphan_receipts"], 0)

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

    def test_archive_capacity_checks_each_folder_at_the_boundaries(self):
        for size, expected in ((99, "within_limit"), (100, "review_due"),
                               (120, "review_due"), (121, "limit_exceeded")):
            for folder, other in (("inbox", "receipts"), ("receipts", "inbox")):
                with self.subTest(folder=folder, size=size):
                    capacity = channel_audit.archive_capacity({folder: size, other: 1})
                    self.assertEqual(capacity["state"], expected)
                    self.assertEqual(capacity["remaining_before_limit"][folder], max(0, 120 - size))

    def test_live_audit_preflights_both_folders_before_reading_overfull_queue(self):
        inbox_url = channel_audit.folder_url("inbox") + "?ref=main"
        receipts_url = channel_audit.folder_url("receipts") + "?ref=main"
        overfull = [{"type": "file", "name": f"receipt-{number}.json"} for number in range(121)]
        for listings in ((overfull, []), ([], overfull)):
            with self.subTest(inbox_count=len(listings[0])):
                output = io.StringIO()
                with patch.object(channel_audit, "github_json", side_effect=listings) as fetch:
                    with contextlib.redirect_stdout(output):
                        self.assertEqual(channel_audit.main(["--live"]), 1)
                    self.assertEqual([args[0] for args, _ in fetch.call_args_list],
                                     [inbox_url, receipts_url])
                report = json.loads(output.getvalue())
                self.assertEqual(report["audit"], "unavailable")
                self.assertEqual(report["archive_capacity"]["state"], "limit_exceeded")
                self.assertEqual(report["archive_capacity"]["file_counts"],
                                 {"inbox": len(listings[0]), "receipts": len(listings[1])})
                self.assertNotIn("matching_execution_receipts", report)

    def test_live_audit_keeps_matching_receipts_at_the_ceiling(self):
        inbox_url = channel_audit.folder_url("inbox")
        receipts_url = channel_audit.folder_url("receipts")
        entries = [{"type": "file", "name": self.name}, {"type": "file", "name": "README.md"}]
        entries.extend({"type": "file", "name": f"archive-{number}.json"} for number in range(119))

        def fake_github(url):
            if url == inbox_url + "?ref=main":
                return [{"type": "file", "name": self.name}]
            if url == receipts_url + "?ref=main":
                return entries
            if url.startswith(inbox_url + "/"):
                document = self.job
            elif url == receipts_url + "/" + self.name + "?ref=main":
                document = self.good
            else:
                document = {}
            return {"encoding": "base64",
                    "content": base64.b64encode(json.dumps(document).encode()).decode("ascii")}

        output = io.StringIO()
        with patch.object(channel_audit, "github_json", side_effect=fake_github) as fetch:
            with contextlib.redirect_stdout(output):
                self.assertEqual(channel_audit.main(["--live"]), 0)
            self.assertEqual(fetch.call_count, 123)
        report = json.loads(output.getvalue())
        self.assertEqual(report["matching_execution_receipts"], 1)
        self.assertEqual(report["archive_capacity"]["state"], "review_due")
        self.assertEqual(report["archive_capacity"]["file_counts"], {"inbox": 1, "receipts": 120})
        self.assertEqual(report["archive_capacity"]["remaining_before_limit"]["receipts"], 0)


if __name__ == "__main__":
    unittest.main()
