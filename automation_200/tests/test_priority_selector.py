"""Owner priority and dependency selection regressions. No network/HP execution."""
import json
import unittest
from pathlib import Path
from automation_200.priority_selector import select_tasks

REGISTRY = json.loads((Path(__file__).resolve().parents[1] / "registry.json").read_text(encoding="utf-8"))

def task(id_, stream, status="planned", depends_on=(), priority=1, hp=False):
    return {"id":id_, "stream":stream, "status":status, "depends_on":list(depends_on),
            "priority":priority, "physical_hp_required":hp, "authority":"owner-reviewed",
            "title":id_}

class OwnerPriorityTests(unittest.TestCase):
    def test_real_registry_output_is_deterministic_and_source_only(self):
        first = select_tasks(REGISTRY, limit=8)
        self.assertEqual(first, select_tasks(REGISTRY, limit=8))
        self.assertTrue(first)
        self.assertTrue(all(REGISTRY["tasks"][next(i for i, t in enumerate(REGISTRY["tasks"]) if t["id"] == r["id"])]["status"] == "planned" for r in first))
        self.assertTrue(all(not r["physical_hp_required"] for r in first))

    def test_priority_tiers(self):
        sample = {"tasks":[task("F", "public_finance"), task("R","research"),
                           task("A","archive"), task("P","priority_logic"),
                           task("X","receipt")]}
        self.assertEqual([t["id"] for t in select_tasks(sample, limit=5)], ["X","A","P","F","R"])

    def test_blocked_task_skipped(self):
        sample = {"tasks":[task("X","receipt"), task("P","priority_logic")]}
        self.assertEqual([t["id"] for t in select_tasks(sample, blocked_ids=["X"])], ["P"])

    def test_unverified_dependency_not_selected(self):
        sample = {"tasks":[task("X","receipt",depends_on=["Z"]),
                           task("Z","receipt",status="planned"),
                           task("P","priority_logic")]}
        self.assertEqual([t["id"] for t in select_tasks(sample)], ["Z","P"])

    def test_explicit_owner_preference_cannot_bypass_dependency_or_hp_gate(self):
        sample = {"tasks":[task("R","research"),task("X","receipt"),
                           task("B","public_finance",depends_on=["Z"]),
                           task("Z","receipt",hp=True)]}
        preferred = ["R","B","Z"]
        self.assertEqual([t["id"] for t in select_tasks(sample,owner_preference_ids=preferred)],
                         ["R","X"])
        self.assertEqual([t["id"] for t in select_tasks(sample,owner_preference_ids=preferred,
                                                        allow_hp_tasks=True)],
                         ["R","Z","X"])

    def test_owner_override_without_mutation(self):
        sample = {"tasks":[task("F","public_finance"),task("X","receipt")]}
        before = json.dumps(sample, sort_keys=True)
        self.assertEqual(select_tasks(sample,owner_preference_ids=["F"])[0]["id"], "F")
        self.assertEqual(json.dumps(sample,sort_keys=True),before)

    def test_invalid_preferences_and_limit_fail_closed(self):
        sample={"tasks":[task("X","receipt")]}
        for kw in ({"limit":0},{"limit":21},{"owner_preference_ids":["none"]},
                   {"owner_preference_ids":["X","X"]}):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                select_tasks(sample,**kw)

if __name__ == "__main__":
    unittest.main()
