"""CF-112: independent tasks may be proposed together across P0/P1/P2/P3.

A proposal for multiple independent workstreams is not unattended execution,
parallel HP control, permission to contact customers, or an approved purchase.
"""
import copy
import json
import pathlib
import unittest

from automation_200.decision_engine import propose
from automation_200.priority_selector import select_tasks

REGISTRY = json.loads((pathlib.Path(__file__).resolve().parents[1] / "registry.json").read_text(encoding="utf-8"))


def job(id, stream, *, deps=(), status="planned", hp=False):
    return {"id": id, "title": id, "stream": stream, "status": status,
            "priority": 1, "depends_on": list(deps), "physical_hp_required": hp,
            "authority": "existing-source-tests"}


class ConcurrentIndependentCF112Tests(unittest.TestCase):
    def test_independent_workstreams_can_share_read_only_proposal(self):
        example = {"tasks": [
            job("RESEARCH", "research"), job("FINANCE", "public_finance"),
            job("PRIORITY", "priority_logic"), job("AUTO", "receipt"),
        ]}
        original = copy.deepcopy(example)
        proposal = propose(example, now=1700, limit=4)
        self.assertEqual([r["id"] for r in proposal["selected"]],
                         ["AUTO", "PRIORITY", "FINANCE", "RESEARCH"])
        self.assertEqual([r["priority_tier"] for r in proposal["selected"]], [0, 1, 2, 3])
        self.assertEqual(len({r["id"] for r in proposal["selected"]}), 4)
        self.assertFalse(proposal["execution_authorized"])
        self.assertEqual(original, example)

    def test_dependency_on_proposed_task_does_not_become_verified_in_same_batch(self):
        example = {"tasks": [
            job("AUTO", "receipt"),
            job("NEEDS_AUTO", "priority_logic", deps=("AUTO",)),
            job("FINANCE", "public_finance"), job("RESEARCH", "research"),
        ]}
        proposal = propose(example, now=1700, limit=4)
        self.assertEqual([r["id"] for r in proposal["selected"]],
                         ["AUTO", "FINANCE", "RESEARCH"])
        self.assertEqual(proposal["held_counts"]["dependencies_unverified"], 1)
        self.assertEqual(example["tasks"][0]["status"], "planned")

    def test_blocked_p0_does_not_freeze_three_independent_other_lanes(self):
        example = {"tasks": [
            job("AUTO", "security"), job("PRIORITY", "priority_logic"),
            job("FINANCE", "public_finance"), job("RESEARCH", "research"),
        ]}
        proposal = propose(example, now=1700, limit=4, blocked_ids=["AUTO"])
        self.assertEqual([r["id"] for r in proposal["selected"]],
                         ["PRIORITY", "FINANCE", "RESEARCH"])
        self.assertEqual(proposal["held_counts"]["explicitly_blocked"], 1)

    def test_owner_preference_changes_order_not_eligibility(self):
        example = {"tasks": [
            job("AUTO", "receipt"), job("HP", "hp_install", hp=True),
            job("FINANCE", "public_finance"), job("RESEARCH", "research"),
        ]}
        plan = propose(example, now=1700, owner_preference_ids=["HP", "RESEARCH"])
        self.assertEqual([x["id"] for x in plan["selected"]],
                         ["RESEARCH", "AUTO", "FINANCE"])
        self.assertNotIn("HP", [x["id"] for x in plan["selected"]])
        self.assertTrue(plan["read_only"])

    def test_deterministic_real_registry_multiple_proposals_without_writes(self):
        original = copy.deepcopy(REGISTRY)
        a = propose(REGISTRY, now=1700, limit=8, health_state="not_published")
        b = propose(REGISTRY, now=1700, limit=8, health_state="not_published")
        self.assertEqual(a, b)
        self.assertEqual(REGISTRY, original)
        self.assertTrue(all(x["action"] == "propose_source_work_only" for x in a["selected"]))
        self.assertFalse(a["execution_authorized"])
        # Independent work can be ranked together; this alone does not prove
        # concurrently running processes on any device.
        self.assertEqual(select_tasks(REGISTRY, limit=8),
                         select_tasks(REGISTRY, limit=8))


if __name__ == "__main__":
    unittest.main()
