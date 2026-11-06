#!/usr/bin/env python3
"""Bounded, auditable waiting-cycle state for the read-only CF-200 selector.

Explicitly invoked by an operator; never runs HP commands or marks tasks verified.
State is public-safe: task IDs and integer counters only.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
try:
    from automation_200.priority_selector import eligible_tasks, select_tasks
except ModuleNotFoundError:
    from priority_selector import eligible_tasks, select_tasks

MAX_WAIT = 100000

def advance(registry, previous, selected_ids, *, blocked_ids=()):
    ids = {t["id"] for t in registry["tasks"]}
    if not isinstance(previous, dict) or any(
        type(k) is not str or k not in ids or type(v) is not int or not 0 <= v <= MAX_WAIT
        for k, v in previous.items()
    ):
        raise ValueError("invalid waiting-cycle state")
    if len(selected_ids) != len(set(selected_ids)) or any(x not in ids for x in selected_ids):
        raise ValueError("invalid selection")
    eligible = {t["id"] for t in eligible_tasks(registry, blocked_ids=blocked_ids)}
    if not set(selected_ids) <= eligible:
        raise ValueError("selected task is not eligible")
    result = {}
    for task in registry["tasks"]:
        tid = task["id"]
        if tid in eligible:
            result[tid] = 0 if tid in selected_ids else min(MAX_WAIT, previous.get(tid, 0) + 1)
    return result

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--state", required=True, type=Path)
    p.add_argument("--registry", type=Path, default=Path(__file__).with_name("registry.json"))
    p.add_argument("--limit", type=int, default=4)
    p.add_argument("--blocked", action="append", default=[])
    p.add_argument("--owner-preference", action="append", default=[])
    p.add_argument("--write", action="store_true", help="Explicitly persist counters, not registry")
    args = p.parse_args(argv)
    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    previous = json.loads(args.state.read_text(encoding="utf-8")) if args.state.exists() else {}
    selected = select_tasks(registry, limit=args.limit, blocked_ids=args.blocked,
                            owner_preference_ids=args.owner_preference, waiting_cycles=previous)
    next_state = advance(registry, previous, [x["id"] for x in selected], blocked_ids=args.blocked)
    if args.write:
        args.state.parent.mkdir(parents=True, exist_ok=True)
        temp = args.state.with_suffix(args.state.suffix + ".tmp")
        temp.write_text(json.dumps(next_state, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        temp.replace(args.state)
    print(json.dumps({"selected": selected, "next_waiting_cycles": next_state, "persisted": args.write}, indent=2))

if __name__ == "__main__":
    main()
