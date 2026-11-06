"""Source-level regression tests for documented approved capabilities.

A passing cloud test cannot prove the installed HP version or owner consent.
"""
import copy
import json
import unittest
from pathlib import Path

from automation_200.capability_guard import check, CONTRACT, ROOT

BASE = json.loads(CONTRACT.read_text(encoding="utf-8"))
RELAY = (ROOT / "relay" / "cf_public_relay.py").read_text(encoding="utf-8")


def altered(which, **kwargs):
    x = copy.deepcopy(BASE)
    for cap in x["capabilities"]:
        if cap["id"] == which:
            cap.update(kwargs)
            return x
    raise ValueError("not found")


class CapabilityGuardTests(unittest.TestCase):
    def test_real_source_reports_open_regression_without_claiming_restoration(self):
        state = check(BASE, RELAY)
        self.assertEqual(state["open_regressions"], ["notepad_owner_launch"])
        self.assertEqual(set(state["active_commands"]), {"ping", "hp_status", "sidecar_verify"})
        self.assertFalse(state["owner_approval_proven"])
        self.assertEqual(state["device_state"], "unverified")

    def test_owner_mission_is_not_swapped_or_erased(self):
        for change in (
            {"creator": "Kiara Lynn Rose Smith"},
            {"designated_owner": "Assistant"},
            {"mission": "Generate tests"},
            {"priority_order": ["finance", "automation", "other"]},
            {"change_rule": ""},
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                check({**BASE, **change}, RELAY)

    def test_removing_a_working_command_breaks_ci(self):
        changed=RELAY.replace("'ping', 'hp_status', 'sidecar_verify'",
                              "'ping', 'hp_status'", 1)
        with self.assertRaisesRegex(ValueError, "previously_active_command_removed"):
            check(BASE, changed)

    def test_manifest_cannot_silently_delete_historical_notepad(self):
        x=copy.deepcopy(BASE)
        x["capabilities"]=[c for c in x["capabilities"] if c["id"]!="notepad_owner_launch"]
        with self.assertRaisesRegex(ValueError, "capability_removed_or_duplicated"):
            check(x, RELAY)

    def test_manifest_cannot_silently_retire_notepad(self):
        with self.assertRaisesRegex(ValueError, "notepad_regression_silently_retired"):
            check(altered("notepad_owner_launch", status="retired"), RELAY)

    def test_manifest_cannot_call_notepad_restored_without_source(self):
        with self.assertRaisesRegex(ValueError, "notepad_claimed_active_without_source"):
            check(altered("notepad_owner_launch", status="active_source"), RELAY)

    def test_notepad_source_presence_without_contract_update_is_rejected(self):
        changed=RELAY.replace("'ping', 'hp_status', 'sidecar_verify'",
                              "'ping', 'hp_status', 'sidecar_verify', 'open_notepad'", 1)
        with self.assertRaisesRegex(ValueError, "notepad_source_enabled_but_contract_not_updated"):
            check(BASE, changed)

    def test_unexpected_command_allowlist_source_shape_rejected(self):
        changed=RELAY.replace("ALLOWED = frozenset(('ping', 'hp_status', 'sidecar_verify'))",
                              "ALLOWED = {'ping', 'hp_status', 'sidecar_verify'}", 1)
        with self.assertRaisesRegex(ValueError, "relay_allowlist_is_not_static"):
            check(BASE, changed)

    def test_active_capability_missing_source_rejected(self):
        with self.assertRaisesRegex(ValueError, "approved_capability_evidence_replaced"):
            check(altered("hp_health_monitor", source="missing.py"), RELAY)

    def test_silently_inactivating_any_approved_source_capability_fails(self):
        for cid in (
            "public_relay_ping", "public_relay_status", "public_relay_sidecar_verify",
            "hp_health_monitor", "founder_decision_engine",
            "relay_unknown_attempt_recovery",
        ):
            with self.subTest(capability=cid):
                with self.assertRaisesRegex(ValueError, "approved_capability_silently_disabled:" + cid):
                    check(altered(cid, status="disabled"), RELAY)

    def test_source_path_swapping_to_other_existing_file_fails(self):
        with self.assertRaisesRegex(ValueError, "approved_capability_evidence_replaced"):
            check(altered("founder_decision_engine", source="relay/health_watch.py"), RELAY)

    def test_unlisted_new_command_cannot_be_silently_exposed(self):
        relay = RELAY.replace("'ping', 'hp_status', 'sidecar_verify'",
                              "'ping', 'hp_status', 'sidecar_verify', 'delete_data'", 1)
        with self.assertRaisesRegex(ValueError, "unlisted_command_exposed"):
            check(BASE, relay)

    def test_repeated_allowlist_assignment_is_not_trusted(self):
        relay = RELAY + "\nALLOWED = frozenset(('ping', 'hp_status'))\n"
        with self.assertRaisesRegex(ValueError, "relay_allowlist_missing_or_ambiguous"):
            check(BASE, relay)

    def test_old_private_master_pointer_is_rejected(self):
        docs = {**BASE["critical_documents"],
                "private_master_library_path":
                    "/Caveman Focus/Master Records/Caveman_Focus_Integrated_Master_Record_2026-11-06.docx"}
        with self.assertRaisesRegex(ValueError, "current_private_master_reference_missing"):
            check({**BASE, "critical_documents": docs}, RELAY)



if __name__ == "__main__":
    unittest.main()
