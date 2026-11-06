"""CF-200 recovery tests: source simulation only, never physical HP evidence."""
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("cf_public_relay", ROOT / "cf_public_relay.py")
relay = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = relay
spec.loader.exec_module(relay)

class MemoryRepo:
    def __init__(self, job):
        self.job = job
        self.receipts = {}
        self.publish_attempts = 0
        self.fail_publish = True
    def files(self):
        return [self.job["id"] + ".json"]
    def load(self, name):
        return self.job
    def publish(self, jid, receipt):
        self.publish_attempts += 1
        if self.fail_publish:
            raise relay.RelayError("simulated_network_interruption")
        old = self.receipts.get(jid)
        if old is not None and old != receipt:
            raise relay.RelayError("receipt_conflict")
        self.receipts[jid] = receipt
        return True

class RecoveryTests(unittest.TestCase):
    def test_process_exit_after_local_save_replays_without_execution(self):
        job = relay.make_job("ping")
        child = """
import json
import os
import pathlib
import sys
from test_cf200_recovery import MemoryRepo, relay

repo = MemoryRepo(json.loads(sys.argv[1]))
repo.publish = lambda *_: os._exit(17)
relay.tick(repo, relay.State(pathlib.Path(sys.argv[2])))
"""
        with tempfile.TemporaryDirectory() as folder:
            db = pathlib.Path(folder) / "relay.sqlite3"
            exited = subprocess.run(
                [sys.executable, "-c", child, json.dumps(job), str(db)],
                cwd=ROOT, capture_output=True, text=True, timeout=15,
            )
            self.assertEqual(exited.returncode, 17, exited.stderr)

            restarted = relay.State(db)
            digest, receipt = restarted.receipt(job["id"])
            self.assertEqual(digest, relay.sha(job))
            self.assertEqual(restarted.cursor(), job["id"] + ".json")
            repo = MemoryRepo(job)
            repo.fail_publish = False
            with patch.object(relay, "execute") as execute:
                result = relay.tick(repo, restarted)
                execute.assert_not_called()
            self.assertEqual(result["errors"], [])
            self.assertEqual((result["executed"], result["replayed"], result["public_receipts"]), (0, 1, 1))
            self.assertEqual(repo.receipts, {job["id"]: receipt})
            self.assertEqual(restarted.count(), 1)

    def test_interrupted_receipt_upload_does_not_reexecute(self):
        job = relay.make_job("ping")
        repo = MemoryRepo(job)
        with tempfile.TemporaryDirectory() as folder:
            db = pathlib.Path(folder) / "relay.sqlite3"
            first = relay.tick(repo, relay.State(db))
            self.assertEqual(first["executed"], 1)
            self.assertEqual(first["public_receipts"], 0)
            self.assertEqual(len(first["errors"]), 1)
            repo.fail_publish = False
            second = relay.tick(repo, relay.State(db))
            self.assertEqual(second["executed"], 0)
            self.assertEqual(second["replayed"], 1)
            self.assertEqual(second["public_receipts"], 1)
            self.assertEqual(repo.receipts[job["id"]]["request_sha256"], relay.sha(job))

    def test_restart_retains_receipt_and_cursor(self):
        job = relay.make_job("ping")
        repo = MemoryRepo(job)
        repo.fail_publish = False
        with tempfile.TemporaryDirectory() as folder:
            db = pathlib.Path(folder) / "relay.sqlite3"
            relay.tick(repo, relay.State(db))
            restarted = relay.State(db)
            self.assertEqual(restarted.count(), 1)
            self.assertEqual(restarted.cursor(), job["id"] + ".json")
            again = relay.tick(repo, restarted)
            self.assertEqual(again["executed"], 0)

    def test_conflicting_receipt_does_not_replace_local_result(self):
        job = relay.make_job("ping")
        repo = MemoryRepo(job)
        repo.fail_publish = False
        with tempfile.TemporaryDirectory() as folder:
            state = relay.State(pathlib.Path(folder) / "relay.sqlite3")
            relay.tick(repo, state)
            repo.receipts[job["id"]] = {"status": "untrusted"}
            again = relay.tick(repo, state)
            self.assertEqual(again["executed"], 0)
            self.assertTrue(again["errors"])
            self.assertEqual(state.count(), 1)

    def test_status_receipt_excludes_local_private_details(self):
        job = relay.make_job("hp_status")
        result = relay.execute(job)
        self.assertEqual(set(result), {"worker", "policy", "commands"})
        self.assertEqual(result["policy"], "public-safe")
        self.assertFalse(any(k in str(result).lower() for k in
                             ("username", "hostname", "token", "password", "ip_address")))

if __name__ == "__main__":
    unittest.main()
