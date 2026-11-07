"""CF-110: blocking the highest-priority task must not freeze safe work.

This is source-only decision testing, not HP execution or permission to bypass
the owner's declared P0/P1/P2/P3 priorities.
"""
import copy
import json
import pathlib
import unittest

from automation_200.decision_engine import propose

REGISTRY = json.loads((pathlib.Path(__file__).resolve().parents[1] / "registry.json").read_text(encoding="utf-8"))


def job(id, stream, *, status="planned", depends=(), hp=False, priority=1):
    return {
        "id": id, "title": id, "stream": stream, "status": status,
        "depends_on": list(depends), "physical_hp_required": hp,
        "priority": priority, "authority": "existing-source-tests"
    }


class BlockedPriorityCF110Tests(unittest.TestCase):
    def test_owner_explicitly_blocks_highest_p0_and_next_safe_p0_proceeds(self):
        registry = {"tasks": [
            job("TOP", "security", priority=1),
            job("ALTERNATE", "receipt", priority=2),
            job("FINANCE", "public_finance", priority=1),
        ]}
        before = copy.deepcopy(registry)
        result = propose(registry, health_state="not_published", now=1500,
                         blocked_ids=["TOP"], owner_preference_ids=["TOP"])
        self.assertEqual([x["id"] for x in result["selected"]], ["ALTERNATE", "FINANCE"])
        self.assertEqual(result["held_counts"]["explicitly_blocked"], 1)
        self.assertFalse(result["execution_authorized"])
        self.assertEqual(registry, before)

    def test_p0_dependency_block_and_hardware_hold_continue_through_lower_tiers(self):
        registry = {"tasks": [
            job("DEP", "security", depends=["MISSING"]),
            job("MISSING", "security", hp=True),
            job("HP", "hp_install"),
            job("SOURCE", "priority_logic"),
            job("CUSTOMER", "public_finance"),
        ]}
        result = propose(registry, health_state="fresh_public_report", now=1500,
                         owner_preference_ids=["DEP", "HP", "MISSING"])
        self.assertEqual([x["id"] for x in result["selected"]], ["SOURCE", "CUSTOMER"])
        self.assertEqual(result["held_counts"]["dependencies_unverified"], 1)
        self.assertEqual(result["held_counts"]["physical_hp_required"], 1)
        self.assertEqual(result["held_counts"]["hp_install_needs_local_review"], 1)
        self.assertFalse(result["hp_identity_attested"])

    def test_cooldown_and_retry_ceiling_do_not_stall_unblocked_work(self):
        registry = {"tasks": [
            job("RETRY", "security"), job("STOP", "receipt"),
            job("NEXT", "security"), job("P1", "priority_logic"),
        ]}
        failures = {"RETRY": {"failures": 2, "failed_at": 1000},
                    "STOP": {"failures": 3, "failed_at": 1000}}
        at_1200 = propose(registry, now=1200, attempts=failures,
                          owner_preference_ids=["RETRY", "STOP"])
        self.assertEqual([t["id"] for t in at_1200["selected"]], ["NEXT", "P1"])
        self.assertEqual(at_1200["held_counts"]["retry_cooldown"], 1)
        self.assertEqual(at_1200["held_counts"]["retry_limit_reached"], 1)
        after_cooldown = propose(registry, now=1600, attempts=failures)
        self.assertIn("RETRY", [t["id"] for t in after_cooldown["selected"]])
        self.assertNotIn("STOP", [t["id"] for t in after_cooldown["selected"]])

    def test_real_registry_blocked_p0_tasks_still_return_safe_proposals(self):
        first = propose(REGISTRY, now=1500, health_state="not_published", limit=8)
        self.assertGreater(first["selected_count"], 0)
        top = first["selected"][0]["id"]
        second = propose(REGISTRY, now=1500, health_state="not_published", limit=8,
                         blocked_ids=[top], owner_preference_ids=[top])
        self.assertNotIn(top, [t["id"] for t in second["selected"]])
        self.assertGreater(second["selected_count"], 0)
        self.assertEqual(second["held_counts"]["explicitly_blocked"], 1)
        self.assertTrue(all(not t["physical_hp_required"] for t in second["selected"]))
        self.assertTrue(all(t["action"] == "propose_source_work_only" for t in second["selected"]))
        self.assertFalse(second["execution_authorized"])


if __name__ == "__main__":
    unittest.main()
