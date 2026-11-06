"""CF-069: preserve uncertainty across relay interruptions, without HP access."""
import contextlib
import json
import os
import pathlib
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import cf_public_relay as relay


class Queue:
    def __init__(self, job):
        self.job = job
        self.published = []
    def files(self):
        return [self.job["id"] + ".json"]
    def load(self, name):
        return self.job
    def publish(self, jid, receipt):
        self.published.append(receipt)
        return False


class UnknownProgressTests(unittest.TestCase):
    def test_crash_inside_action_is_never_replayed_as_success(self):
        job = relay.make_job("ping")
        child = """
import json, os, pathlib, sys
import cf_public_relay as relay
job=json.loads(sys.argv[1])
class Repo:
    def files(self):return [job['id']+'.json']
    def load(self,name):return job
    def publish(self,*args):raise RuntimeError('must not publish')
def disappear(*_):os._exit(23)
relay.execute=disappear
relay.tick(Repo(),relay.State(pathlib.Path(sys.argv[2])))
"""
        with tempfile.TemporaryDirectory() as folder:
            db = pathlib.Path(folder) / "relay.sqlite3"
            process = subprocess.run(
                [sys.executable, "-c", child, json.dumps(job), str(db)],
                cwd=pathlib.Path(__file__).resolve().parents[1],
                capture_output=True, text=True, timeout=15,
            )
            self.assertEqual(process.returncode, 23, process.stderr)
            state = relay.State(db)
            self.assertIsNone(state.receipt(job["id"]))
            self.assertEqual(state.attempt(job["id"]), (relay.sha(job), "in_progress"))
            self.assertEqual(state.cursor(), job["id"] + ".json")
            queue = Queue(job)
            with patch.object(relay, "execute") as execute:
                result = relay.tick(queue, state)
                execute.assert_not_called()
            self.assertEqual(result["uncertain"], 1)
            self.assertEqual(result["executed"], 0)
            self.assertEqual(result["replayed"], 0)
            self.assertEqual(result["public_receipts"], 0)
            self.assertEqual(result["errors"], [])
            self.assertEqual(queue.published, [])
            self.assertEqual(state.count(), 0)

    def test_normal_action_transitions_to_completed_atomically(self):
        job = relay.make_job("ping")
        with tempfile.TemporaryDirectory() as folder:
            state = relay.State(pathlib.Path(folder) / "state.sqlite3")
            first = relay.tick(Queue(job), state)
            self.assertEqual((first["executed"], first["uncertain"]), (1, 0))
            self.assertEqual(state.attempt(job["id"]), (relay.sha(job), "completed"))
            self.assertEqual(state.receipt(job["id"])[1]["status"], "completed")
            with patch.object(relay, "execute") as execute:
                second = relay.tick(Queue(job), relay.State(state.db))
                execute.assert_not_called()
            self.assertEqual((second["replayed"], second["uncertain"]), (1, 0))

    def test_invalid_job_never_opens_an_attempt(self):
        job = relay.make_job("ping", now=100)
        with tempfile.TemporaryDirectory() as folder:
            state = relay.State(pathlib.Path(folder) / "state.sqlite3")
            report = relay.tick(Queue(job), state)
            self.assertEqual(report["executed"], 0)
            self.assertEqual(report["errors"][0]["error"], "expired_or_future")
            self.assertIsNone(state.attempt(job["id"]))

    def test_action_error_keeps_unknown_not_completed(self):
        job = relay.make_job("ping")
        with tempfile.TemporaryDirectory() as folder:
            state = relay.State(pathlib.Path(folder) / "state.sqlite3")
            queue = Queue(job)
            with patch.object(relay, "execute", side_effect=relay.RelayError("test_interruption")):
                first = relay.tick(queue, state)
            self.assertEqual(first["errors"][0]["error"], "test_interruption")
            self.assertEqual(state.attempt(job["id"])[1], "in_progress")
            self.assertIsNone(state.receipt(job["id"]))
            with patch.object(relay, "execute") as execute:
                second = relay.tick(queue, relay.State(state.db))
                execute.assert_not_called()
            self.assertEqual(second["uncertain"], 1)
            self.assertEqual(queue.published, [])

    def test_altered_request_digest_refused_after_unknown_attempt(self):
        job = relay.make_job("ping")
        with tempfile.TemporaryDirectory() as folder:
            state = relay.State(pathlib.Path(folder) / "relay.sqlite3")
            self.assertTrue(state.begin(job["id"], relay.sha(job)))
            changed = dict(job, expires=job["expires"] + 5)
            with patch.object(relay, "execute") as execute:
                result = relay.tick(Queue(changed), state)
                execute.assert_not_called()
            self.assertEqual(result["errors"][0]["error"], "attempt_conflict")
            self.assertEqual(result["uncertain"], 0)
            self.assertEqual(state.attempt(job["id"])[0], relay.sha(job))

    def test_expired_prior_attempt_stays_uncertain_not_reexecuted(self):
        job = relay.make_job("ping", now=100)
        with tempfile.TemporaryDirectory() as folder:
            state = relay.State(pathlib.Path(folder) / "state.sqlite3")
            self.assertTrue(state.begin(job["id"], relay.sha(job)))
            with patch.object(relay, "execute") as execute:
                result = relay.tick(Queue(job), relay.State(state.db))
                execute.assert_not_called()
            self.assertEqual(result["uncertain"], 1)
            self.assertEqual(result["errors"], [])
            self.assertEqual(state.attempt(job["id"])[1], "in_progress")

    def test_existing_sqlite_receipt_migrates_without_reexecution(self):
        job = relay.make_job("ping")
        receipt = {"v": 1, "id": job["id"], "request_sha256": relay.sha(job),
                   "status": "completed", "result": {"pong": True, "protocol": 1}}
        with tempfile.TemporaryDirectory() as folder:
            db = pathlib.Path(folder) / "relay.sqlite3"
            with contextlib.closing(sqlite3.connect(db)) as con:
                with con:
                    con.execute("CREATE TABLE receipts(id TEXT PRIMARY KEY, digest TEXT NOT NULL, receipt TEXT NOT NULL)")
                    con.execute("INSERT INTO receipts VALUES(?,?,?)",
                                (job["id"], relay.sha(job), relay.dump(receipt).decode()))
            state = relay.State(db)
            self.assertEqual(state.count(), 1)
            self.assertIsNone(state.attempt(job["id"]))
            with patch.object(relay, "execute") as execute:
                result = relay.tick(Queue(job), state)
                execute.assert_not_called()
            self.assertEqual((result["replayed"], result["uncertain"]), (1, 0))


if __name__ == "__main__":
    unittest.main()
