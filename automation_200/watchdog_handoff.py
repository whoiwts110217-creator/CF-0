"""Assemble a public CF-0 Work handoff from one watchdog run's pinned reads."""
from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from relay.channel_audit import MAX_FILES, REPO

from .decision_engine import HEALTH_STATES, ROOT, propose
from .validate_registry import check_registry

QUEUE_COUNTS = (
    "matching_execution_receipts", "pending_requests", "expired_without_receipt",
    "invalid_requests", "mismatched_receipts", "writeback_setup_probes", "orphan_receipts",
)
MAX_INPUT_BYTES = 16_384


def read_report(path: Path) -> dict:
    """An unavailable step or malformed file is missing evidence."""
    try:
        with path.open("rb") as handle:
            raw = handle.read(MAX_INPUT_BYTES + 1)
        if len(raw) <= MAX_INPUT_BYTES:
            report = json.loads(raw)
            if isinstance(report, dict):
                return report
    except (OSError, ValueError, RecursionError):
        pass
    return {}


def build_handoff(registry, queue, health, *, commit, event, now):
    """Project allowlisted facts and task IDs, never raw reports or authority."""
    check_registry(registry)
    queue_summary = {"state": "unavailable"}
    if (queue.get("source_commit") == commit and queue.get("audit") == "read_only"
            and queue.get("repo") == REPO):
        counts = {name: queue.get(name) for name in QUEUE_COUNTS}
        if all(type(count) is int and 0 <= count <= MAX_FILES for count in counts.values()):
            queue_summary = {"state": "read_only", **counts}
    health_state = health.get("state")
    if (health.get("source_commit") != commit
            or health.get("monitor") != "cf0.hp_health.read_only.v1"
            or not isinstance(health_state, str) or health_state not in HEALTH_STATES):
        health_state = "unavailable"
    proposal = propose(registry, health_state=health_state, now=now)
    return {
        "schema": "cf0.work_handoff.v1",
        "source_commit": commit,
        "watchdog_event": event,
        "assembled_utc": datetime.fromtimestamp(now, timezone.utc).isoformat(),
        "registry": {"verified": registry["completed"], "target": registry["target"]},
        "public_queue": queue_summary,
        "hp": {"health_state": health_state, "identity_attested": False,
               "scheduled_receipt_origin": "unverified"},
        "next_source_proposals": [item["id"] for item in proposal["selected"]],
        "execution_authorized": False,
    }, proposal


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--health", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--event", choices=("push", "schedule", "workflow_dispatch"), required=True)
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[0-9a-f]{40}", args.commit):
        parser.error("--commit must be a 40-character lowercase Git SHA")
    registry = json.loads((ROOT / "registry.json").read_text(encoding="utf-8"))
    handoff, proposal = build_handoff(
        registry, read_report(args.queue), read_report(args.health),
        commit=args.commit, event=args.event, now=int(time.time()),
    )
    print(json.dumps(proposal, sort_keys=True, indent=2))
    print("CF0_WORK_HANDOFF=" + json.dumps(handoff, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
