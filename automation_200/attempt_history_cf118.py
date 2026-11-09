"""CF-118: join the existing local retry journal to read-only task proposals.

The authoritative failure journal is retry_evidence.py; do not create another
event format or scheduler. A hash chain detects accidental modification, not
authorship or task success. This adapter never retries, executes, writes, or
claims HP/cloud permission. It only supplies recorded failures to the
already-existing decision_engine's bounded cooldown and ceiling.
"""
from __future__ import annotations

from .decision_engine import MAX_ATTEMPT_AGE, propose
from .retry_evidence import read_events

SCHEMA = "cf0.retry_proposal_from_existing_journal.v1"


def propose_from_retry_journal(registry: dict, journal_path, *, now: int, **options) -> dict:
    """Read local failure evidence without mutation; reject ambiguity.

    The caller chooses an already-approved *local* path, not an arbitrary
    remotely supplied file or public URL. The journal is diagnostic; even a
    syntactically valid, hash-chained event is not authenticated HP evidence.
    """
    if type(now) is not int or not 0 <= now <= MAX_ATTEMPT_AGE:
        raise ValueError("invalid time")
    if type(registry) is not dict or type(registry.get("tasks")) is not list:
        raise ValueError("invalid registry")
    tasks = registry["tasks"]
    if any(type(t) is not dict or type(t.get("id")) is not str for t in tasks):
        raise ValueError("invalid task IDs")
    allowed_ids = {t["id"] for t in tasks}
    if len(allowed_ids) != len(tasks):
        raise ValueError("duplicate task IDs")
    if "attempts" in options:
        raise ValueError("attempts must come from the existing journal")
    events, attempts = read_events(journal_path, allowed_ids)
    # The decision engine rejects future timestamps and applies a fixed
    # three-failure ceiling. It emits proposals only, with no execution rights.
    result = propose(registry, now=now, attempts=attempts, **options)
    result["retry_journal_adapter_schema"] = SCHEMA
    result["retry_journal_event_count"] = len(events)
    result["retry_journal_last_digest"] = events[-1]["digest"] if events else None
    result["retry_journal_authenticated"] = False
    result["retry_journal_was_modified"] = False
    return result
