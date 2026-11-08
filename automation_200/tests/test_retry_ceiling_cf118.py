"""CF-118 regression tests: bounded, read-only retry proposals (synthetic tasks).

These tests do not prove durable retries or actual HP execution. They protect
the retry ceiling, cooldown, owner priority and input-validation boundaries.
"""
import copy
import unittest

from automation_200.decision_engine import propose, RETRY_LIMIT, RETRY_BASE_SECONDS


def registry():
    tasks = []
    for n in range(1, 201):
        tid = f"CF-{n:03d}"
        tasks.append({
            "id": tid, "stream": "priority_logic", "status": "planned",
            "depends_on": [], "physical_hp_required": False,
            "priority": 1, "authority": "owner-reviewed", "title": tid,
        })
    return {"tasks": tasks, "completed": 0, "target": 200}


class RetryCeilingTests(unittest.TestCase):
    def test_failure_ceiling_blocks_even_owner_preference(self):
        sample = registry()
        before = copy.deepcopy(sample)
        result = propose(sample, now=10000, limit=4,
                         owner_preference_ids=["CF-001"],
                         attempts={"CF-001": {"failures": RETRY_LIMIT, "failed_at": 0}})
        self.assertNotIn("CF-001", [x["id"] for x in result["selected"]])
        self.assertEqual(result["held_counts"]["retry_limit_reached"], 1)
        self.assertFalse(result["execution_authorized"])
        self.assertEqual(sample, before)

    def test_cooldown_expires_at_exact_boundary(self):
        sample = registry()
        for failures in (1, 2):
            delay = RETRY_BASE_SECONDS * (2 ** (failures - 1))
            attempts = {"CF-001": {"failures": failures, "failed_at": 1000}}
            waiting = propose(sample, now=1000 + delay - 1,
                              owner_preference_ids=["CF-001"], attempts=attempts)
            self.assertNotIn("CF-001", [x["id"] for x in waiting["selected"]])
            self.assertEqual(waiting["held_counts"]["retry_cooldown"], 1)
            ready = propose(sample, now=1000 + delay,
                            owner_preference_ids=["CF-001"], attempts=attempts)
            self.assertEqual(ready["selected"][0]["id"], "CF-001")

    def test_missing_attempt_state_is_not_inferred(self):
        sample = registry()
        result = propose(sample, now=10000, owner_preference_ids=["CF-001"])
        self.assertEqual(result["selected"][0]["id"], "CF-001")
        self.assertFalse(result["execution_authorized"])

    def test_malformed_attempts_fail_closed(self):
        sample = registry()
        bad = [
            {"CF-999": {"failures": 1, "failed_at": 0}},
            {"CF-001": {"failures": True, "failed_at": 0}},
            {"CF-001": {"failures": 0, "failed_at": 0}},
            {"CF-001": {"failures": 11, "failed_at": 0}},
            {"CF-001": {"failures": 1, "failed_at": -1}},
            {"CF-001": {"failures": 1, "failed_at": 0, "command": "ping"}},
            [],
        ]
        for attempts in bad:
            with self.subTest(attempts=attempts), self.assertRaises(ValueError):
                propose(sample, now=10000, attempts=attempts)

    def test_hp_local_gate_remains_even_after_cooldown(self):
        sample = registry()
        sample["tasks"][0]["physical_hp_required"] = True
        result = propose(sample, now=10000,
                         owner_preference_ids=["CF-001"],
                         attempts={"CF-001": {"failures": 1, "failed_at": 0}})
        self.assertNotIn("CF-001", [x["id"] for x in result["selected"]])
        self.assertEqual(result["held_counts"]["physical_hp_required"], 1)


if __name__ == "__main__":
    unittest.main()
