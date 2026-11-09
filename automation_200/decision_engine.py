#!/usr/bin/env python3
"""CF-200 evidence-gated decision proposal, not an executor.

Deterministically select eligible tasks using the founder's existing P0/P1/P2/P3
selector. A missing HP heartbeat or a public receipt never grants HP authority.
No writes, network commands to the HP, registry completion, or task execution.
"""
from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from pathlib import Path

try:
    from .priority_selector import select_tasks
    from .validate_registry import check_registry
    from .task_context_expiry import held_task_contexts
    from .hp_authority_gate import cloud_hold_reason, assess_public_proof, OWNER_LOCAL_EVIDENCE_IDS
except ImportError:
    from priority_selector import select_tasks
    from validate_registry import check_registry
    from task_context_expiry import held_task_contexts
    from hp_authority_gate import cloud_hold_reason, assess_public_proof, OWNER_LOCAL_EVIDENCE_IDS

ROOT = Path(__file__).resolve().parent
POLICY = "cf200.decision_proposal.v1"
HEALTH_STATES = frozenset({
    "not_published", "fresh_public_report", "reported_problem",
    "late", "stale", "future_timestamp", "invalid", "unavailable",
})
RETRY_LIMIT = 3
RETRY_BASE_SECONDS = 300
MAX_ATTEMPT_AGE = 10**12

def _attempts_valid(registry, attempts):
    ids = {t["id"] for t in registry["tasks"]}
    if not isinstance(attempts, dict):
        raise ValueError("attempts must be an object")
    for task_id, attempt in attempts.items():
        if type(task_id) is not str or task_id not in ids:
            raise ValueError("unknown attempt task")
        if not isinstance(attempt, dict) or set(attempt) != {"failures", "failed_at"}:
            raise ValueError("invalid attempt record")
        count, stamp = attempt["failures"], attempt["failed_at"]
        if (type(count) is not int or not 1 <= count <= 10
                or type(stamp) is not int or not 0 <= stamp <= MAX_ATTEMPT_AGE):
            raise ValueError("invalid attempt values")


def propose(registry, *, health_state="unavailable", now=None, limit=4,
            blocked_ids=(), owner_preference_ids=(), attempts=None,
            task_contexts=None):
    """Produce a cloud-safe proposal; fail closed on malformed owner inputs.

    The registry's physical_hp_required bit is necessary but not sufficient.
    The entire hp_install stream requires actual owner-local confirmation,
    including early items still tagged false for physical_hp_required.
    """
    if type(health_state) is not str or health_state not in HEALTH_STATES:
        raise ValueError("unknown HP health state")
    if now is None:
        now = int(time.time())
    if type(now) is not int or not 0 <= now <= MAX_ATTEMPT_AGE:
        raise ValueError("invalid time")
    if attempts is None:
        attempts = {}
    _attempts_valid(registry, attempts)
    # Future-dated failure evidence can hold tasks indefinitely. Reject it
    # rather than silently treating an unverified clock value as a cooldown.
    if any(attempt["failed_at"] > now for attempt in attempts.values()):
        raise ValueError("attempt timestamp is in the future")
    ids = {task["id"] for task in registry["tasks"]}
    # Validate types before deduplication: an unhashable list/dict in an
    # external proposal input must fail closed with a controlled ValueError.
    try:
        explicit_blocked = list(blocked_ids)
    except TypeError as exc:
        raise ValueError("invalid blocked task IDs") from exc
    if (any(type(x) is not str or x not in ids for x in explicit_blocked)
            or len(explicit_blocked) != len(set(explicit_blocked))):
        raise ValueError("invalid blocked task IDs")
    if task_contexts is None:
        task_contexts = {}
    context_holds = held_task_contexts(task_contexts, ids, now)
    reasons = {}
    status = {t["id"]: t["status"] for t in registry["tasks"]}
    for task in registry["tasks"]:
        tid = task["id"]
        if task["status"] != "planned":
            continue
        if tid in explicit_blocked:
            reasons[tid] = "explicitly_blocked"
        elif tid in context_holds:
            reasons[tid] = context_holds[tid]
        elif (hp_hold := cloud_hold_reason(task)) is not None:
            reasons[tid] = hp_hold
        elif not all(status.get(d) == "verified" for d in task["depends_on"]):
            reasons[tid] = "dependencies_unverified"
        elif tid in attempts:
            record = attempts[tid]
            if record["failures"] >= RETRY_LIMIT:
                reasons[tid] = "retry_limit_reached"
            elif now < record["failed_at"] + RETRY_BASE_SECONDS * (2 ** (record["failures"] - 1)):
                reasons[tid] = "retry_cooldown"
    selected = select_tasks(
        registry, limit=limit, blocked_ids=list(reasons),
        owner_preference_ids=owner_preference_ids,
        allow_hp_tasks=False,
    )
    for item in selected:
        item["action"] = "propose_source_work_only"
        item["decision_basis"] = "founder_explicit_priority" if item["why"] == "owner_override" else "founder_tier_dependencies"
    counts = dict(sorted(Counter(reasons.values()).items()))
    # Include only bounded identifiers, not external files or untrusted descriptions.
    held_examples = [{"id":tid, "reason":reason} for tid, reason in sorted(reasons.items())[:10]]
    return {
        "schema": POLICY,
        "read_only": True,
        "execution_authorized": False,
        "owner_priority_order": ["automation", "governance", "finance", "other"],
        "hp_health_state": health_state,
        "hp_identity_attested": False,
        "hp_proof_gate": assess_public_proof(health_state=health_state),
        "selected": selected,
        "held_counts": counts,
        "held_examples": held_examples,
        "selected_count": len(selected),
        "policy_note": (
            "Cloud-only proposals: HP installation, owner-local evidence, and physical-HP tasks are held "
            "regardless of public heartbeat freshness. Failure retry state is input, "
            "not automatically inferred or persisted."
        ),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=4)
    parser.add_argument("--health-state", choices=sorted(HEALTH_STATES), default="unavailable")
    parser.add_argument("--live", action="store_true",
                        help="Read the fixed public HP report, do not run HP commands.")
    parser.add_argument("--blocked", action="append", default=[])
    parser.add_argument("--owner-preference", action="append", default=[])
    parser.add_argument("--attempts-json", default="{}",
                        help="Explicit public-safe failures/failed_at map. No state writes.")
    parser.add_argument("--task-contexts-json", default="{}",
                        help="Optional reviewed ID to created_at/expires_at map; old/unknown contexts are not execution authorization.")
    args = parser.parse_args(argv)
    registry = json.loads((ROOT / "registry.json").read_text(encoding="utf-8"))
    check_registry(registry)
    health = args.health_state
    if args.live:
        # Import only on live use; CI offline tests remain network-free.
        from relay.health_watch import watch
        health = watch()["state"]
    result = propose(
        registry, health_state=health, now=int(time.time()), limit=args.limit,
        blocked_ids=args.blocked, owner_preference_ids=args.owner_preference,
        attempts=json.loads(args.attempts_json),
        task_contexts=json.loads(args.task_contexts_json),
    )
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
