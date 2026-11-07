"""CF-113: detect silent owner-priority changes in contract AND actual selector.

Uses temporary public-source copies and synthetic mutations only. Does not
change owner policy, access the physical HP or approve new authorities.
"""
import copy
import json
import pathlib
import tempfile
import unittest

from automation_200.capability_guard import (
    CONTRACT, ROOT, EXPECTED_STREAM_TIERS, REQUIRED_ACTIVE_SOURCE,
    _check_priority_selector_source, check,
)

BASE = json.loads(CONTRACT.read_text(encoding="utf-8"))
RELAY = (ROOT / "relay/cf_public_relay.py").read_text(encoding="utf-8")
SELECTOR = (ROOT / "automation_200/priority_selector.py").read_text(encoding="utf-8")


def temporary_tree(dest):
    paths = {
        "automation_200/priority_selector.py",
        "automation_200/MASTER_OPERATOR_PROMPT.md",
        "automation_200/MASTER_CONTINUITY_PROMPT.md",
    }
    paths.update(source for _, _, source in REQUIRED_ACTIVE_SOURCE.values())
    for name in paths:
        destination = dest / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / name).read_bytes())


class OwnerPolicyIntegrityTests(unittest.TestCase):
    def test_real_owner_contract_and_selector_agree(self):
        report = check(BASE, RELAY)
        self.assertEqual(report["owner"], "Kiara Lynn Rose Smith")
        self.assertFalse(report["owner_approval_proven"])
        self.assertEqual(EXPECTED_STREAM_TIERS["public_finance"], 2)
        self.assertEqual(EXPECTED_STREAM_TIERS["security"], 0)
        self.assertEqual(EXPECTED_STREAM_TIERS["research"], 3)

    def test_tier_swap_with_unchanged_contract_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            temporary_tree(root)
            path = root / "automation_200/priority_selector.py"
            path.write_text(SELECTOR.replace('"public_finance": 2', '"public_finance": 0'),
                            encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "founder_selector_priority_regression"):
                check(BASE, RELAY, root=root)

    def test_research_cannot_be_silently_promoted_above_automation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            temporary_tree(root)
            path = root / "automation_200/priority_selector.py"
            path.write_text(SELECTOR.replace('"research": 3', '"research": 0'),
                            encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "founder_selector_priority_regression"):
                _check_priority_selector_source(root)

    def test_duplicate_or_computed_policy_assignment_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            temporary_tree(root)
            path = root / "automation_200/priority_selector.py"
            path.write_text(SELECTOR + "\nPRIORITY_ORDER = {}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "owner_selector_policy_missing_or_ambiguous"):
                _check_priority_selector_source(root)
            path.write_text(SELECTOR.replace("PRIORITY_ORDER = {", "PRIORITY_ORDER = dict({")
                            .replace('\n}\n\ndef eligible_tasks', '\n})\n\ndef eligible_tasks'),
                            encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "owner_selector_policy_not_static"):
                _check_priority_selector_source(root)

    def test_contract_priority_swap_is_detected_separately(self):
        altered = copy.deepcopy(BASE)
        altered["priority_order"][0], altered["priority_order"][2] = (
            altered["priority_order"][2], altered["priority_order"][0])
        with self.assertRaisesRegex(ValueError, "founder_priority_regression"):
            check(altered, RELAY)


if __name__ == "__main__":
    unittest.main()
