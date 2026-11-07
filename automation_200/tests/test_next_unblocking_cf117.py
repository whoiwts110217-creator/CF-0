"""CF-117 next-unblocking selection tests; synthetic 200-task registry only."""
import copy
import unittest
from automation_200.next_unblocking_task import next_unblocking_task


def registry():
    items = []
    for n in range(1, 201):
        id_ = f"CF-{n:03d}"
        items.append({"id": id_, "stream": "priority_logic",
                      "status": "planned", "depends_on": [],
                      "physical_hp_required": False, "priority": 1,
                      "authority": "owner-reviewed", "title": id_})
    return {"tasks": items, "completed": 0, "target": 200}


class NextUnblockingTests(unittest.TestCase):
    def test_picks_first_unfinished_dependency_not_blocked_target(self):
        sample = registry()
        sample["tasks"][1]["depends_on"] = ["CF-001"]
        sample["tasks"][2]["depends_on"] = ["CF-002"]
        before = copy.deepcopy(sample)
        result = next_unblocking_task(sample, "CF-003")
        self.assertEqual(result["next"]["id"], "CF-001")
        self.assertFalse(result["execution_authorized"])
        self.assertEqual(sample, before)
        sample["tasks"][0]["status"] = "verified"
        self.assertEqual(next_unblocking_task(sample, "CF-003")["next"]["id"], "CF-002")

    def test_hp_or_owner_local_dependency_is_not_bypassed(self):
        sample = registry()
        sample["tasks"][0]["physical_hp_required"] = True
        sample["tasks"][1]["depends_on"] = ["CF-001"]
        result = next_unblocking_task(sample, "CF-002")
        self.assertIsNone(result["next"])
        self.assertTrue(result["blocked_or_owner_local"])
        sample["tasks"][0]["physical_hp_required"] = False
        sample["tasks"][0]["stream"] = "hp_install"
        self.assertIsNone(next_unblocking_task(sample, "CF-002")["next"])

    def test_explicit_block_on_only_prerequisite_does_not_skip_dependency(self):
        sample = registry()
        sample["tasks"][1]["depends_on"] = ["CF-001"]
        result = next_unblocking_task(sample, "CF-002", blocked_ids=["CF-001"])
        self.assertIsNone(result["next"])

    def test_verified_target_needs_no_work(self):
        sample = registry()
        sample["tasks"][0]["status"] = "verified"
        result = next_unblocking_task(sample, "CF-001")
        self.assertIsNone(result["next"])
        self.assertFalse(result["blocked_or_owner_local"])

    def test_dependency_cycle_or_unknown_target_rejected(self):
        sample = registry()
        sample["tasks"][0]["depends_on"] = ["CF-002"]
        sample["tasks"][1]["depends_on"] = ["CF-001"]
        with self.assertRaisesRegex(ValueError, "dependency_cycle"):
            next_unblocking_task(sample, "CF-001")
        with self.assertRaisesRegex(ValueError, "invalid_target_id"):
            next_unblocking_task(sample, "CF-999")

    def test_current_registry_can_propose_next_owner_source_task(self):
        import json
        from pathlib import Path
        path = Path(__file__).resolve().parents[1] / "registry.json"
        current = json.loads(path.read_text(encoding="utf-8"))
        result = next_unblocking_task(current, "CF-117")
        self.assertEqual(result["next"]["id"], "CF-117")
        self.assertFalse(result["execution_authorized"])


if __name__ == "__main__":
    unittest.main()
