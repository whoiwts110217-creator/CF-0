"""CF-116: stale/future task context cannot authorize a task proposal."""
import copy
import unittest

from automation_200.task_context_expiry import held_task_contexts
from automation_200.decision_engine import propose


def task(id_, stream="priority_logic", status="planned"):
    return {"id": id_, "stream": stream, "status": status,
            "depends_on": [], "physical_hp_required": False, "priority": 1,
            "authority": "owner-reviewed", "title": id_}


REG = {"tasks": [task("CF-115", status="verified"), task("CF-116"),
                  task("CF-122", stream="public_finance")]}


class ContextExpiryTests(unittest.TestCase):
    def test_expired_context_blocks_while_fresh_survives(self):
        before = copy.deepcopy(REG)
        out = propose(REG, now=1000,
                      owner_preference_ids=["CF-116"],
                      task_contexts={
                          "CF-116": {"created_at": 500, "expires_at": 1000},
                          "CF-122": {"created_at": 999, "expires_at": 1001},
                      })
        self.assertNotIn("CF-116", [x["id"] for x in out["selected"]])
        self.assertEqual([x["id"] for x in out["selected"]], ["CF-122"])
        self.assertEqual(out["held_counts"]["task_context_expired"], 1)
        self.assertEqual(REG, before)
        self.assertFalse(out["execution_authorized"])

    def test_future_issued_record_does_not_work(self):
        out = propose(REG, now=1000,
                      task_contexts={"CF-116": {"created_at": 1001, "expires_at": 2000}})
        self.assertEqual(out["held_counts"]["task_context_future_issued"], 1)
        self.assertNotIn("CF-116", [x["id"] for x in out["selected"]])

    def test_legacy_no_context_keeps_existing_behavior(self):
        expected = propose(REG, now=1000)
        self.assertEqual(expected, propose(REG, now=1000, task_contexts={}))
        self.assertIn("CF-116", [x["id"] for x in expected["selected"]])

    def test_unknown_tasks_bad_types_and_unbounded_contexts_refused(self):
        known = {t["id"] for t in REG["tasks"]}
        for wrong in (
            {"CF-999": {"created_at": 1, "expires_at": 2}},
            {"CF-116": {"created_at": True, "expires_at": 2}},
            {"CF-116": {"created_at": 2, "expires_at": 2}},
            {"CF-116": {"created_at": 1, "expires_at": 10**12 + 1}},
            {"CF-116": {"created_at": 1, "expires_at": 90 * 86400 + 2}},
            {"CF-116": {"created_at": 1, "expires_at": 2, "secret": "private"}},
            [],
        ):
            with self.subTest(wrong=wrong), self.assertRaises(ValueError):
                held_task_contexts(wrong, known, 1000)

    def test_an_expired_owner_preference_does_not_bypass_hold(self):
        out = propose(REG, now=1000,
                      owner_preference_ids=["CF-116", "CF-122"],
                      task_contexts={"CF-116": {"created_at": 100, "expires_at": 900}})
        self.assertEqual(out["selected"][0]["id"], "CF-122")
        self.assertTrue(out["read_only"])


if __name__ == "__main__":
    unittest.main()
