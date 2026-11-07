"""CF-114 policy diff is deterministic, explanatory, read-only and unapproved."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from automation_200.policy_diff import ROOT, snapshot, compare, main


class PolicyDiffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for path in ["automation_200/OWNER_CAPABILITY_CONTRACT.json",
                     "automation_200/priority_selector.py"]:
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, target)

    def tearDown(self):
        self.temp.cleanup()

    def contract(self):
        path = self.root / "automation_200/OWNER_CAPABILITY_CONTRACT.json"
        return path, json.loads(path.read_text(encoding="utf-8"))

    def test_current_repository_matches_pinned_guard_without_implied_approval(self):
        output = compare(snapshot(ROOT))
        self.assertEqual(output["schema"], "cf0.owner_policy_diff.v1")
        self.assertFalse(output["policy_changed"])
        self.assertFalse(output["requires_owner_review"])
        self.assertFalse(output["owner_approval_proven"])
        self.assertEqual(output["changes"], [])
        self.assertTrue(output["read_only"])

    def test_order_and_tier_mutations_are_reported_but_not_accepted(self):
        path, data = self.contract()
        data["priority_order"] = list(reversed(data["priority_order"]))
        path.write_text(json.dumps(data), encoding="utf-8")
        source = self.root / "automation_200/priority_selector.py"
        source.write_text(source.read_text(encoding="utf-8").replace(
            '"research": 3', '"research": 0'), encoding="utf-8")
        before = {str(p): p.read_bytes() for p in (path, source)}
        output = compare(snapshot(self.root))
        self.assertTrue(output["requires_owner_review"])
        self.assertFalse(output["owner_approval_proven"])
        self.assertEqual([x["field"] for x in output["changes"]],
                         ["priority_order", "stream_tier"])
        self.assertEqual(output["changes"][1]["id"], "research")
        self.assertEqual(output["changes"][1]["before"], 3)
        self.assertEqual(output["changes"][1]["after"], 0)
        self.assertEqual(before, {str(p): p.read_bytes() for p in (path, source)})

    def test_capability_status_change_reported_and_historical_notepad_preserved(self):
        path, data = self.contract()
        for cap in data["capabilities"]:
            if cap["id"] == "notepad_owner_launch":
                cap["status"] = "active_source"
        path.write_text(json.dumps(data), encoding="utf-8")
        output = compare(snapshot(self.root))
        self.assertEqual(output["changes"], [{
            "field": "capability_status", "id": "notepad_owner_launch",
            "before": "regression_open", "after": "active_source",
            "risk": "owner_review",
        }])
        self.assertFalse(output["owner_approval_proven"])

    def test_compare_checked_out_source_without_false_baseline_claims(self):
        earlier = snapshot(self.root)
        path, data = self.contract()
        data["priority_order"] = ["automation", "legitimate_finance",
                                  "owner_priority_policy", "parallel_other_projects"]
        path.write_text(json.dumps(data), encoding="utf-8")
        output = compare(snapshot(self.root), earlier)
        self.assertTrue(output["policy_changed"])
        self.assertEqual(output["baseline_kind"], "explicit_checked_out_source")
        self.assertEqual(len(output["changes"]), 1)

    def test_invalid_dynamic_selector_never_executes_code(self):
        source = self.root / "automation_200/priority_selector.py"
        source.write_text(source.read_text(encoding="utf-8").replace(
            'PRIORITY_ORDER = {', 'PRIORITY_ORDER = dict({').replace(
            '\n}\n\ndef eligible_tasks', '\n})\n\ndef eligible_tasks'),
            encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "selector_priority_not_literal"):
            snapshot(self.root)

    def test_malformed_source_returns_safe_error_with_no_private_paths(self):
        path, data = self.contract()
        path.write_text("{private details unparseable}", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "^owner_contract_unavailable$"):
            snapshot(self.root)


if __name__ == "__main__":
    unittest.main()
