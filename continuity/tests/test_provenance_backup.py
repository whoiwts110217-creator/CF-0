"""Synthetic continuity backup provenance regression; no private owner data."""
import contextlib
from pathlib import Path
import tempfile
import unittest

from continuity import local_index as continuity


class ProvenanceBackupTests(unittest.TestCase):
    def test_identical_bytes_keep_distinct_origins_across_backup_restore(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = root / "archive_one" / "record.txt"
            second = root / "archive_two" / "record.txt"
            for path in (first, second):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"synthetic same original bytes")
            state = root / "private_state"
            with contextlib.closing(continuity.open_db(state)) as db:
                a = continuity.ingest(db, state, first, "synthetic", "first origin")
                b = continuity.ingest(db, state, second, "synthetic", "second origin")
                self.assertEqual(a["source_id"], b["source_id"])
                before = continuity.audit(db, full_hash=True)
                self.assertEqual(before["sources"], 1)
                self.assertEqual(before["origins"], 2)
                archive = root / "private_backup.zip"
                continuity.backup_private(db, state, archive)
            restored = root / "restored_state"
            continuity.restore_private(archive, restored)
            with contextlib.closing(continuity.open_db(restored)) as db:
                after = continuity.audit(db, full_hash=True)
                self.assertTrue(after["chain_valid"])
                self.assertEqual(after["sources"], before["sources"])
                self.assertEqual(after["origins"], before["origins"])
                origins = list(db.execute(
                    "SELECT source_path, label FROM source_origins ORDER BY label"
                ))
                self.assertEqual([row["label"] for row in origins],
                                 ["first origin", "second origin"])
                self.assertEqual({row["source_path"] for row in origins},
                                 {str(first), str(second)})


if __name__ == "__main__":
    unittest.main()
