"""Exact-current-source CF-200 import smoke test; no private user sources."""
from pathlib import Path
import hashlib
import json
import tempfile
import unittest

from continuity import local_index
from continuity import workorder_bridge

ROOT = Path(__file__).resolve().parents[2]


class CurrentRegistryBridgeTests(unittest.TestCase):
    def test_exact_public_registry_import_and_idempotence(self):
        source = ROOT / "automation_200" / "registry.json"
        original_bytes = source.read_bytes()
        # The checkout can have CRLF on Windows; preserve canonical Git bytes
        # as a separate temp source for a stable cross-platform identity.
        canonical_git_bytes = original_bytes.replace(b"\r\n", b"\n")
        blob_digest = hashlib.sha1(
            b"blob " + str(len(canonical_git_bytes)).encode("ascii") + b"\0" + canonical_git_bytes
        ).hexdigest()
        state = json.loads((ROOT / "docs/PUBLIC_CONTINUITY_STATE.json").read_text())
        self.assertEqual(blob_digest, state["cf200"]["registry_git_blob_sha1"])
        self.assertFalse(state["cf200"]["registry_exact_raw_bytes_imported_into_private_store"])

        with tempfile.TemporaryDirectory(prefix="cf0-actual-registry-test-") as folder:
            private_dir = Path(folder) / "private-synthetic-only"
            with local_index.open_db(private_dir) as db:
                first = workorder_bridge.import_registry(
                    db, private_dir, source,
                    origin="CF-0 current checkout public authoritative raw bytes"
                )
                second = workorder_bridge.import_registry(
                    db, private_dir, source,
                    origin="CF-0 current checkout duplicate check"
                )
                self.assertTrue(first["imported"])
                self.assertFalse(second["imported"])
                self.assertEqual(first["orders"], 200)
                self.assertEqual(first["verified_source_statuses"], state["cf200"]["verified"])
                self.assertEqual(first["source_id"], "sha256:" + hashlib.sha256(original_bytes).hexdigest())
                summary = workorder_bridge.audit_workorders(db)
                self.assertEqual(summary["cf200_snapshots"], 1)
                self.assertEqual(summary["cf200_order_versions"], 200)
                self.assertEqual(summary["explicit_project_links"], 0)
                self.assertTrue(local_index.audit(db, full_hash=True)["chain_valid"])

if __name__ == "__main__":
    unittest.main()
