"""CF-116: bounded expiry for independently verified task context hints.

Context is metadata for source-only scheduling, never an owner instruction or
permission. Missing contexts retain legacy behavior; expired and future-issued
contexts hold their tasks until an independently reviewed refresh.
"""
from __future__ import annotations

MAX_TIMESTAMP = 10**12
MAX_CONTEXT_LIFETIME = 90 * 24 * 60 * 60


def held_task_contexts(contexts, known_ids: set[str], now: int) -> dict[str, str]:
    if type(contexts) is not dict or type(now) is not int or not 0 <= now <= MAX_TIMESTAMP:
        raise ValueError("invalid_task_contexts")
    if len(contexts) > 200:
        raise ValueError("too_many_task_contexts")
    held = {}
    for task_id, record in contexts.items():
        if (type(task_id) is not str or task_id not in known_ids
                or type(record) is not dict or set(record) != {"created_at", "expires_at"}):
            raise ValueError("invalid_task_context")
        created, expires = record["created_at"], record["expires_at"]
        if (type(created) is not int or type(expires) is not int
                or not 0 <= created < expires <= MAX_TIMESTAMP
                or expires-created > MAX_CONTEXT_LIFETIME):
            raise ValueError("invalid_task_context_dates")
        if created > now:
            held[task_id] = "task_context_future_issued"
        elif now >= expires:
            held[task_id] = "task_context_expired"
    return held
