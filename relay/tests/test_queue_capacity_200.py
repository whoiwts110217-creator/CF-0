"""CF-070: offline 200-command capacity and restart safety; no HP/network calls."""
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import cf_public_relay as relay


class FakeInbox:
    def __init__(self, jobs):
        self.jobs = {job["id"] + ".json": job for job in jobs}
        self.receipts = {}
        self.publish_calls = 0

    def files(self):
        return sorted(self.jobs)

    def load(self, name):
        return self.jobs[name]

    def publish(self, jid, receipt):
        self.publish_calls += 1
        old = self.receipts.get(jid)
        if old is not None:
            if old != receipt:
                raise AssertionError("receipt changed during replay")
            return False
        self.receipts[jid] = receipt
        return True


class QueueCapacityTests(unittest.TestCase):
    def test_two_hundred_requests_across_fresh_worker_instances(self):
        jobs = [relay.make_job("ping") for _ in range(200)]
        inbox = FakeInbox(jobs)
        with tempfile.TemporaryDirectory() as folder:
            db = pathlib.Path(folder) / "relay.sqlite3"
            executed = 0
            # 200 requests / 4 actions per tick = 50 ticks. Recreate State
            # each time to simulate a fresh scheduled worker process.
            for _ in range(50):
                report = relay.tick(inbox, relay.State(db))
                self.assertEqual(report["executed"], 4)
                self.assertEqual(report["errors"], [])
                self.assertLessEqual(report["scanned"], relay.MAX_SCAN)
                executed += report["executed"]
            self.assertEqual(executed, 200)
            self.assertEqual(relay.State(db).count(), 200)
            self.assertEqual(len(inbox.receipts), 200)
            self.assertEqual(inbox.publish_calls, 200)
            for job in jobs:
                receipt = inbox.receipts[job["id"]]
                self.assertEqual(receipt["request_sha256"], relay.sha(job))
                self.assertEqual(receipt["status"], "completed")
                self.assertEqual(receipt["result"], {"pong": True, "protocol": 1})
            # Replays can scan the full queue but may not reexecute anything.
            for _ in range(4):
                report = relay.tick(inbox, relay.State(db))
                self.assertEqual(report["executed"], 0)
                self.assertEqual(report["errors"], [])
            self.assertEqual(relay.State(db).count(), 200)
            self.assertEqual(len(inbox.receipts), 200)


if __name__ == "__main__":
    unittest.main()
