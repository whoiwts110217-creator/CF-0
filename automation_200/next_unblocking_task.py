"""CF-117: identify the next safe source task that unblocks a target.

Read-only advisory. No owner consent, HP permissions, or task completion are
inferred from an eligible proposal. Blocked/hardware-only dependency chains
remain blocked rather than silently skipped.
"""
from __future__ import annotations

from .decision_engine import propose


def next_unblocking_task(registry, target_id: str, *, blocked_ids=()) -> dict:
    tasks = registry.get("tasks")
    if type(tasks) is not list or len(tasks) != 200:
        raise ValueError("invalid_registry")
    mapping = {t["id"]: t for t in tasks}
    if len(mapping) != len(tasks) or type(target_id) is not str or target_id not in mapping:
        raise ValueError("invalid_target_id")
    blocked = list(blocked_ids)
    if (len(blocked) != len(set(blocked))
            or any(type(x) is not str or x not in mapping for x in blocked)):
        raise ValueError("invalid_blocked_ids")
    visiting = set()
    ancestry = set()

    def traverse(task_id):
        if task_id in visiting:
            raise ValueError("dependency_cycle")
        if task_id in ancestry:
            return
        task = mapping[task_id]
        if task["status"] == "verified":
            return
        visiting.add(task_id)
        for parent in task["depends_on"]:
            if parent not in mapping:
                raise ValueError("missing_dependency")
            traverse(parent)
        visiting.remove(task_id)
        ancestry.add(task_id)

    traverse(target_id)
    blocked_for_selection = sorted(set(mapping) - ancestry | set(blocked))
    selection = propose(registry, limit=20, blocked_ids=blocked_for_selection)
    choices = selection["selected"]
    result = choices[0] if choices else None
    return {
        "schema": "cf0.next_unblocking_task.v1",
        "read_only": True,
        "execution_authorized": False,
        "target_id": target_id,
        "next": result,
        "candidate_count": len(choices),
        "blocked_or_owner_local": result is None and mapping[target_id]["status"] != "verified",
        "note": ("A cloud-safe source proposal, never a bypass for hardware-local evidence, "
                 "owner approvals, blocked tasks or unverified dependencies."),
    }
