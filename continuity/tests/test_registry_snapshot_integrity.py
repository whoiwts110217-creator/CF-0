"""Offline integrity regressions for private CF-200 registry snapshots.

Synthetic fixtures only; never reads private backups or modifies public registry.
"""
import json
from pathlib import Path
import tempfile
import unittest

from continuity import local_index, workorder_bridge


class RegistrySnapshotIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.state = self.root / "private"
        self.source = self.root / "registry.json"
        self.db = local_index.open_db(self.state)
        self.addCleanup(self.db.close)

    def write(self, *, completed=0, status="planned", evidence=""):
        self.source.write_text(json.dumps({
            "target": 1, "completed": completed,
            "tasks": [{"id": "CF-001", "stream": "receipt",
                       "title": "Synthetic task", "status": status,
                       "evidence": evidence}]
        }), encoding="utf-8")

    def test_rejects_false_completed_count_before_source_ingest(self):
        self.write(completed=1)
        with self.assertRaisesRegex(ValueError, "completed_count_mismatch"):
            workorder_bridge.import_registry(self.db, self.state, self.source)
        self.assertEqual(self.db.execute(
            "SELECT COUNT(*) FROM sources").fetchone()[0], 0)

    def test_rejects_verified_without_evidence_before_source_ingest(self):
        self.write(completed=1, status="verified")
        with self.assertRaisesRegex(ValueError, "without_evidence"):
            workorder_bridge.import_registry(self.db, self.state, self.source)
        self.assertEqual(self.db.execute(
            "SELECT COUNT(*) FROM sources").fetchone()[0], 0)

    def test_snapshot_rows_cannot_be_rewritten_or_deleted(self):
        self.write()
        sid = workorder_bridge.import_registry(
            self.db, self.state, self.source)["source_id"]
        import sqlite3
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("UPDATE cf200_orders SET status='verified' WHERE source_id=?", (sid,))
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("DELETE FROM cf200_snapshots WHERE source_id=?", (sid,))
        self.assertEqual(self.db.execute(
            "SELECT status FROM cf200_orders WHERE source_id=?", (sid,)
        ).fetchone()[0], "planned")


if __name__ == "__main__":
    unittest.main()
