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

    def test_rejects_noncanonical_or_missing_ids_before_ingestion(self):
        # Two tasks with valid-looking but noncanonical IDs must not enter
        # the private evidence store, even if counts and statuses agree.
        for ids in (("CF-001", "CF-003"), ("CF-001", "CF-999"),
                    ("CF-000", "CF-002"), ("CF-1", "CF-002")):
            with self.subTest(ids=ids):
                items = [dict(id=ident, stream="research", title=ident,
                              status="planned", evidence="") for ident in ids]
                self.source.write_text(json.dumps(
                    {"tasks": items, "target": 2, "completed": 0}), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "noncanonical_or_missing"):
                    workorder_bridge.import_registry(self.db, self.state, self.source)
                self.assertEqual(workorder_bridge.audit_workorders(self.db)["cf200_snapshots"], 0)

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

    def test_link_requires_a_known_project_and_preserves_existing_link(self):
        source = self.snapshot()["source_id"]
        with self.assertRaisesRegex(ValueError, "unknown_project"):
            workorder_bridge.link_workorder(
                self.db, source, "CF-001", "UNKNOWN-PROJECT", "related",
                reason="Reviewed a proposed relation to an unknown project")
        first = workorder_bridge.link_workorder(
            self.db, source, "CF-001", "AUTO-03", "supports",
            reason="Reviewed matching relay project and task descriptions")
        again = workorder_bridge.link_workorder(
            self.db, source, "CF-001", "AUTO-03", "supports",
            reason="Reviewed matching relay project and task descriptions")
        self.assertTrue(first["linked"])
        self.assertFalse(again["linked"])
        self.assertEqual(first["event_id"], again["event_id"])
        self.assertEqual(workorder_bridge.audit_workorders(self.db)["explicit_project_links"], 1)

    def test_evidence_revision_same_status_requires_review_and_preserves_prior_snapshot(self):
        first = self.snapshot("verified", "Synthetic evidence version one")["source_id"]
        second = self.snapshot("verified", "Synthetic evidence version two")["source_id"]
        self.assertNotEqual(first, second)
        diff = workorder_bridge.snapshot_diff(self.db, first, second)
        self.assertEqual(diff["missing_tasks"], [])
        self.assertEqual(diff["new_tasks"], [])
        self.assertEqual(len(diff["changed"]), 1)
        self.assertEqual(diff["changed"][0]["task_id"], "CF-001")
        self.assertEqual(diff["changed"][0]["before"], "verified")
        self.assertEqual(diff["changed"][0]["after"], "verified")
        self.assertTrue(diff["changed"][0]["evidence_changed"])
        self.assertTrue(diff["changed"][0]["review_required"])
        self.assertEqual(workorder_bridge.audit_workorders(self.db)["cf200_snapshots"], 2)
        self.assertEqual(workorder_bridge.audit_workorders(self.db)["explicit_project_links"], 0)
        self.assertTrue(local_index.audit(self.db, full_hash=True)["chain_valid"])

    def test_snapshot_difference_requires_review(self):
        before = self.snapshot()["source_id"]
        after = self.snapshot("verified", "Synthetic test evidence")["source_id"]
        result = workorder_bridge.snapshot_diff(self.db, before, after)
        self.assertEqual(len(result["changed"]), 1)
        self.assertTrue(result["changed"][0]["review_required"])
        self.assertTrue(local_index.audit(self.db, full_hash=True)["chain_valid"])


if __name__ == "__main__":
    unittest.main()
