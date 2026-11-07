"""CF-115: evidence-gated conflict detection for structured owner directions.

This module never declares a raw GitHub issue, comment, or AI-generated record
to be an authenticated owner command. Callers must independently establish
authority before providing records. Opposing directions fail closed.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

VALID = {"prioritize", "block"}
TASK_ID = re.compile(r"CF-[0-9]{3}\Z")
RECORD_ID = re.compile(r"[A-Za-z0-9._-]{1,64}\Z")


def analyze(records: object, known_task_ids: set[str]) -> dict:
    if (type(records) is not list or len(records) > 100
            or type(known_task_ids) is not set
            or any(type(t) is not str or not TASK_ID.fullmatch(t) for t in known_task_ids)):
        raise ValueError("invalid_owner_direction_batch")
    seen = set()
    grouped: dict[str, list[dict]] = {}
    for record in records:
        if (type(record) is not dict
                or set(record) != {"id", "task_id", "decision", "authority_verified"}):
            raise ValueError("invalid_owner_direction_record")
        rid, tid, decision = record["id"], record["task_id"], record["decision"]
        if (type(rid) is not str or not RECORD_ID.fullmatch(rid)
                or rid in seen or type(tid) is not str or tid not in known_task_ids
                or decision not in VALID or record["authority_verified"] is not True):
            raise ValueError("unverified_or_invalid_owner_direction")
        seen.add(rid)
        grouped.setdefault(tid, []).append(record)
    conflicts = []
    blocked = []
    preferred = []
    for task_id in sorted(grouped):
        entries = grouped[task_id]
        decisions = {r["decision"] for r in entries}
        if decisions == VALID:
            conflicts.append({
                "task_id": task_id,
                "record_ids": sorted(r["id"] for r in entries),
                "status": "needs_owner_resolution",
            })
            blocked.append(task_id)
        elif decisions == {"block"}:
            blocked.append(task_id)
        elif decisions == {"prioritize"}:
            preferred.append(task_id)
    return {
        "schema": "cf0.owner_instruction_conflict.v1",
        "read_only": True,
        "authority_verified_externally": True,
        "conflicting_task_ids": [r["task_id"] for r in conflicts],
        "conflicts": conflicts,
        "blocked_ids": blocked,
        "preferred_ids": preferred,
        "owner_resolution_required": bool(conflicts),
        "note": "Conflict blocks the affected task. No timestamps or external comments implicitly resolve an owner dispute.",
    }


def main(argv=None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True,
                        help="Locally reviewed JSON records; never publish private owner messages")
    parser.add_argument("--registry", type=Path,
                        default=Path(__file__).with_name("registry.json"))
    args = parser.parse_args(argv)
    try:
        ids = {x["id"] for x in json.loads(args.registry.read_text(encoding="utf-8"))["tasks"]}
        decisions = json.loads(args.input.read_text(encoding="utf-8"))
        result = analyze(decisions, ids)
    except (OSError, UnicodeError, ValueError, TypeError, KeyError):
        print(json.dumps({"schema": "cf0.owner_instruction_conflict.v1",
                          "read_only": True, "error": "invalid_or_unavailable_input"}))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
