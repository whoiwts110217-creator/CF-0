#!/usr/bin/env python3
"""Source-only guard against accidental CF-0 capability and mission regression.

Read-only. This guard cannot independently prove owner approval or enforce
GitHub branch protections; it makes unreviewed disabling conspicuous in CI.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "automation_200" / "OWNER_CAPABILITY_CONTRACT.json"
EXPECTED_COMMANDS = frozenset({"ping", "hp_status", "sidecar_verify"})
REQUIRED_IDS = frozenset({
    "public_relay_ping", "public_relay_status",
    "public_relay_sidecar_verify", "hp_health_monitor",
    "founder_decision_engine", "relay_unknown_attempt_recovery",
    "notepad_owner_launch",
})
PRIORITY = ["automation", "owner_priority_policy", "legitimate_finance", "parallel_other_projects"]


def _relay_commands(source: str) -> frozenset[str]:
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "ALLOWED"
            for target in node.targets
        ):
            value = node.value
            if (not isinstance(value, ast.Call)
                    or not isinstance(value.func, ast.Name)
                    or value.func.id != "frozenset"
                    or len(value.args) != 1 or value.keywords):
                raise ValueError("relay_allowlist_is_not_static")
            literal = ast.literal_eval(value.args[0])
            if (not isinstance(literal, (tuple, list, set, frozenset))
                    or any(type(name) is not str for name in literal)):
                raise ValueError("invalid_relay_allowlist")
            return frozenset(literal)
    raise ValueError("relay_allowlist_missing")


def check(contract: dict, relay_source: str, *, root: Path = ROOT) -> dict:
    if not isinstance(contract, dict) or contract.get("schema") != "cf0.owner_capability_contract.v1":
        raise ValueError("capability_contract_missing_or_invalid")
    if contract.get("creator") != "David Smith" or contract.get("designated_owner") != "Kiara Lynn Rose Smith":
        raise ValueError("creator_owner_credit_regression")
    if contract.get("priority_order") != PRIORITY:
        raise ValueError("founder_priority_regression")
    mission = contract.get("mission")
    if not isinstance(mission, str) or "sustainable generational wealth" not in mission.lower():
        raise ValueError("generational_wealth_mission_missing")
    change_rule = contract.get("change_rule")
    if not isinstance(change_rule, str) or "silently" not in change_rule:
        raise ValueError("capability_change_rule_missing")
    caps = contract.get("capabilities")
    if not isinstance(caps, list):
        raise ValueError("missing_capabilities")
    if any(not isinstance(x, dict) or not isinstance(x.get("id"), str) for x in caps):
        raise ValueError("malformed_capability")
    names = [c["id"] for c in caps]
    if len(names) != len(set(names)) or not REQUIRED_IDS <= set(names):
        raise ValueError("capability_removed_or_duplicated")
    map_ = {c["id"]: c for c in caps}
    commands = _relay_commands(relay_source)
    active = {
        map_[key]["command"] for key in (
            "public_relay_ping", "public_relay_status", "public_relay_sidecar_verify")
        if map_[key].get("status") == "active_source"
    }
    if active != EXPECTED_COMMANDS or not active <= commands:
        raise ValueError("previously_active_command_removed")
    notepad = map_["notepad_owner_launch"]
    if notepad.get("previously_owner_approved") is not True or notepad.get("command") != "open_notepad":
        raise ValueError("historical_notepad_approval_erased")
    if notepad.get("status") not in ("regression_open", "active_source"):
        raise ValueError("notepad_regression_silently_retired")
    if notepad["status"] == "regression_open" and "open_notepad" in commands:
        raise ValueError("notepad_source_enabled_but_contract_not_updated")
    if notepad["status"] == "active_source" and "open_notepad" not in commands:
        raise ValueError("notepad_claimed_active_without_source")
    if not isinstance(notepad.get("last_known_issue"), str) or not notepad["last_known_issue"]:
        raise ValueError("notepad_regression_history_missing")
    for cap in caps:
        if cap.get("status") == "active_source":
            source = cap.get("source", cap.get("evidence"))
            if not isinstance(source, str) or not source or not (root / source).is_file():
                raise ValueError("active_capability_without_source:" + cap["id"])
    docs = contract.get("critical_documents")
    if (not isinstance(docs, dict) or "Master Records" not in docs.get("private_master_library_path", "")
            or "Project_Atlas" not in docs.get("private_reconstructed_project_atlas", "")):
        raise ValueError("private_master_reference_missing")
    return {
        "guard": "cf0.owner_capability_source_guard.v1",
        "creator": contract["creator"],
        "owner": contract["designated_owner"],
        "active_commands": sorted(active),
        "open_regressions": ["notepad_owner_launch"] if notepad["status"] == "regression_open" else [],
        "public_scope_only": True,
        "device_state": "unverified",
        "owner_approval_proven": False,
    }


def main():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    relay = (ROOT / "relay" / "cf_public_relay.py").read_text(encoding="utf-8")
    print(json.dumps(check(contract, relay), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
