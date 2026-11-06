#!/usr/bin/env python3
"""Conservative, read-only CF-0 public-release gate report.

A file existing is not proof that a capability works. Every operational gate
requires an explicit evidence record; unknown and unverified are NOT passed.
"""
import argparse
import json
from pathlib import Path

GATES = (
    "unattended_execution",
    "hp_end_to_end_recovery",
    "idempotency_dependencies_retries",
    "priority_policy_tests",
    "security_review",
    "clean_install",
    "license_docs_samples",
    "versioned_release_evidence",
)
ALLOWED = {"verified", "blocked", "unverified"}

def evaluate(evidence):
    if not isinstance(evidence, dict):
        raise ValueError("evidence must be a JSON object")
    unknown = set(evidence) - set(GATES)
    if unknown:
        raise ValueError("unknown gates: " + ", ".join(sorted(unknown)))
    result = {}
    for gate in GATES:
        entry = evidence.get(gate, {"status": "unverified"})
        if not isinstance(entry, dict) or entry.get("status") not in ALLOWED:
            raise ValueError("invalid gate status: " + gate)
        status = entry["status"]
        refs = entry.get("evidence", [])
        if not isinstance(refs, list) or any(not isinstance(x, str) or not x.strip() for x in refs):
            raise ValueError("invalid evidence references: " + gate)
        if status == "verified" and not refs:
            raise ValueError("verified gate lacks evidence: " + gate)
        result[gate] = {"status": status, "evidence": refs}
    return {
        "release_ready": all(x["status"] == "verified" for x in result.values()),
        "verified_count": sum(x["status"] == "verified" for x in result.values()),
        "total_gates": len(GATES),
        "gates": result,
        "note": "Evidence references are declarations, not independently authenticated by this script.",
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, help="Optional reviewed evidence JSON; omit for conservative unknowns")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    evidence = json.loads(args.evidence.read_text(encoding="utf-8")) if args.evidence else {}
    report = evaluate(evidence)
    serialized = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
