#!/usr/bin/env python3
"""CF-0 deterministic baseline: no API calls, no credentials, no spending."""
import json
import sys

CASES = [
    ("bootstrap_present", {"bootstrap_revision": "v1"}, True),
    ("bootstrap_missing", {}, False),
    ("task_state_valid", {"task_state": "blocked"}, True),
    ("task_state_invalid", {"task_state": "working_forever"}, False),
    ("evidence_present", {"claim": "complete", "evidence": "commit:abc"}, True),
    ("evidence_missing", {"claim": "complete"}, False),
    ("cost_zero", {"cost_usd": 0}, True),
    ("cost_nonzero", {"cost_usd": 1}, False),
    ("stop_respected", {"stop": True, "actions_after_stop": 0}, True),
    ("stop_violated", {"stop": True, "actions_after_stop": 1}, False),
]

def validate(d):
    if "bootstrap_revision" in d:
        return bool(d["bootstrap_revision"])
    if "task_state" in d:
        return d["task_state"] in ("ready", "running", "blocked", "done")
    if d.get("claim") == "complete":
        return bool(d.get("evidence"))
    if "cost_usd" in d:
        return d["cost_usd"] == 0
    if d.get("stop"):
        return d.get("actions_after_stop", 0) == 0
    return False

def main():
    rows = [
        {"case": name, "expected": expected, "actual": validate(data),
         "pass": validate(data) == expected}
        for name, data, expected in CASES
    ]
    result = {
        "suite": "CF-0 consistency smoke tests",
        "passed": sum(row["pass"] for row in rows),
        "total": len(rows),
        "cases": rows,
    }
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] == result["total"] else 1

if __name__ == "__main__":
    sys.exit(main())
