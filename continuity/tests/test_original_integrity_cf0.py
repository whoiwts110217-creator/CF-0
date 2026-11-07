"""Adversarial offline test: corrupted content-addressed originals fail closed."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from continuity import local_index as c


class OriginalIntegrityTests(unittest.TestCase):
    def test_corrupted_existing_original_rejected_without_new_origin_or_event(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            state = base / "private"
            original = base / "source.txt"
            original.write_bytes(b"original verified data")
            with c.open_db(state) as db:
                first = c.ingest(db, state, original, "memo", "first")
                stored = Path(first["private_original"])
                stored.write_bytes(b"corrupt")
                before = c.audit(db)
                with self.assertRaisesRegex(ValueError, "private_original_hash_mismatch"):
                    c.ingest(db, state, original, "memo", "second")
                after = c.audit(db)
                self.assertEqual(before["events"], after["events"])
                self.assertEqual(before["origins"], after["origins"])
                self.assertEqual(stored.read_bytes(), b"corrupt")

    def test_correct_duplicate_still_keeps_separate_provenance(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            state = base / "private"
            original = base / "source.txt"
            original.write_bytes(b"unchanged source")
            with c.open_db(state) as db:
                a = c.ingest(db, state, original, "memo", "first")
                b = c.ingest(db, state, original, "memo", "second")
                self.assertTrue(b["duplicate"])
                self.assertEqual(a["source_id"], b["source_id"])
                self.assertEqual(c.audit(db)["origins"], 2)
                self.assertTrue(c.audit(db, full_hash=True)["chain_valid"])

    def test_symlink_at_digest_path_rejected_if_supported(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            state = base / "private"
            original = base / "source.txt"
            original.write_bytes(b"symlink adversarial case")
            digest = hashlib.sha256(original.read_bytes()).hexdigest()
            dest = state / "originals" / digest[:2] / digest
            dest.parent.mkdir(parents=True)
            try:
                dest.symlink_to(original)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation unavailable")
            with c.open_db(state) as db:
                with self.assertRaisesRegex(ValueError, "private_original_path_not_regular_file"):
                    c.ingest(db, state, original, "memo")
                self.assertEqual(c.audit(db)["sources"], 0)

if __name__ == "__main__":
    unittest.main()
