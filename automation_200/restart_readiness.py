#!/usr/bin/env python3
"""Read-only CF-0 completion and restart/cutover readiness report.

This does not run a restart, disable schedules, modify any project, or read
private archives. Positive evidence must be independently verified by the owner.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from automation_200.prompt_change_guard import audit as prompt_audit
from automation_200.release_gate import evaluate as release_evaluate
from automation_200.validate_registry import check_registry

ROOT = Path(__file__).resolve().parents[1]
RESTART_GATES = (
    "hp_scheduled_receipt_correlated",
    "seven_day_unattended_cycle",
    "private_backup_restore_rehearsal",
    "non_destructive_rollback_rehearsal",
    "owner_cutover_approval",
)


def declared_gates(evidence: dict) -> dict:
    if not isinstance(evidence, dict):
        raise ValueError("restart evidence must be an object")
    extra = set(evidence) - set(RESTART_GATES) - {"release_gates"}
    if extra:
        raise ValueError("unknown restart gate names: " + ", ".join(sorted(extra)))
    gates = {}
    for name in RESTART_GATES:
        record = evidence.get(name, {"status": "unverified", "evidence": []})
        if not isinstance(record, dict) or record.get("status") not in ("verified", "unverified", "blocked"):
            raise ValueError("invalid restart gate: " + name)
        refs = record.get("evidence", [])
        if not isinstance(refs, list) or any(not isinstance(x, str) or not x.startswith("https://") for x in refs):
            raise ValueError("invalid gate references: " + name)
        if record["status"] == "verified" and not refs:
            raise ValueError("verified restart gate requires evidence: " + name)
        gates[name] = {"status": record["status"], "evidence": refs}
    return gates


def fingerprint(raw: bytes) -> str:
    # The canonical public registry uses LF Git blobs. Checkout on Windows
    # can convert this text to CRLF without changing the Git object.
    raw = raw.replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def evaluate(root: Path = ROOT, evidence: dict | None = None) -> dict:
    evidence = {} if evidence is None else evidence
    gates = declared_gates(evidence)
    source_problems = []
    completed, total = 0, 200
    try:
        raw = (root / "automation_200/registry.json").read_bytes()
        registry = json.loads(raw)
        counts = check_registry(registry)
        completed, total = counts["verified"], counts["target"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        source_problems.append("registry_unavailable_or_invalid:" + type(exc).__name__)
        raw = None

    try:
        state = json.loads((root / "docs/PUBLIC_CONTINUITY_STATE.json").read_text(encoding="utf-8"))
        if raw is None or state.get("cf200", {}).get("verified") != completed:
            source_problems.append("continuity_count_does_not_match_registry")
        elif state["cf200"].get("registry_git_blob_sha1") != fingerprint(raw):
            source_problems.append("continuity_fingerprint_does_not_match_registry")
        if state.get("mission") != "sustainable_generational_wealth":
            source_problems.append("continuity_mission_drift")
    except (OSError, ValueError, KeyError, TypeError):
        source_problems.append("continuity_state_unavailable_or_invalid")

    try:
        owner = json.loads((root / "automation_200/OWNER_CAPABILITY_CONTRACT.json").read_text(encoding="utf-8"))
        if owner.get("priority_order") != ["automation", "owner_priority_policy", "legitimate_finance", "parallel_other_projects"]:
            source_problems.append("priority_policy_drift")
        regressions = sorted(x.get("id", "unknown") for x in owner["capabilities"]
                             if x.get("status") == "regression_open")
    except (OSError, ValueError, KeyError, TypeError):
        source_problems.append("owner_capability_contract_unavailable_or_invalid")
        regressions = ["unknown"]

    source_problems.extend("prompt:" + x for x in prompt_audit(root))
    release = release_evaluate(evidence.get("release_gates", {}))
    gates_ok = all(x["status"] == "verified" for x in gates.values())
    clean_source = not source_problems
    ready = bool(clean_source and not regressions and release["release_ready"] and gates_ok)
    return {
        "schema": "cf0.restart_readiness.v1",
        "action": "READ_ONLY_NO_RESET",
        "intended_restart": "Non-destructive, owner-approved vNext cutover; preserve v1 and its rollback.",
        "cutover_ready": ready,
        "full_cf200_closure_ready": ready and completed == total,
        "verified_work_orders": completed,
        "target_work_orders": total,
        "source_consistent": clean_source,
        "source_problems": source_problems,
        "known_owner_capability_regressions": regressions,
        "release_gate": release,
        "restart_evidence_gates": gates,
        "notes": [
            "A completed work-order count is not proof of unattended HP operation.",
            "Even verified declarations here require independent examination of underlying evidence.",
            "No private archive is read, copied or modified by this report.",
            "Unfinished financial and creative branches are carried forward rather than deleted.",
            "Never reset CF-0, overwrite originals, cancel schedules or switch HP workers based on this report alone.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, help="Optional separately owner-reviewed public-safe gate declarations")
    parser.add_argument("--output", type=Path, help="Optional generated read-only report path")
    args = parser.parse_args()
    evidence = json.loads(args.evidence.read_text(encoding="utf-8")) if args.evidence else {}
    report = evaluate(evidence=evidence)
    serialized = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")


if __name__ == "__main__":
    main()
