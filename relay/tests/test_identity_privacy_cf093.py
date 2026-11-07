"""CF-093: No host/user identity in public-facing CF-0 relay surfaces.

Synthetic identity sentinels only. Does not inspect actual Windows users,
private archives, network accounts, credentials, or physical HP state.
"""
import contextlib
import io
import json
import os
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import cf_public_relay as relay
from cf_hp_health_snapshot import snapshot
from cf_hp_health_publish import sanitized

USER = "CF0SyntheticPrivateWindowsAccount742"
HOST = "CF0SyntheticPrivateComputerOnly742"
HOME = f"C:/Users/{USER}/Documents/Private"
IDENTIFIERS = (USER, HOST, HOME)


def no_private_identity(testcase, value):
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False)
    for marker in IDENTIFIERS:
        testcase.assertNotIn(marker, encoded)


class FakeInbox:
    def __init__(self, job):
        self.job = job
        self.receipts = []

    def files(self):
        return [self.job["id"] + ".json"]

    def load(self, name):
        assert name == self.job["id"] + ".json"
        return self.job

    def publish(self, jid, receipt):
        self.receipts.append(receipt)
        return True


class PublicIdentityPrivacyTests(unittest.TestCase):
    def test_generated_results_ignore_host_environment_identity(self):
        variables = {
            "USERNAME": USER,
            "USER": USER,
            "COMPUTERNAME": HOST,
            "HOSTNAME": HOST,
            "USERPROFILE": HOME,
        }
        with patch.dict(os.environ, variables):
            for action in sorted(relay.ALLOWED):
                with self.subTest(action=action):
                    result = relay.execute(relay.make_job(action))
                    relay.validate_public_result(result, action)
                    no_private_identity(self, result)

    def test_successful_public_receipt_and_console_status_exclude_identity(self):
        with tempfile.TemporaryDirectory(prefix=USER) as folder:
            db = pathlib.Path(folder) / "relay.sqlite3"
            job = relay.make_job("hp_status")
            inbox = FakeInbox(job)
            outcome = relay.tick(inbox, relay.State(db))
            self.assertEqual(outcome["errors"], [])
            self.assertEqual(outcome["executed"], 1)
            self.assertEqual(outcome["public_receipts"], 1)
            no_private_identity(self, outcome)
            self.assertEqual(len(inbox.receipts), 1)
            no_private_identity(self, inbox.receipts[0])
            saved = relay.State(db).receipt(job["id"])
            no_private_identity(self, saved[1])
            with patch.dict(os.environ, {"USERNAME": USER, "COMPUTERNAME": HOST}):
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    self.assertEqual(relay.main(["status", "--state-dir", folder]), 0)
                no_private_identity(self, json.loads(stdout.getvalue()))

    def test_health_aggregation_suppresses_untrusted_receipt_identity(self):
        with tempfile.TemporaryDirectory(prefix=USER) as folder:
            home = pathlib.Path(folder)
            dbpath = home / ".caveman_focus_relay" / "relay.sqlite3"
            dbpath.parent.mkdir()
            with contextlib.closing(sqlite3.connect(dbpath)) as conn:
                conn.execute("CREATE TABLE receipts (receipt TEXT)")
                conn.execute("INSERT INTO receipts VALUES (?)", (json.dumps({
                    "status": "completed",
                    "result": {"pong": True, "protocol": 1},
                    "username": USER,
                    "hostname": HOST,
                    "private_path": HOME
                }),))
                conn.commit()
            report = snapshot(home)
            self.assertEqual(report["receipt_count"], 1)
            self.assertEqual(report["ping_receipt_count"], 1)
            no_private_identity(self, report)
            payload = sanitized(report).decode("utf-8")
            for secret in IDENTIFIERS:
                self.assertNotIn(secret, payload)

    def test_identity_injection_rejected_before_public_github_upload(self):
        job = relay.make_job("ping")
        result = {"pong": True, "protocol": 1, "computer_name": HOST}
        receipt = {
            "v": 2, "id": job["id"], "request_sha256": relay.sha(job),
            "status": "completed", "result": result,
            "response_sha256": relay.sha(result),
        }
        repo = relay.HttpRepo(token="dummy-synthetic-token")
        with patch.object(repo, "request") as request:
            with self.assertRaisesRegex(relay.RelayError, "^unsafe_public_result$"):
                repo.publish(job["id"], receipt)
            request.assert_not_called()
        report = snapshot(tempfile.gettempdir())
        report["username"] = USER
        with self.assertRaisesRegex(ValueError, "invalid_health_schema"):
            sanitized(report)


if __name__ == "__main__":
    unittest.main()
