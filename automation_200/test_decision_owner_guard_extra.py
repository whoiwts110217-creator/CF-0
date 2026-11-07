"""Additional offline regression cases for cloud decision safety.

Run: python -m unittest automation_200.test_decision_owner_guard_extra
No HP, network, credentials, or registry writes.
"""
import unittest
from automation_200.decision_engine import propose


def task(tid, stream="security", status="planned", deps=(), hp=False):
    return {"id": tid, "title": "Synthetic task", "stream": stream,
            "status": status, "depends_on": list(deps), "priority": 1,
            "physical_hp_required": hp, "authority": "existing-source-tests"}


class OwnerGuardExtraTests(unittest.TestCase):
    def test_owner_preference_cannot_bypass_unverified_dependency(self):
        registry = {"tasks": [task("CF-001"), task("CF-002", deps=("CF-001",)),
                              task("CF-003")]}
        result = propose(registry, now=1000, owner_preference_ids=["CF-002"], limit=3)
        self.assertNotIn("CF-002", [t["id"] for t in result["selected"]])
        self.assertEqual(result["held_counts"].get("dependencies_unverified"), 1)

    def test_owner_preference_cannot_bypass_hp_gate(self):
        registry = {"tasks": [task("CF-001", hp=True), task("CF-002")]}
        result = propose(registry, now=1000, owner_preference_ids=["CF-001"],
                         health_state="fresh_public_report")
        self.assertEqual([t["id"] for t in result["selected"]], ["CF-002"])
        self.assertFalse(result["execution_authorized"])

    def test_owner_preference_cannot_bypass_owner_local_id(self):
        registry = {"tasks": [task("CF-042"), task("CF-002")]}
        result = propose(registry, now=1000, owner_preference_ids=["CF-042"])
        self.assertEqual([t["id"] for t in result["selected"]], ["CF-002"])
        self.assertEqual(result["held_counts"].get("owner_local_evidence_required"), 1)

    def test_duplicate_blocked_ids_fail_closed(self):
        registry = {"tasks": [task("CF-001")]}
        with self.assertRaisesRegex(ValueError, "invalid blocked"):
            propose(registry, now=1000, blocked_ids=["CF-001", "CF-001"])

    def test_no_automatic_completion_or_execution(self):
        registry = {"tasks": [task("CF-001")]}
        before = repr(registry)
        result = propose(registry, now=1000)
        self.assertEqual(repr(registry), before)
        self.assertTrue(result["read_only"])
        self.assertEqual(result["selected"][0]["action"], "propose_source_work_only")


if __name__ == "__main__":
    unittest.main()
