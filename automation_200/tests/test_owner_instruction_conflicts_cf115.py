"""CF-115 conflicting owner directions fail closed without changing policy."""
import unittest
from automation_200.owner_instruction_conflicts import analyze
from automation_200.priority_selector import select_tasks

IDS = {"CF-114", "CF-115", "CF-122"}
def order(rid, task, decision, verified=True):
    return {"id": rid, "task_id": task, "decision": decision,
            "authority_verified": verified}

def task(id_, stream):
    return {"id": id_, "stream": stream, "status": "planned",
            "depends_on": [], "priority": 1, "physical_hp_required": False,
            "authority": "existing-source-tests", "title": id_}


class ConflictingOwnerDirectionsTests(unittest.TestCase):
    def test_conflicting_directions_require_resolution_and_are_blocked(self):
        result = analyze([order("first", "CF-115", "prioritize"),
                          order("second", "CF-115", "block"),
                          order("third", "CF-122", "prioritize")], IDS)
        self.assertTrue(result["owner_resolution_required"])
        self.assertEqual(result["conflicting_task_ids"], ["CF-115"])
        self.assertEqual(result["blocked_ids"], ["CF-115"])
        self.assertEqual(result["preferred_ids"], ["CF-122"])
        self.assertFalse(result.get("owner_approval_proven", False))
        queue = select_tasks({"tasks": [task("CF-115", "priority_logic"),
                                         task("CF-122", "public_finance")]},
                             blocked_ids=result["blocked_ids"],
                             owner_preference_ids=result["preferred_ids"])
        self.assertEqual([x["id"] for x in queue], ["CF-122"])

    def test_input_reordering_does_not_change_result(self):
        records = [order("b", "CF-122", "block"),
                   order("c", "CF-115", "prioritize"),
                   order("a", "CF-122", "prioritize")]
        self.assertEqual(analyze(records, IDS), analyze(list(reversed(records)), IDS))

    def test_absent_or_untrusted_authorization_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "unverified_or_invalid"):
            analyze([order("r", "CF-115", "prioritize", False)], IDS)
        with self.assertRaisesRegex(ValueError, "unverified_or_invalid"):
            analyze([order("r", "CF-999", "prioritize")], IDS)
        with self.assertRaisesRegex(ValueError, "invalid_owner_direction_record"):
            analyze([{"id": "r", "task_id": "CF-115", "decision": "block",
                      "authority_verified": True, "owner_message": "private"}], IDS)

    def test_duplicate_record_ids_and_unknown_decisions_fail(self):
        with self.assertRaisesRegex(ValueError, "unverified_or_invalid"):
            analyze([order("same", "CF-115", "block"),
                     order("same", "CF-122", "prioritize")], IDS)
        with self.assertRaisesRegex(ValueError, "unverified_or_invalid"):
            analyze([order("x", "CF-115", "execute_shell")], IDS)

    def test_records_never_mutated_or_silently_resolved_by_timestamp(self):
        records = [order("older", "CF-114", "block"),
                   order("newer", "CF-114", "prioritize")]
        before = [dict(x) for x in records]
        result = analyze(records, IDS)
        self.assertEqual(records, before)
        self.assertEqual(result["conflicts"][0]["record_ids"], ["newer", "older"])
        self.assertEqual(result["blocked_ids"], ["CF-114"])

    def test_empty_batch_is_not_implied_consent(self):
        result = analyze([], IDS)
        self.assertEqual(result["preferred_ids"], [])
        self.assertEqual(result["blocked_ids"], [])
        self.assertFalse(result["owner_resolution_required"])
        self.assertTrue(result["read_only"])


if __name__ == "__main__":
    unittest.main()
