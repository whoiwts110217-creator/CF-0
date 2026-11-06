"""Offline tests for the privacy-minimized, read-only HP health collector."""
import json
import pathlib
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from cf_hp_health_snapshot import snapshot


class HPHealthSnapshotTests(unittest.TestCase):
    def test_missing_database_is_safe_and_does_not_create_it(self):
        with tempfile.TemporaryDirectory() as home:
            report = snapshot(home)
            self.assertEqual(report["schema"], "cf0.hp_health.v1")
            self.assertFalse(report["db_exists"])
            self.assertIsNone(report["receipt_count"])
            self.assertIsNone(report["error"])
            self.assertFalse((pathlib.Path(home) / ".caveman_focus_relay").exists())

    def test_counts_recent_pings_without_exposing_receipt_data(self):
        with tempfile.TemporaryDirectory() as home:
            folder = pathlib.Path(home) / ".caveman_focus_relay"
            folder.mkdir()
            with sqlite3.connect(folder / "relay.sqlite3") as db:
                db.execute("CREATE TABLE receipts (receipt TEXT)")
                db.execute("INSERT INTO receipts VALUES (?)", (json.dumps({
                    "status": "completed", "result": {"pong": True, "protocol": 1},
                    "private_token": "must-not-appear"}),))
                db.execute("INSERT INTO receipts VALUES (?)", (json.dumps({
                    "status": "failed", "result": {"error": "internal"}}),))
            report = snapshot(home)
            self.assertEqual(report["receipt_count"], 2)
            self.assertEqual(report["ping_receipt_count"], 1)
            self.assertEqual(report["last_receipt_status"], "failed")
            self.assertNotIn("must-not-appear", json.dumps(report))
            self.assertNotIn(str(folder), json.dumps(report))

    def test_snapshot_releases_database_handle(self):
        # A leaked read-only handle prevents rename/cleanup on Windows.
        with tempfile.TemporaryDirectory() as home:
            folder = pathlib.Path(home) / ".caveman_focus_relay"
            folder.mkdir()
            db_path = folder / "relay.sqlite3"
            con = sqlite3.connect(db_path)
            try:
                con.execute("CREATE TABLE receipts (receipt TEXT)")
                con.commit()
            finally:
                con.close()
            report = snapshot(home)
            self.assertIsNone(report["error"])
            renamed = folder / "relay-renamed.sqlite3"
            db_path.rename(renamed)
            self.assertTrue(renamed.exists())

    def test_unreadable_schema_returns_generic_error(self):
        with tempfile.TemporaryDirectory() as home:
            folder = pathlib.Path(home) / ".caveman_focus_relay"
            folder.mkdir()
            with sqlite3.connect(folder / "relay.sqlite3") as db:
                db.execute("CREATE TABLE unrelated (id INTEGER)")
            report = snapshot(home)
            self.assertEqual(report["error"], "state_unavailable")
            self.assertNotIn(str(folder), json.dumps(report))


if __name__ == "__main__":
    unittest.main()
