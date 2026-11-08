"""CF-118: deterministic retry boundary and owner-local hold regression.

Run: python -m unittest automation_200.tests.test_retry_boundary_cf118 -v
This is an offline, read-only source test; it is not HP execution evidence.
"""
import unittest

from automation_200.decision_engine import propose


def registry():
    return {"tasks": [
        {"id": "CF-001", "status": "verified", "stream": "priority_logic",
         "priority": 1, "depends_on": [], "physical_hp_required": False},
        {"id": "CF-002", "status": "planned", "stream": "priority_logic",
         "priority": 1, "depends_on": ["CF-001"], "physical_hp_required": False},
        {"id": "CF-003", "status": "planned", "stream": "priority_logic",
         "priority": 2, "depends_on": ["CF-001"], "physical_hp_required": False},
        {"id": "CF-004", "status": "planned", "stream": "hp_install",
         "priority": 1, "depends_on": ["CF-001"], "physical_hp_required": False},
    ]}


class RetryBoundaryTests(unittest.TestCase):
    def test_retry_cooldown_is_strict_before_boundary(self):
        attempts = {"CF-002": {"failures": 2, "failed_at": 1000}}
        before = propose(registry(), now=1599, attempts=attempts, limit=4)
        self.assertEqual(before["held_counts"].get("retry_cooldown"), 1)
        self.assertNotIn("CF-002", [item["id"] for item in before["selected"]])
        at = propose(registry(), now=1600, attempts=attempts, limit=4)
        self.assertNotIn("retry_cooldown", at["held_counts"])
        self.assertIn("CF-002", [item["id"] for item in at["selected"]])
        self.assertEqual(attempts["CF-002"], {"failures": 2, "failed_at": 1000})

    def test_retry_ceiling_remains_even_after_cooldown(self):
        result = propose(registry(), now=999999, attempts={
            "CF-002": {"failures": 3, "failed_at": 1000}}, limit=4)
        self.assertEqual(result["held_counts"].get("retry_limit_reached"), 1)
        self.assertNotIn("CF-002", [item["id"] for item in result["selected"]])
        self.assertIn("CF-003", [item["id"] for item in result["selected"]])

    def test_fresh_hp_report_never_unlocks_hp_install(self):
        result = propose(registry(), health_state="fresh_public_report",
                         now=1000, owner_preference_ids=["CF-004"], limit=4)
        self.assertEqual(result["held_counts"].get("hp_install_needs_local_review"), 1)
        self.assertNotIn("CF-004", [item["id"] for item in result["selected"]])
        self.assertFalse(result["execution_authorized"])


    def test_owner_override_cannot_reopen_exhausted_retry(self):
        attempts = {"CF-002": {"failures": 3, "failed_at": 1000}}
        result = propose(registry(), now=5000, attempts=attempts,
                         owner_preference_ids=["CF-002"], limit=4)
        self.assertEqual(result["held_counts"].get("retry_limit_reached"), 1)
        self.assertNotIn("CF-002", [item["id"] for item in result["selected"]])
        self.assertIn("CF-003", [item["id"] for item in result["selected"]])
        self.assertFalse(result["execution_authorized"])
        self.assertEqual(attempts["CF-002"], {"failures": 3, "failed_at": 1000})

    def test_future_failure_timestamp_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "future"):
            propose(registry(), now=1000, attempts={
                "CF-002": {"failures": 1, "failed_at": 1001}})


if __name__ == "__main__":
    unittest.main()
