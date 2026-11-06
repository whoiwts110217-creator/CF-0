#!/usr/bin/env python3
"""Deterministic, read-only CF-200 task selection.

Owner priority: automation -> priority governance -> financial operations ->
other branches. Explicit owner task preferences may reorder *eligible* work
but cannot bypass dependencies, authorization or physical-HP evidence gates.
This program selects work; it never executes it or modifies the registry.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PRIORITY_ORDER = {
    "chat_command": 0, "hp_install": 0, "sidecar": 0,
    "receipt": 0, "security": 0, "real_operations": 0,
    "priority_logic": 1, "archive": 1,
    "public_finance": 2,
    "research": 3,
}

def eligible_tasks(registry: dict, *, blocked_ids=(), allow_hp_tasks=False):
    """Yield tasks with met dependencies; reject blocked and HP-only work by default."""
    tasks = registry["tasks"]
    mapping = {t["id"]: t for t in tasks}
    blocked = set(blocked_ids)
    for task in tasks:
        if task["status"] != "planned" or task["id"] in blocked:
            continue
        if task.get("physical_hp_required", False) and not allow_hp_tasks:
            continue
        if not all(mapping.get(parent, {}).get("status") == "verified" for parent in task["depends_on"]):
            continue
        yield task

def select_tasks(registry: dict, *, limit=4, blocked_ids=(), owner_preference_ids=(), allow_hp_tasks=False, waiting_cycles=None):
    """Optional bounded fairness: within the same tier, prefer eligible tasks waiting longer."""
    if waiting_cycles is None:
        waiting_cycles = {}
    if not isinstance(waiting_cycles, dict) or any(type(k) is not str or type(v) is not int or v < 0 or v > 100000 for k,v in waiting_cycles.items()):
        raise ValueError("waiting_cycles must map task IDs to bounded nonnegative integers")
    if any(k not in {t["id"] for t in registry["tasks"]} for k in waiting_cycles):
        raise ValueError("unknown waiting task ID")
    if type(limit) is not int or not 1 <= limit <= 20:
        raise ValueError("limit must be between 1 and 20")
    prefs = list(owner_preference_ids)
    if len(prefs) != len(set(prefs)):
        raise ValueError("duplicate owner preference IDs")
    all_ids = {t["id"] for t in registry["tasks"]}
    if any(p not in all_ids for p in prefs):
        raise ValueError("unknown owner preference ID")
    order = {task_id: pos for pos, task_id in enumerate(prefs)}
    def rank(task):
        id_ = task["id"]
        return (
            0 if id_ in order else 1,
            order.get(id_, len(prefs)),
            PRIORITY_ORDER.get(task["stream"], 4),
            -waiting_cycles.get(id_, 0),
            task["priority"],
            id_,
        )
    selected = sorted(
        eligible_tasks(registry, blocked_ids=blocked_ids, allow_hp_tasks=allow_hp_tasks),
        key=rank
    )[:limit]
    return [
        {"id":t["id"], "title":t["title"], "stream":t["stream"],
         "priority_tier":PRIORITY_ORDER.get(t["stream"], 4),
         "authority":t["authority"], "physical_hp_required":t["physical_hp_required"],
         "depends_on":t["depends_on"], "why":"owner_override" if t["id"] in order else "priority_and_dependencies"}
        for t in selected
    ]

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=4)
    parser.add_argument("--owner-preference", action="append", default=[], metavar="CF-ID")
    parser.add_argument("--waiting-cycles-json", default="{}", help="JSON object of task ID to completed waiting cycles; read-only")
    parser.add_argument("--blocked", action="append", default=[], metavar="CF-ID")
    parser.add_argument("--include-hp-only", action="store_true",
                        help="Show eligible HP-only tasks for human review; does not run or authorize them")
    args = parser.parse_args(argv)
    try:
        from automation_200.validate_registry import check_registry
    except ModuleNotFoundError:
        from validate_registry import check_registry
    waiting_cycles = json.loads(args.waiting_cycles_json)
    registry = json.loads((ROOT / "registry.json").read_text(encoding="utf-8"))
    check_registry(registry)
    print(json.dumps({"owner_priority_order":["automation","governance","finance","other"],
                      "read_only":True, "selected":select_tasks(
                          registry, limit=args.limit, blocked_ids=args.blocked,
                          owner_preference_ids=args.owner_preference,
                          allow_hp_tasks=args.include_hp_only, waiting_cycles=waiting_cycles)}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
