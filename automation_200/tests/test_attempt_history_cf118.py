"""CF-118 reviewed failure history; synthetic data, no HP or network."""
import copy
import json
import unittest
from automation_200.attempt_history_cf118 import (
    replay_reviewed_attempts, propose_with_reviewed_attempts, SCHEMA,
)


def registry():
    tasks = [{"id": f"CF-{n:03d}", "stream": "priority_logic", "title": str(n),
              "priority": 2, "depends_on": [], "status": "verified",
              "authority": "owner-reviewed", "physical_hp_required": False}
             for n in range(1, 201)]
    tasks[117]["status"] = "planned"
    return {"tasks": tasks, "completed": 199, "target": 200}


def event(n, at, result="failed", task_id="CF-118"):
    return json.dumps({"schema": SCHEMA, "event_id": f"test-{n}", "task_id": task_id,
                       "occurred_at": at, "result": result, "evidence_ref": f"ci:example-{n}",
                       "reviewed": True}, sort_keys=True)


class AttemptHistoryTests(unittest.TestCase):
    def test_cooldown_then_ceiling_then_verified_reset(self):
        sample = registry()
        original = copy.deepcopy(sample)
        lines = [event(1, 1000)]
        state = replay_reviewed_attempts(sample, lines, now=1001)
        self.assertEqual(state, {"CF-118": {"failures": 1, "failed_at": 1000}})
        self.assertEqual(propose_with_reviewed_attempts(sample, lines, now=1001)["held_counts"]["retry_cooldown"], 1)
        self.assertEqual(propose_with_reviewed_attempts(sample, lines, now=1300)["selected"][0]["id"], "CF-118")
        lines += [event(2, 1400), event(3, 1600)]
        self.assertEqual(propose_with_reviewed_attempts(sample, lines, now=10000)["held_counts"]["retry_limit_reached"], 1)
        self.assertEqual(propose_with_reviewed_attempts(sample, lines + [event(4, 10001, "verified_success")], now=10002)["selected"][0]["id"], "CF-118")
        self.assertEqual(sample, original)

    def test_reject_bad_or_unreviewed_events(self):
        base = json.loads(event(1, 10))
        for key, value in [("reviewed", False), ("task_id", "CF-999"),
                           ("occurred_at", 1001), ("result", "ok"),
                           ("evidence_ref", "bad" + chr(10) + "link")]:
            record = dict(base, **{key: value})
            with self.subTest(key=key), self.assertRaises(ValueError):
                replay_reviewed_attempts(registry(), [json.dumps(record)], now=1000)
        with self.assertRaises(ValueError):
            replay_reviewed_attempts(registry(), [event(1, 10), event(1, 11)], now=20)
        with self.assertRaises(ValueError):
            replay_reviewed_attempts(registry(), [event(1, 20), event(2, 19)], now=30)

    def test_reject_malformed_result_and_no_raw_override(self):
        sample = registry()
        row = json.loads(event(1, 10))
        row["result"] = []
        with self.assertRaises(ValueError):
            replay_reviewed_attempts(sample, [json.dumps(row)], now=20)
        with self.assertRaises(ValueError):
            propose_with_reviewed_attempts(sample, [], now=5, attempts={})
        result = propose_with_reviewed_attempts(sample, [], now=5)
        self.assertFalse(result["execution_authorized"])
        self.assertFalse(result["attempt_history_persisted_here"])
        self.assertEqual(result["selected"][0]["id"], "CF-118")


if __name__ == "__main__":
    unittest.main()
