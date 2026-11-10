#!/usr/bin/env python3
"""Source-level evidence gate for CF-0 skill evolution. stdlib only; NO code execution.

This tool reads local documents, validates evidence structure, compares hashes,
and writes a bounded decision report. It does not edit repos or install skills.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

MAX_FILE = 1_000_000
MAX_EVIDENCE = 64_000
GATES = ("owner_authority_unchanged", "privacy_preserved", "capabilities_preserved", "continuity_complete")
KINDS = {"normal", "ambiguous", "failure"}
VOTES = {"better", "worse", "tie"}
ORDERS = {"baseline_first", "candidate_first"}


def fail(msg):
    raise ValueError(msg)


def read_bytes(path, limit=MAX_FILE):
    p = Path(path)
    if not p.is_file():
        fail(f"missing file: {p}")
    if p.stat().st_size > limit:
        fail(f"file too large: {p}")
    return p.read_bytes()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def evidence_file(path):
    raw = read_bytes(path, MAX_EVIDENCE)
    try:
        o = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as e:
        fail(f"invalid JSON evidence: {e}")
    if not isinstance(o, dict):
        fail("evidence must be an object")
    return o, sha256(raw)


def evaluate(baseline_path, candidate_path, evidence_path):
    base = read_bytes(baseline_path)
    cand = read_bytes(candidate_path)
    evidence, evidence_sha = evidence_file(evidence_path)
    reasons = []
    decision = "needs_evidence"
    # Bind claimed experiment evidence to the exact SKILL.md bytes under evaluation.
    # Matching hashes do not authenticate who executed tests or wrote the claims.
    actual_base = sha256(base)
    actual_cand = sha256(cand)
    valid_digest = lambda v: isinstance(v, str) and len(v) == 64 and all(k in "0123456789abcdef" for k in v)
    supplied_base = evidence.get("baseline_sha256")
    supplied_cand = evidence.get("candidate_sha256")
    hashes_supplied = valid_digest(supplied_base) and valid_digest(supplied_cand)
    hashes_match = hashes_supplied and supplied_base == actual_base and supplied_cand == actual_cand
    if not hashes_supplied:
        reasons.append("missing or malformed version-bound SHA-256 evidence (64 lowercase hex chars required)")
    elif not hashes_match:
        reasons.append("evidence references different baseline/candidate file bytes")
        decision = "reject"
    if evidence.get("synthetic") is True:
        reasons.append("synthetic evidence cannot establish a real skill gain")
    hard_gates = evidence.get("hard_gates", {})
    if not isinstance(hard_gates, dict):
        fail("hard_gates must be an object")
    unknown_gates = sorted(set(hard_gates) - set(GATES))
    if unknown_gates:
        reasons.append("unknown hard gates are not authority: " + ",".join(unknown_gates))
    bad = [g for g in GATES if hard_gates.get(g) is False]
    missing = [g for g in GATES if hard_gates.get(g) is not True and g not in bad]
    if bad:
        reasons.append("explicit hard gate failure: " + ",".join(bad))
        decision = "reject"
    if missing:
        reasons.append("missing explicit true gate(s): " + ",".join(missing))
    if base == cand:
        reasons.append("baseline and candidate bytes are identical")
        decision = "reject"

    runs = evidence.get("test_runs", [])
    if not isinstance(runs, list):
        fail("test_runs must be a list")
    ids = set()
    kinds = set()
    regressions = []
    improvements = []
    bad_tests = []
    for row in runs:
        if not isinstance(row, dict):
            bad_tests.append("non-object test row")
            continue
        tid = row.get("id")
        kind = row.get("kind")
        if not isinstance(tid, str) or not tid.strip() or tid in ids:
            bad_tests.append("missing/duplicate test id")
            continue
        ids.add(tid)
        if kind not in KINDS:
            bad_tests.append(f"{tid}: invalid kind")
            continue
        kinds.add(kind)
        if row.get("mode") != "full_test":
            bad_tests.append(f"{tid}: not a real full_test")
        for label in ("baseline_pass", "candidate_pass"):
            if type(row.get(label)) is not bool:
                bad_tests.append(f"{tid}: missing boolean {label}")
        for label in ("baseline_output_ref", "candidate_output_ref"):
            if not isinstance(row.get(label), str) or not row.get(label).strip():
                bad_tests.append(f"{tid}: missing {label}")
        if type(row.get("baseline_pass")) is bool and type(row.get("candidate_pass")) is bool:
            if row["baseline_pass"] and not row["candidate_pass"]:
                regressions.append(tid)
            if not row["baseline_pass"] and row["candidate_pass"]:
                improvements.append(tid)
    if len(ids) < 3 or kinds != KINDS:
        bad_tests.append("need distinct normal, ambiguous and failure tests")
    if bad_tests:
        reasons.append("test evidence inadequate: " + "; ".join(bad_tests))
    if regressions:
        reasons.append("regression on previously passing tests: " + ",".join(regressions))
        decision = "reject"
    if not improvements:
        reasons.append("no observed improvement over passing baseline")

    judges = evidence.get("judges", [])
    if not isinstance(judges, list):
        fail("judges must be a list")
    judge_ids = set()
    invalid_judges = []
    votes = {v: 0 for v in VOTES}
    orders = set()
    for row in judges:
        if not isinstance(row, dict):
            invalid_judges.append("non-object judge")
            continue
        jid = row.get("id")
        vote = row.get("vote")
        order = row.get("order")
        reason = row.get("reason")
        if not isinstance(jid, str) or not jid.strip() or jid in judge_ids:
            invalid_judges.append("missing/duplicate judge id")
            continue
        judge_ids.add(jid)
        if vote not in VOTES or order not in ORDERS or not isinstance(reason, str) or not reason.strip():
            invalid_judges.append(f"{jid}: vote/order/reason incomplete")
            continue
        votes[vote] += 1
        orders.add(order)
    if len(judge_ids) < 3 or len(judge_ids) % 2 == 0 or invalid_judges or len(orders) < 2:
        reasons.append("need odd >=3 distinct judges with counterbalanced order and reasons; " + ",".join(invalid_judges))
    if votes["better"] <= len(judge_ids) // 2:
        reasons.append("no majority of explicit better votes (ties are not approvals)")

    if decision != "reject" and not (evidence.get("synthetic") is True or not hashes_match or unknown_gates or missing or bad_tests or not improvements or len(judge_ids) < 3
                    or len(judge_ids) % 2 == 0 or invalid_judges or len(orders) < 2
                    or votes["better"] <= len(judge_ids) // 2):
        decision = "owner_review_required"
        reasons.append("eligible for human review; not automatically approved for deployment")

    return {
        "schema": "cf0.skill_evolution_gate.v1",
        "experiment_id": evidence.get("experiment_id", "unidentified"),
        "decision": decision,
        "evidence_level": "source-level evidence validation only; tests/judges not independently authenticated",
        "baseline_sha256": actual_base,
        "hashes_match": bool(hashes_match),
        "candidate_sha256": actual_cand,
        "evidence_sha256": evidence_sha,
        "distinct_versions": base != cand,
        "test_count": len(ids),
        "improvements": improvements,
        "regressions": regressions,
        "judge_votes": votes,
        "reasons": reasons,
        "publishing_authorized": False,
        "hp_control_authorized": False,
        "finance_authorized": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", help="Immutable before-SKILL.md path")
    parser.add_argument("candidate", help="Candidate SKILL.md path")
    parser.add_argument("evidence", help="Evidence JSON (same test IDs + independent paired judge votes)")
    parser.add_argument("--out", help="Write result JSON only if destination does not already exist")
    args = parser.parse_args(argv)
    try:
        report = evaluate(args.baseline, args.candidate, args.evidence)
        payload = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        if args.out:
            path = Path(args.out)
            with path.open("x", encoding="utf-8") as f:
                f.write(payload)
        print(payload, end="")
        return 0 if report["decision"] == "owner_review_required" else 2
    except (ValueError, OSError) as err:
        print(f"GATE_ERROR: {err}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
