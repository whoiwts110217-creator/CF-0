"""Offline tests for CF-200 owner-governed decisions. Never execute tasks."""
import copy
import json
import unittest
from pathlib import Path

from automation_200.decision_engine import propose

REGISTRY = json.loads(
    (Path(__file__).resolve().parents[1] / "registry.json").read_text(encoding="utf-8")
)


def task(tid, stream, *, status="planned", dependencies=(), hp=False, priority=1):
    return {"id": tid, "title": tid, "stream": stream,
            "status": status, "depends_on": list(dependencies),
            "physical_hp_required": hp, "priority": priority,
            "authority": "owner-reviewed"}


class EvidenceDecisionTests(unittest.TestCase):
    def test_real_registry_has_safe_source_work_when_hp_missing(self):
        plan = propose(REGISTRY, health_state="not_published")
        self.assertEqual(plan["schema"], "cf200.decision_proposal.v1")
        self.assertTrue(plan["read_only"])
        self.assertFalse(plan["execution_authorized"])
        self.assertTrue(plan["selected"])
        self.assertTrue(all(x["priority_tier"] == 0 for x in plan["selected"]))
        self.assertTrue(all(x["action"] == "propose_source_work_only" for x in plan["selected"]))
        self.assertNotIn("CF-027", [x["id"] for x in plan["selected"]])
        self.assertNotIn("CF-042", [x["id"] for x in plan["selected"]])
        self.assertGreater(plan["held_counts"].get("hp_install_needs_local_review", 0), 0)
        self.assertGreater(plan["held_counts"].get("owner_local_evidence_required", 0), 0)

    def test_heartbeat_cannot_authorize_hp_or_installation(self):
        sample = {"tasks": [task("HP", "hp_install"),
                            task("HW", "real_operations", hp=True),
                            task("SRC", "security")]}
        for state in ("not_published", "fresh_public_report", "reported_problem",
                      "stale", "unavailable"):
            with self.subTest(state=state):
                report = propose(sample, health_state=state, now=100)
                self.assertEqual([x["id"] for x in report["selected"]], ["SRC"])
                self.assertFalse(report["hp_identity_attested"])
                self.assertIn("hp_install_needs_local_review", report["held_counts"])
                self.assertIn("physical_hp_required", report["held_counts"])

    def test_misflagged_owner_local_work_is_never_cloud_eligible(self):
        sample = {"tasks": [task("CF-042", "sidecar"),
                            task("CF-190", "real_operations"),
                            task("SRC", "receipt")]}
        result = propose(sample, health_state="fresh_public_report", now=100)
        self.assertEqual([x["id"] for x in result["selected"]], ["SRC"])
        self.assertEqual(result["held_counts"]["owner_local_evidence_required"], 2)

    def test_dependency_block_and_explicit_owner_override(self):
        sample = {"tasks": [task("P0", "receipt"),
                            task("P1", "priority_logic"),
                            task("F", "public_finance"),
                            task("WAIT", "security", dependencies=["Z"]),
                            task("Z", "security", status="verified")]}
        report = propose(sample, now=100, owner_preference_ids=["F"])
        self.assertEqual([x["id"] for x in report["selected"]], ["F", "P0", "WAIT", "P1"])
        self.assertEqual(report["selected"][0]["decision_basis"], "founder_explicit_priority")
        blocked = propose(sample, now=100, blocked_ids=["F", "WAIT"])
        self.assertEqual([x["id"] for x in blocked["selected"]], ["P0", "P1"])
        self.assertEqual(blocked["held_counts"]["explicitly_blocked"], 2)

    def test_retry_backoff_and_ceiling(self):
        sample = {"tasks": [task("A", "security"), task("B", "security"),
                            task("C", "priority_logic"), task("D", "public_finance")]}
        attempts = {
            "A": {"failures": 1, "failed_at": 1000},
            "B": {"failures": 2, "failed_at": 1000},
            "C": {"failures": 3, "failed_at": 1000},
        }
        at_1200 = propose(sample, now=1200, attempts=attempts)
        self.assertEqual([x["id"] for x in at_1200["selected"]], ["D"])
        self.assertEqual(at_1200["held_counts"]["retry_cooldown"], 2)
        self.assertEqual(at_1200["held_counts"]["retry_limit_reached"], 1)
        at_1300 = propose(sample, now=1300, attempts=attempts)
        self.assertEqual([x["id"] for x in at_1300["selected"]], ["A", "D"])
        at_1600 = propose(sample, now=1600, attempts=attempts)
        self.assertEqual([x["id"] for x in at_1600["selected"]], ["A", "B", "D"])
        self.assertNotIn("C", [x["id"] for x in at_1600["selected"]])

    def test_owner_override_cannot_bypass_retry_or_hardware(self):
        sample = {"tasks": [task("R", "research"), task("H", "hp_install"),
                            task("S", "security")]}
        result = propose(sample, now=1000, attempts={"S": {"failures": 3, "failed_at": 900}},
                         owner_preference_ids=["S", "H", "R"])
        self.assertEqual([x["id"] for x in result["selected"]], ["R"])
        self.assertEqual(result["selected"][0]["decision_basis"], "founder_explicit_priority")

    def test_input_and_attempt_validation_fails_closed(self):
        sample = {"tasks": [task("A", "receipt")]}
        bad_cases = (
            {"health_state": "healthy"},
            {"limit": 0},
            {"blocked_ids": ["A", "A"]},
            {"blocked_ids": ["UNKNOWN"]},
            {"attempts": {"A": {"failures": True, "failed_at": 90}}},
            {"attempts": {"A": {"failures": 3, "failed_at": -1}}},
            {"attempts": {"A": {"failures": 1}}},
            {"attempts": {"B": {"failures": 1, "failed_at": 5}}},
            {"attempts": []},
            {"now": -1},
            {"owner_preference_ids": ["UNKNOWN"]},
        )
        for case in bad_cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                propose(sample, **case)

    def test_pure_deterministic_and_no_registry_or_attempt_mutation(self):
        sample = {"tasks": [task("A", "receipt"), task("B", "public_finance")]}
        attempts = {"B": {"failures": 1, "failed_at": 100}}
        before = copy.deepcopy((sample, attempts))
        one = propose(sample, now=800, attempts=attempts)
        two = propose(sample, now=800, attempts=attempts)
        self.assertEqual(one, two)
        self.assertEqual((sample, attempts), before)
        self.assertNotIn("new_receipts", one)
        self.assertNotIn("verified_tasks", one)


if __name__ == "__main__":
    unittest.main()
