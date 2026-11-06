"""Synthetic restore failure-safety regression; no owner archive or private records."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from continuity import local_index as continuity


class RestoreFailureSafetyTests(unittest.TestCase):
    def test_tampered_member_rejected_without_partial_restore(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "synthetic.txt"
            source.write_bytes(b"synthetic source bytes only")
            state = root / "private_source"
            good = root / "valid.zip"
            with contextlib.closing(continuity.open_db(state)) as db:
                continuity.ingest(db, state, source, "synthetic", "test origin")
                continuity.backup_private(db, state, good)
            bad = root / "tampered.zip"
            with zipfile.ZipFile(good) as original, zipfile.ZipFile(bad, "w") as altered:
                for member in original.infolist():
                    data = original.read(member.filename)
                    if member.filename == "continuity.sqlite3":
                        data = b"tampered SQLite bytes"
                    altered.writestr(member, data)
            target = root / "new_private_restore"
            with self.assertRaisesRegex(ValueError, "backup_entry_(size|digest)_mismatch"):
                continuity.restore_private(bad, target)
            self.assertFalse(target.exists(), "failed restore must not leave partial target")
            self.assertEqual(list(root.glob("cf0-restore-*")), [],
                             "failed restore must clean temporary extraction")
            result = continuity.restore_private(good, target)
            self.assertTrue(result["verified_manifest"])
            with contextlib.closing(continuity.open_db(target)) as db:
                self.assertTrue(continuity.audit(db, full_hash=True)["chain_valid"])

    def test_existing_target_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / "existing_private"
            target.mkdir()
            marker = target / "do_not_replace.txt"
            marker.write_text("preserve", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "restore_target_must_not_exist"):
                continuity.restore_private(root / "missing.zip", target)
            self.assertEqual(marker.read_text(encoding="utf-8"), "preserve")


if __name__ == "__main__":
    unittest.main()
