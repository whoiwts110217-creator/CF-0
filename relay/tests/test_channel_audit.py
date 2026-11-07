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

    def test_malformed_base64_contents_fail_closed_without_a_traceback(self):
        """CF-075: reject corrupt GitHub content and do not report a match."""
        invalid = (
            {"encoding": "base64", "content": "%%%"},
            {"encoding": "base64", "content": "a"},
            {"encoding": "base64", "content": "////="},
            {"encoding": "base64", "content": 7},
            {"encoding": "utf-8", "content": "e30="},
        )
        for document in invalid:
            with self.subTest(document=document):
                with patch.object(channel_audit, "github_json", return_value=document):
                    with self.assertRaises(ValueError):
                        channel_audit.read_contents_json("https://api.github.com/unused")

    def test_live_audit_reports_malformed_base64_as_unavailable(self):
        """CF-075: a broken receipt cannot be counted as HP execution."""
        inbox_url = channel_audit.folder_url("inbox")
        receipt_url = channel_audit.folder_url("receipts")
        encoded_job = base64.b64encode(json.dumps(self.job).encode()).decode()
        responses = {
            inbox_url + "?ref=main": [{"type": "file", "name": self.name}],
            receipt_url + "?ref=main": [{"type": "file", "name": self.name}],
            inbox_url + "/" + self.name + "?ref=main":
                {"encoding": "base64", "content": encoded_job},
            receipt_url + "/" + self.name + "?ref=main":
                {"encoding": "base64", "content": "%%%"},
        }
        output = io.StringIO()
        with patch.object(channel_audit, "github_json", side_effect=responses.__getitem__):
            with contextlib.redirect_stdout(output):
                self.assertEqual(channel_audit.main(["--live"]), 1)
        report = json.loads(output.getvalue())
        self.assertEqual(report["audit"], "unavailable")
        self.assertEqual(report["error_type"], "ValueError")
        self.assertNotIn("matching_execution_receipts", report)

    def test_duplicate_receipt_ids_fail_closed_at_listing_and_read(self):
        """CF-076: duplicate public IDs must never be silently overwritten."""
        for folder in ("inbox", "receipts"):
            with self.subTest(folder=folder):
                url = channel_audit.folder_url(folder) + "?ref=main"
                duplicate = [{"type": "file", "name": self.name},
                             {"type": "file", "name": self.name}]
                with patch.object(channel_audit, "github_json", return_value=duplicate):
                    with self.assertRaisesRegex(ValueError, "duplicate_receipt_or_request_id"):
                        channel_audit.list_json_names(folder)
                with patch.object(channel_audit, "read_contents_json") as read:
                    with self.assertRaisesRegex(ValueError, "duplicate_receipt_or_request_id"):
                        channel_audit.read_folder(folder, names=[self.name, self.name])
                    read.assert_not_called()

    def test_live_audit_duplicate_receipt_id_is_unavailable(self):
        """CF-076: no matched count may escape an ambiguous GitHub listing."""
        inbox_url = channel_audit.folder_url("inbox") + "?ref=main"
        receipts_url = channel_audit.folder_url("receipts") + "?ref=main"
        listing = [{"type": "file", "name": self.name}]
        duplicates = listing * 2
        output = io.StringIO()
        with patch.object(channel_audit, "github_json",
                          side_effect={inbox_url: listing,
                                       receipts_url: duplicates}.__getitem__):
            with contextlib.redirect_stdout(output):
                self.assertEqual(channel_audit.main(["--live"]), 1)
        report = json.loads(output.getvalue())
        self.assertEqual(report["audit"], "unavailable")
        self.assertEqual(report["error_type"], "ValueError")
        self.assertNotIn("matching_execution_receipts", report)

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

    def test_pruning_review_only_selects_old_matched_ping_pairs(self):
        now = self.job["expires"] + channel_audit.PRUNING_GRACE_SECONDS
        cutoff = now - channel_audit.PRUNING_GRACE_SECONDS
        inbox, receipts = {self.name: self.job}, {self.name: self.good}

        def add_pair(action="ping", issued=self.issued, **receipt_changes):
            job = make_job(action, now=issued)
            name = job["id"] + ".json"
            inbox[name] = job
            receipts[name] = {**self.good, "id": job["id"], "request_sha256": sha(job),
                              **receipt_changes}
            return job

        current = add_pair(v=2, response_sha256=sha(self.good["result"]))
        protected = add_pair()
        add_pair(issued=self.issued + 1)  # expires one second after the cutoff
        add_pair(issued=now)  # pending even if a receipt file is present
        add_pair("hp_status")
        add_pair(request_sha256="0" * 64)
        add_pair(v=2, response_sha256="0" * 64)
        add_pair(result={"pong": False, "protocol": 1})
        add_pair(kind="cf0_hp_writeback_probe", status="received")
        unmatched = add_pair()
        receipts.pop(unmatched["id"] + ".json")
        orphan = add_pair()
        inbox.pop(orphan["id"] + ".json")
        self.assertEqual(self.job["expires"], cutoff)

        kwargs = {"source_commit": "a" * 40, "protected_ping_id": protected["id"], "now": now}
        review = channel_audit.pruning_review(inbox, receipts, **kwargs)
        manifest = review["manifest"]
        pairs = manifest["pairs_for_review"]
        self.assertEqual([pair["request_id"] for pair in pairs], sorted([self.job["id"], current["id"]]))
        for pair in pairs:
            name = pair["request_id"] + ".json"
            self.assertEqual(pair["inbox_path"], "command_queue/inbox/" + name)
            self.assertEqual(pair["receipt_path"], "command_queue/receipts/" + name)
            self.assertEqual(pair["request_sha256"], sha(inbox[name]))
            self.assertEqual(pair["receipt_sha256"], sha(receipts[name]))
        self.assertEqual(review["manifest_sha256"], sha(manifest))
        later = channel_audit.pruning_review(inbox, receipts, **{**kwargs, "now": now + 2})
        self.assertNotEqual(review["manifest_sha256"], later["manifest_sha256"])
        moved = channel_audit.pruning_review(inbox, receipts, **{**kwargs, "source_commit": "b" * 40})
        self.assertNotEqual(review["manifest_sha256"], moved["manifest_sha256"])

    def test_pruning_review_pins_reads_and_requires_a_protected_ping(self):
        repo_url = f"{channel_audit.API}/repos/{channel_audit.REPO}"
        ref_url = repo_url + "/git/ref/heads/main"
        commit = "c" * 40
        suffix = "?ref=" + commit
        inbox_url = channel_audit.folder_url("inbox")
        receipts_url = channel_audit.folder_url("receipts")
        state_url = repo_url + "/contents/docs/PUBLIC_CONTINUITY_STATE.json" + suffix
        protected = make_job("ping", now=self.issued)["id"]
        state = {"schema": "cf0.public_continuity.v1", "hp": {"public_ping_request_id": protected}}

        def encoded(value):
            return {"encoding": "base64", "content": base64.b64encode(json.dumps(value).encode()).decode()}

        responses = {
            ref_url: {"ref": "refs/heads/main", "object": {"type": "commit", "sha": commit}},
            inbox_url + suffix: [{"type": "file", "name": self.name}],
            receipts_url + suffix: [{"type": "file", "name": self.name}],
            state_url: encoded(state),
            inbox_url + "/" + self.name + suffix: encoded(self.job),
            receipts_url + "/" + self.name + suffix: encoded(self.good),
        }
        for valid in (True, False):
            with self.subTest(valid=valid):
                if not valid:
                    responses[state_url] = encoded({**state, "hp": {}})
                output = io.StringIO()
                with patch.object(channel_audit, "github_json", side_effect=responses.__getitem__) as fetch:
                    with patch.object(channel_audit.time, "time",
                                      return_value=self.job["expires"] + channel_audit.PRUNING_GRACE_SECONDS):
                        with contextlib.redirect_stdout(output):
                            self.assertEqual(channel_audit.main(["--review-pruning"]), 0 if valid else 1)
                    self.assertEqual([args[0] for args, _ in fetch.call_args_list],
                                     list(responses) if valid else list(responses)[:4])
                report = json.loads(output.getvalue())
                if valid:
                    manifest = report["pruning_review"]["manifest"]
                    self.assertEqual(manifest["source_commit"], commit)
                    self.assertEqual(manifest["protected_ping_id"], protected)
                    self.assertEqual([p["request_id"] for p in manifest["pairs_for_review"]], [self.job["id"]])
                else:
                    self.assertEqual(report["audit"], "unavailable")
                    self.assertNotIn("pruning_review", report)


if __name__ == "__main__":
    unittest.main()
