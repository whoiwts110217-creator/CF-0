"""CF-111: finance remains below automation by default, without becoming a gate.

Owner-governed preferences may reprioritize *eligible* work, but not bypass
dependencies, physical HP requirements or explicit owner blocks.
"""
import copy
import json
import pathlib
import unittest

from automation_200.decision_engine import propose

REGISTRY = json.loads((pathlib.Path(__file__).resolve().parents[1] / "registry.json").read_text(encoding="utf-8"))


def item(id, stream, priority=1, *, depends=(), hp=False):
    return {"id": id, "title": id, "stream": stream, "status": "planned",
            "priority": priority, "depends_on": list(depends),
            "authority": "existing-source-tests", "physical_hp_required": hp}


class FinancePriorityCF111Tests(unittest.TestCase):
    def test_automation_then_priority_policy_then_finance_as_default(self):
        tasks = [
            item("F_LOW", "public_finance", 1),
            item("R", "research", 1),
            item("P0_LATE", "security", 4),
            item("P1", "priority_logic", 2),
            item("P0_FIRST", "receipt", 1),
        ]
        registry = {"tasks": tasks}
        original = copy.deepcopy(registry)
        result = propose(registry, now=5000, limit=10)
        self.assertEqual([x["id"] for x in result["selected"]],
                         ["P0_FIRST", "P0_LATE", "P1", "F_LOW", "R"])
        self.assertEqual([x["priority_tier"] for x in result["selected"]],
                         [0, 0, 1, 2, 3])
        self.assertEqual(registry, original)

    def test_blocked_automation_allows_finance_work_after_governance(self):
        tasks = [item("P0", "security"), item("P1", "priority_logic"),
                 item("F", "public_finance")]
        result = propose({"tasks": tasks}, now=5000, blocked_ids=["P0"])
        self.assertEqual([x["id"] for x in result["selected"]], ["P1", "F"])
        self.assertEqual(result["held_counts"]["explicitly_blocked"], 1)
        self.assertFalse(result["execution_authorized"])

    def test_founder_preference_can_change_eligible_order_explicitly(self):
        tasks = [item("P0", "receipt"), item("F", "public_finance")]
        result = propose({"tasks": tasks}, now=5000, owner_preference_ids=["F"])
        self.assertEqual([x["id"] for x in result["selected"]], ["F", "P0"])
        self.assertEqual(result["selected"][0]["decision_basis"],
                         "founder_explicit_priority")
        self.assertFalse(result["execution_authorized"])

    def test_preferences_cannot_promote_unsafe_finance_or_hp_work(self):
        tasks = [
            item("P0", "security"),
            item("HP", "hp_install", hp=True),
            item("F", "public_finance", depends=("HP",)),
        ]
        result = propose({"tasks": tasks}, now=5000,
                         owner_preference_ids=["F", "HP"])
        self.assertEqual([x["id"] for x in result["selected"]], ["P0"])
        self.assertIn("physical_hp_required", result["held_counts"])
        self.assertIn("dependencies_unverified", result["held_counts"])

    def test_current_real_registry_never_claims_spending_execution(self):
        result = propose(REGISTRY, health_state="not_published", now=5000, limit=15)
        self.assertTrue(result["read_only"])
        self.assertFalse(result["execution_authorized"])
        self.assertTrue(all(x["action"] == "propose_source_work_only"
                            for x in result["selected"]))
        tiers = [x["priority_tier"] for x in result["selected"]]
        self.assertEqual(tiers, sorted(tiers))


if __name__ == "__main__":
    unittest.main()
