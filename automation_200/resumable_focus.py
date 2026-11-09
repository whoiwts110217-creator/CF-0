"""CF-0 resumable task-focus proposals: no task execution or HP access.

Wraps the existing evidence-gated decision engine. A switch cannot silently
discard unfinished active work: it requires a recoverable checkpoint reference.
State is private-local by default, never published to the public repository.
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile
import time
from copy import deepcopy
from pathlib import Path

from .decision_engine import HEALTH_STATES, propose
from .validate_registry import check_registry

SCHEMA = "cf200.resumable_focus.v1"
MAX_REF = 240


def _ref(value):
    return (value is None or
            (type(value) is str and 0 < len(value) <= MAX_REF
             and all(ord(ch) >= 32 and ord(ch) != 127 for ch in value)))


def _check_state(state, ids):
    if type(state) is not dict or set(state) != {"schema", "active", "paused"}:
        raise ValueError("invalid_handoff_state")
    if state["schema"] != SCHEMA or type(state["paused"]) is not list:
        raise ValueError("invalid_handoff_schema")
    if len(state["paused"]) > len(ids):
        raise ValueError("too_many_paused_tasks")
    active = state["active"]
    if active is not None:
        if (type(active) is not dict or set(active) != {"task_id", "checkpoint_ref"}
                or active["task_id"] not in ids or not _ref(active["checkpoint_ref"])):
            raise ValueError("invalid_active_task")
    seen = {active["task_id"]} if active is not None else set()
    for item in state["paused"]:
        if (type(item) is not dict or set(item) != {"task_id", "checkpoint_ref"}
                or type(item["task_id"]) is not str or item["task_id"] not in ids
                or item["task_id"] in seen or not _ref(item["checkpoint_ref"])
                or item["checkpoint_ref"] is None):
            raise ValueError("invalid_paused_task")
        seen.add(item["task_id"])


def default_state():
    return {"schema": SCHEMA, "active": None, "paused": []}


def plan_handoff(registry, decision, state=None, *, checkpoint_ref=None):
    """Pure, deterministic state proposal. Not execution/verification."""
    tasks = {t["id"]: t for t in registry["tasks"]}
    if state is None:
        state = default_state()
    _check_state(state, set(tasks))
    if not _ref(checkpoint_ref):
        raise ValueError("invalid_checkpoint_ref")
    if (type(decision) is not dict or decision.get("schema") != "cf200.decision_proposal.v1"
            or decision.get("read_only") is not True or
            decision.get("execution_authorized") is not False
            or type(decision.get("selected")) is not list):
        raise ValueError("untrusted_decision")
    chosen = decision["selected"][0] if decision["selected"] else None
    selected = decision["selected"]
    for item in selected:
        if (type(item) is not dict or item.get("id") not in tasks
                or type(item.get("priority_tier")) is not int):
            raise ValueError("invalid_decision_candidate")
    active = state["active"]
    if active is not None and checkpoint_ref is not None:
        active = {**active, "checkpoint_ref": checkpoint_ref}
    if active is not None and chosen is not None:
        current = next((x for x in selected if x["id"] == active["task_id"]), None)
        # Avoid churn within a tier. Explicit owner priority and genuinely
        # higher-tier work still preempt this sticky selection.
        if (current is not None and current["priority_tier"] <= chosen["priority_tier"]
                and not (chosen["why"] == "owner_override"
                         and chosen["id"] != active["task_id"])):
            chosen = current
    desired = chosen["id"] if chosen is not None else None
    current_id = active["task_id"] if active else None
    next_state = deepcopy(state)
    if current_id == desired:
        next_state["active"] = active
        transition = "continue" if active else "idle"
    elif active is not None and tasks[current_id]["status"] == "planned" and active["checkpoint_ref"] is None:
        return {
            "schema": SCHEMA, "read_only_proposal": True,
            "execution_authorized": False, "ready": False,
            "transition": "checkpoint_required", "current_id": current_id,
            "proposed_next_id": desired, "next_state": deepcopy(state),
            "alternatives": [x["id"] for x in selected[:4]],
            "note": "Save a private checkpoint and supply its reference before switching unfinished work.",
        }
    else:
        paused = deepcopy(state["paused"])
        if active is not None and tasks[current_id]["status"] == "planned":
            paused.append({"task_id": current_id, "checkpoint_ref": active["checkpoint_ref"]})
        resumed = next((p for p in paused if p["task_id"] == desired), None)
        if resumed:
            paused = [p for p in paused if p["task_id"] != desired]
        next_state["paused"] = paused
        next_state["active"] = (
            {"task_id": desired, "checkpoint_ref": resumed["checkpoint_ref"] if resumed else None}
            if desired else None
        )
        transition = ("resume" if resumed else "switch" if active else
                      "start" if desired else "idle")
    return {
        "schema": SCHEMA, "read_only_proposal": True, "execution_authorized": False,
        "ready": True, "transition": transition, "current_id": current_id,
        "proposed_next_id": desired, "next_state": next_state,
        "alternatives": [x["id"] for x in selected[:4]],
        "note": "A checkpoint reference tracks context; it does not prove the task was executed.",
    }


def save_local_state(path, state):
    """Explicit opt-in persistence, atomic replacement, no network or public push."""
    path = Path(path)
    if path.is_symlink():
        raise ValueError("refuse_symlink_state_file")
    if not path.parent.is_dir():
        raise ValueError("state_directory_missing")
    fd, temporary = tempfile.mkstemp(prefix=".cf0-handoff-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(state, out, sort_keys=True, indent=2)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-file", help="Local private JSON state; not a public GitHub file")
    parser.add_argument("--apply", action="store_true", help="Atomically save ready state locally")
    parser.add_argument("--checkpoint-ref", help="Existing private, durable checkpoint reference")
    parser.add_argument("--owner-preference", action="append", default=[])
    parser.add_argument("--blocked", action="append", default=[])
    parser.add_argument("--health-state", choices=sorted(HEALTH_STATES), default="unavailable")
    args = parser.parse_args(argv)
    if args.apply and not args.state_file:
        parser.error("--apply requires --state-file")
    root = Path(__file__).resolve().parent
    registry = json.loads((root / "registry.json").read_text(encoding="utf-8"))
    check_registry(registry)
    state_path = Path(args.state_file) if args.state_file else None
    state = (json.loads(state_path.read_text(encoding="utf-8"))
             if state_path is not None and state_path.exists() else default_state())
    plan = propose(registry, now=int(time.time()), limit=20,
                   owner_preference_ids=args.owner_preference, blocked_ids=args.blocked,
                   health_state=args.health_state)
    result = plan_handoff(registry, plan, state, checkpoint_ref=args.checkpoint_ref)
    if args.apply and result["ready"]:
        save_local_state(state_path, result["next_state"])
    result["state_saved_locally"] = bool(args.apply and result["ready"])
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["ready"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
