"""Synthetic, offline regression coverage for the CF-200 continuity bridge."""
import json
from pathlib import Path
import tempfile
import unittest

from continuity import local_index
from continuity import workorder_bridge


class WorkorderBridgeTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        root = Path(self.folder.name)
        self.state = root / "store"
        self.source = root / "registry.json"
        self.db = local_index.open_db(self.state)
        self.addCleanup(self.db.close)
        local_index.add_project(self.db, "AUTO-03", "Relay", "CF-0 automation source")

    def snapshot(self, status="planned", evidence=""):
        items = [
            dict(id="CF-001", stream="chat_command", title="Protocol", status=status, evidence=evidence),
            dict(id="CF-002", stream="research", title="Research", status="planned", evidence=""),
        ]
        self.source.write_text(json.dumps(dict(tasks=items, target=2,
                                               completed=int(status=="verified"))))
        return workorder_bridge.import_registry(self.db, self.state, self.source)

    def test_import_idempotence(self):
        one = self.snapshot()
        two = self.snapshot()
        self.assertTrue(one["imported"])
        self.assertFalse(two["imported"])
        self.assertEqual(workorder_bridge.audit_workorders(self.db)["cf200_order_versions"], 2)

    def test_suggestions_do_not_create_project_links(self):
        source = self.snapshot()["source_id"]
        suggestions = workorder_bridge.suggest_links(self.db, source)
        self.assertEqual(len(suggestions["suggestions"]), 1)
        self.assertEqual(len(suggestions["unmapped"]), 1)
        self.assertEqual(workorder_bridge.audit_workorders(self.db)["explicit_project_links"], 0)

    def test_explicit_relation_does_not_change_project_state(self):
        source = self.snapshot()["source_id"]
        result = workorder_bridge.link_workorder(
            self.db, source, "CF-001", "AUTO-03", "supports",
            reason="Reviewed scope and source identity before linking")
        self.assertTrue(result["linked"])
        self.assertFalse(result["project_completed"])
        self.assertEqual(self.db.execute("SELECT state FROM projects WHERE id='AUTO-03'").fetchone()[0],
                         "concept")

    def test_verified_work_order_needs_evidence(self):
        with self.assertRaisesRegex(ValueError, "without_evidence"):
            self.snapshot(status="verified")

    def test_snapshot_difference_requires_review(self):
        before = self.snapshot()["source_id"]
        after = self.snapshot("verified", "Synthetic test evidence")["source_id"]
        result = workorder_bridge.snapshot_diff(self.db, before, after)
        self.assertEqual(len(result["changed"]), 1)
        self.assertTrue(result["changed"][0]["review_required"])
        self.assertTrue(local_index.audit(self.db, full_hash=True)["chain_valid"])


if __name__ == "__main__":
    unittest.main()
