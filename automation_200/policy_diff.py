#!/usr/bin/env python3
"""CF-114: read-only, public-safe owner policy diff against pinned source contract.

Detects and explains what differs; never changes the policy or implies that an
owner has approved a difference. Source paths, private text, and credentials
are not echoed. For explicit release comparisons, a checked-out baseline
folder can be passed with --baseline-dir; otherwise the pinned expected
contract embedded in the current capability guard is the baseline.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

from . import capability_guard as guard

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CREATOR = "David Smith"
EXPECTED_OWNER = "Kiara Lynn Rose Smith"
EXPECTED_OWNER_PRIORITY = tuple(guard.PRIORITY)
EXPECTED_STREAM_TIERS = dict(guard.EXPECTED_STREAM_TIERS)
EXPECTED_CAPABILITIES = tuple(sorted(guard.REQUIRED_IDS))
ALLOWED_STATES = {"active_source", "regression_open", "blocked", "planned"}


def _static_selector_tiers(root: Path):
    """Return a literal tier map without importing or executing source code."""
    try:
        nodes = ast.parse((root / "automation_200/priority_selector.py").read_text(encoding="utf-8")).body
    except (OSError, SyntaxError, UnicodeError):
        raise ValueError("selector_source_unavailable") from None
    assignments = [node for node in nodes if isinstance(node, (ast.Assign, ast.AnnAssign))
                   and any(isinstance(t, ast.Name) and t.id == "PRIORITY_ORDER"
                           for t in (node.targets if isinstance(node, ast.Assign) else [node.target]))]
    if len(assignments) != 1:
        raise ValueError("selector_priority_not_unique")
    try:
        value = ast.literal_eval(assignments[0].value)
    except (ValueError, TypeError, SyntaxError):
        raise ValueError("selector_priority_not_literal") from None
    if (type(value) is not dict or any(type(k) is not str or type(v) is not int
                                     or v < 0 or v > 4 for k, v in value.items())):
        raise ValueError("selector_priority_invalid")
    return value


def _contract(root: Path):
    try:
        data = json.loads((root / "automation_200/OWNER_CAPABILITY_CONTRACT.json").read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        raise ValueError("owner_contract_unavailable") from None
    if not isinstance(data, dict) or data.get("schema") != "cf0.owner_capability_contract.v1":
        raise ValueError("owner_contract_invalid")
    priorities = data.get("priority_order")
    if type(priorities) is not list or any(type(v) is not str for v in priorities):
        raise ValueError("owner_priorities_invalid")
    caps = data.get("capabilities")
    if not isinstance(caps, list) or any(not isinstance(c, dict) for c in caps):
        raise ValueError("owner_capabilities_invalid")
    statuses = {}
    for cap in caps:
        cid, status = cap.get("id"), cap.get("status")
        if (type(cid) is not str or cid not in EXPECTED_CAPABILITIES
                or cid in statuses or type(status) is not str or status not in ALLOWED_STATES):
            raise ValueError("owner_capabilities_invalid")
        statuses[cid] = status
    return {
        "creator": data.get("creator") == EXPECTED_CREATOR,
        "owner": data.get("designated_owner") == EXPECTED_OWNER,
        "priorities": tuple(priorities),
        "capabilities": statuses,
    }


def snapshot(root: Path):
    contract = _contract(root)
    contract["tiers"] = _static_selector_tiers(root)
    return contract


def compare(current: dict, baseline: dict | None = None) -> dict:
    if baseline is None:
        baseline = {
            "creator": True, "owner": True, "priorities": EXPECTED_OWNER_PRIORITY,
            "tiers": EXPECTED_STREAM_TIERS,
            "capabilities": {
                **{key: "active_source" for key in guard.REQUIRED_ACTIVE_SOURCE},
                "notepad_owner_launch": "regression_open",
            },
        }
    changes = []
    if current["creator"] != baseline["creator"]:
        changes.append({"field": "creator_credit", "before": "expected", "after": "changed", "risk": "owner_review"})
    if current["owner"] != baseline["owner"]:
        changes.append({"field": "designated_owner_credit", "before": "expected", "after": "changed", "risk": "owner_review"})
    if current["priorities"] != baseline["priorities"]:
        changes.append({
            "field": "priority_order", "before": list(baseline["priorities"]),
            "after": list(current["priorities"]), "risk": "owner_review",
        })
    for stream in sorted(set(current["tiers"]) | set(baseline["tiers"])):
        before, after = baseline["tiers"].get(stream), current["tiers"].get(stream)
        if before != after:
            changes.append({
                "field": "stream_tier", "id": stream, "before": before,
                "after": after, "risk": "owner_review",
            })
    for cid in sorted(set(current["capabilities"]) | set(baseline["capabilities"])):
        before, after = baseline["capabilities"].get(cid), current["capabilities"].get(cid)
        if before != after:
            changes.append({
                "field": "capability_status", "id": cid, "before": before,
                "after": after, "risk": "owner_review",
            })
    return {
        "schema": "cf0.owner_policy_diff.v1",
        "read_only": True,
        "owner_approval_proven": False,
        "baseline_kind": "pinned_source_contract" if baseline is None else "explicit_checked_out_source",
        "policy_changed": bool(changes),
        "requires_owner_review": bool(changes),
        "changes": changes,
        "note": "A diff is evidence of source changes, not approval, deployed HP state or proof of a legal transfer.",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-dir", type=Path, help="Optional existing offline baseline checkout")
    parser.add_argument("--current-dir", type=Path, default=ROOT, help="Existing checkout; no modifications")
    args = parser.parse_args(argv)
    try:
        result = compare(snapshot(args.current_dir),
                         snapshot(args.baseline_dir) if args.baseline_dir else None)
    except ValueError as exc:
        print(json.dumps({"schema": "cf0.owner_policy_diff.v1",
                          "read_only": True, "error": str(exc), "owner_approval_proven": False}))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
