"""Offline regression tests for privacy-minimized HP status collector."""
import importlib.util
import json
import pathlib
import sqlite3
import tempfile
import unittest

MODULE = pathlib.Path(__file__).resolve().parents[1] / "relay" / "cf_hp_health_snapshot.py"
spec = importlib.util.spec_from_file_location("cf_hp_health_snapshot", MODULE)
health = importlib.util.module_from_spec(spec)
spec.loader.exec_module(health)

class HealthSnapshotTests(unittest.TestCase):
    def test_missing_database_is_not_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            status = health.snapshot(tmp)
            self.assertFalse(status["db_exists"])
            self.assertIsNone(status["receipt_count"])
            self.assertNotIn(str(tmp), json.dumps(status))

    def test_read_only_counts_and_malformed_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / ".caveman_focus_relay"
            path.mkdir()
            db = path / "relay.sqlite3"
            with sqlite3.connect(db) as con:
                con.execute("CREATE TABLE receipts (receipt TEXT)")
                con.executemany("INSERT INTO receipts VALUES (?)", [
                    (json.dumps({"status": "completed", "result": {"pong": True, "protocol": 1}}),),
                    ("broken json",),
                    (json.dumps({"status": "failed", "result": {}}),),
                ])
            status = health.snapshot(tmp)
            self.assertTrue(status["db_exists"])
            self.assertEqual(status["receipt_count"], 3)
            self.assertEqual(status["ping_receipt_count"], 1)
            self.assertEqual(status["last_receipt_status"], "failed")
            self.assertEqual(status["error"], "malformed_receipt")
            self.assertNotIn(str(db), json.dumps(status))
            with sqlite3.connect(db) as con:
                self.assertEqual(con.execute("SELECT COUNT(*) FROM receipts").fetchone()[0], 3)

    def test_unknown_schema_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / ".caveman_focus_relay"
            path.mkdir()
            with sqlite3.connect(path / "relay.sqlite3") as con:
                con.execute("CREATE TABLE unrelated (x TEXT)")
            status = health.snapshot(tmp)
            self.assertEqual(status["error"], "state_unavailable")
            self.assertIsNone(status["receipt_count"])

if __name__ == "__main__":
    unittest.main()
