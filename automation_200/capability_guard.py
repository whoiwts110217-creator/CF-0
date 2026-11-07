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
# This maps the owner's *existing* workstream tiers to selector source. This is
# regression detection only; owner-approved changes require an explicit policy
# decision and an accompanying deliberate guard/test revision.
EXPECTED_STREAM_TIERS = {
    "chat_command": 0, "hp_install": 0, "sidecar": 0,
    "receipt": 0, "security": 0, "real_operations": 0,
    "priority_logic": 1, "archive": 1,
    "public_finance": 2,
    "research": 3,
}


def _check_priority_selector_source(root: Path) -> None:
    source_path = root / "automation_200" / "priority_selector.py"
    try:
        nodes = ast.parse(source_path.read_text(encoding="utf-8")).body
    except (OSError, SyntaxError, UnicodeError):
        raise ValueError("owner_selector_policy_unreadable") from None
    assignments = [node for node in nodes
                   if isinstance(node, (ast.Assign, ast.AnnAssign))
                   and any(isinstance(target, ast.Name)
                           and target.id == "PRIORITY_ORDER"
                           for target in (node.targets if isinstance(node, ast.Assign)
                                          else [node.target]))]
    if len(assignments) != 1:
        raise ValueError("owner_selector_policy_missing_or_ambiguous")
    try:
        tiers = ast.literal_eval(assignments[0].value)
    except (ValueError, TypeError, SyntaxError):
        raise ValueError("owner_selector_policy_not_static") from None
    if (type(tiers) is not dict or tiers != EXPECTED_STREAM_TIERS
            or any(type(level) is not int for level in tiers.values())):
        raise ValueError("founder_selector_priority_regression")


# Minimum source capabilities from the last verified owner-facing contract.
# Changes to these expectations are governance changes; CI alone is not consent.
REQUIRED_ACTIVE_SOURCE = {
    "public_relay_ping": ("command", "ping", "relay/cf_public_relay.py"),
    "public_relay_status": ("command", "hp_status", "relay/cf_public_relay.py"),
    "public_relay_sidecar_verify": ("command", "sidecar_verify", "relay/cf_public_relay.py"),
    "hp_health_monitor": ("source", "relay/health_watch.py", "relay/health_watch.py"),
    "founder_decision_engine": ("source", "automation_200/decision_engine.py", "automation_200/decision_engine.py"),
    "relay_unknown_attempt_recovery": ("source", "relay/UNKNOWN_ATTEMPTS.md", "relay/UNKNOWN_ATTEMPTS.md"),
}



def _relay_commands(source: str) -> frozenset[str]:
    tree = ast.parse(source)
    assignments = [
        node for node in tree.body
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign))
        and any(isinstance(target, ast.Name) and target.id == "ALLOWED"
                for target in (node.targets if isinstance(node, ast.Assign)
                               else [node.target]))
    ]
    if len(assignments) != 1:
        raise ValueError("relay_allowlist_missing_or_ambiguous")
    value = assignments[0].value
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


def check(contract: dict, relay_source: str, *, root: Path = ROOT) -> dict:
    if not isinstance(contract, dict) or contract.get("schema") != "cf0.owner_capability_contract.v1":
        raise ValueError("capability_contract_missing_or_invalid")
    if contract.get("creator") != "David Smith" or contract.get("designated_owner") != "Kiara Lynn Rose Smith":
        raise ValueError("creator_owner_credit_regression")
    if contract.get("priority_order") != PRIORITY:
        raise ValueError("founder_priority_regression")
    _check_priority_selector_source(root)
    mission = contract.get("mission")
    if not isinstance(mission, str) or "sustainable generational wealth" not in mission.lower():
        raise ValueError("generational_wealth_mission_missing")
    change_rule = contract.get("change_rule")
    if not isinstance(change_rule, str) or "silently" not in change_rule:
        raise ValueError("capability_change_rule_missing")
    # Standing owner-directed continuity preflight; this source test detects
    # deletion of the rule, but cannot prove a model actually read the file.
    orders = contract.get("standing_owner_orders")
    if not isinstance(orders, list):
        raise ValueError("missing_owner_continuity_orders")
    order_map = {o.get("id"): o for o in orders if isinstance(o, dict)}
    first = order_map.get("public_master_read_first")
    merged = order_map.get("full_project_continuity")
    if (not isinstance(first, dict) or first.get("status") != "required"
            or first.get("scope") != "all_CF0_operational_decisions"
            or first.get("first_source") != "automation_200/MASTER_OPERATOR_PROMPT.md"
            or first.get("then_source") != "automation_200/MASTER_CONTINUITY_PROMPT.md"
            or not (root / first["first_source"]).is_file()
            or not (root / first["then_source"]).is_file()):
        raise ValueError("public_master_first_order_removed")
    if not isinstance(merged, dict) or merged.get("status") != "required":
        raise ValueError("whole_system_continuity_order_removed")
    caps = contract.get("capabilities")
    if not isinstance(caps, list):
        raise ValueError("missing_capabilities")
    if any(not isinstance(x, dict) or not isinstance(x.get("id"), str) for x in caps):
        raise ValueError("malformed_capability")
    names = [c["id"] for c in caps]
    if len(names) != len(set(names)) or not REQUIRED_IDS <= set(names):
        raise ValueError("capability_removed_or_duplicated")
    map_ = {c["id"]: c for c in caps}
    for cid, (kind, value, source) in REQUIRED_ACTIVE_SOURCE.items():
        record = map_[cid]
        if record.get("status") != "active_source":
            raise ValueError("approved_capability_silently_disabled:" + cid)
        if record.get(kind) != value or record.get("source", record.get("evidence")) != source:
            raise ValueError("approved_capability_evidence_replaced:" + cid)
    commands = _relay_commands(relay_source)
    active = {
        map_[key]["command"] for key in (
            "public_relay_ping", "public_relay_status", "public_relay_sidecar_verify")
        if map_[key].get("status") == "active_source"
    }
    if active != EXPECTED_COMMANDS or not active <= commands:
        raise ValueError("previously_active_command_removed")
    # Commands cannot be introduced just by changing relay code without
    # updating the owner-reviewed source contract and tests.
    if commands - EXPECTED_COMMANDS:
        if "open_notepad" in commands and map_["notepad_owner_launch"].get("status") == "regression_open":
            raise ValueError("notepad_source_enabled_but_contract_not_updated")
        raise ValueError("unlisted_command_exposed")
    notepad = map_["notepad_owner_launch"]
    if notepad.get("previously_owner_approved") is not True or notepad.get("command") != "open_notepad":
        raise ValueError("historical_notepad_approval_erased")
    if notepad.get("status") not in ("regression_open", "active_source"):
        raise ValueError("notepad_regression_silently_retired")

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
    if (not isinstance(docs, dict)
            or docs.get("private_master_library_path") != "/Caveman Focus/Master Records/Caveman_Focus_Integrated_Master_Record_2026-11-06_R2.docx"
            or docs.get("private_reconstructed_project_atlas") != "/Caveman Focus/Master Records/Caveman_Focus_Reconstructed_Project_Atlas_2026-11-06.json"):
        raise ValueError("current_private_master_reference_missing")
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
