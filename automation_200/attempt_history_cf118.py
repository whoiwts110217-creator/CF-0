"""CF-118: deterministic, read-only replay of reviewed task attempt evidence.

This never executes/retries tasks, authenticates an owner, or establishes HP
origin. It converts separately reviewed, public-safe JSONL events into the
existing decision engine's capped failure inputs. Persisting or approving an
event is intentionally outside this module's authority.
"""
from __future__ import annotations
import json
from .decision_engine import propose, MAX_ATTEMPT_AGE

SCHEMA = "cf0.reviewed_attempt.v1"
RESULTS = frozenset({"failed", "verified_success"})
MAX_FAILURES = 10
MAX_LINES = 10000


def replay_reviewed_attempts(registry: dict, lines, *, now: int) -> dict:
    """Turn chronological reviewed JSONL into bounded, consecutive failures.

    Fields: schema, event_id, task_id, occurred_at (UTC epoch seconds),
    result, evidence_ref, reviewed. The reviewed flag is a caller assertion,
    not cryptographic proof. Evidence must be independently checked first.
    """
    if type(now) is not int or not 0 <= now <= MAX_ATTEMPT_AGE:
        raise ValueError("invalid time")
    if type(registry) is not dict or type(registry.get("tasks")) is not list:
        raise ValueError("invalid registry")
    ids = {t.get("id") for t in registry["tasks"] if type(t) is dict}
    if len(ids) != len(registry["tasks"]):
        raise ValueError("duplicate or invalid registry tasks")
    seen = set()
    attempts = {}
    previous_time = -1
    expected = {"schema", "event_id", "task_id", "occurred_at", "result", "evidence_ref", "reviewed"}
    for index, line in enumerate(lines):
        if index >= MAX_LINES:
            raise ValueError("too many attempt events")
        if type(line) is not str or not line.strip() or len(line) > 4096:
            raise ValueError("invalid attempt event line")
        try:
            row = json.loads(line)
        except (ValueError, TypeError) as exc:
            raise ValueError("invalid attempt event JSON") from exc
        if type(row) is not dict or set(row) != expected:
            raise ValueError("invalid attempt event fields")
        event_id, task_id = row["event_id"], row["task_id"]
        timestamp = row["occurred_at"]
        evidence = row["evidence_ref"]
        if (row["schema"] != SCHEMA or row["reviewed"] is not True
                or type(event_id) is not str or not 1 <= len(event_id) <= 128
                or event_id in seen or type(task_id) is not str or task_id not in ids
                or type(timestamp) is not int or not previous_time <= timestamp <= now
                or type(row["result"]) is not str or row["result"] not in RESULTS
                or type(evidence) is not str or not 1 <= len(evidence) <= 512
                or any(ord(c) < 33 or ord(c) > 126 for c in evidence)):
            raise ValueError("invalid or unreviewed attempt event")
        seen.add(event_id)
        previous_time = timestamp
        if row["result"] == "verified_success":
            attempts.pop(task_id, None)
        else:
            previous = attempts.get(task_id, {"failures": 0})
            attempts[task_id] = {"failures": min(MAX_FAILURES, previous["failures"] + 1), "failed_at": timestamp}
    return attempts


def propose_with_reviewed_attempts(registry: dict, lines, *, now: int, **options) -> dict:
    """Apply existing retry ceiling and cooldown; no file or HP writes."""
    if "attempts" in options:
        raise ValueError("attempts must come from reviewed events only")
    attempts = replay_reviewed_attempts(registry, lines, now=now)
    result = propose(registry, attempts=attempts, now=now, **options)
    result["attempt_history_source"] = "caller_supplied_reviewed_events"
    result["attempt_history_persisted_here"] = False
    return result
