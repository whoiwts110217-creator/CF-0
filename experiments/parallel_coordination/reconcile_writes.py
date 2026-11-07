"""Classify observed partial multi-file writes without executing or retrying them.

The caller must independently fetch trustworthy current blob SHAs. A file not
observed at all is UNKNOWN, distinct from an observed missing file (None).
This is a diagnostic, not an atomic transaction, executor, or authorization.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class WriteIntent:
    path: str
    before_sha: str | None
    after_sha: str


@dataclass(frozen=True)
class Reconciliation:
    status: str
    applied: tuple[str, ...]
    untouched: tuple[str, ...]
    drifted: tuple[str, ...]
    unknown: tuple[str, ...]
    automatic_retry_allowed: bool = False


def reconcile_writes(
    intents: Sequence[WriteIntent],
    observed: Mapping[str, str | None],
) -> Reconciliation:
    """Fail closed on missing observations, partial commits and diverged files.

    SHA shape is intentionally not accepted as evidence of content, identity,
    authorization, or origin. The reader must validate source independently.
    """
    if not intents:
        raise ValueError("at least one write intent required")
    applied: list[str] = []
    untouched: list[str] = []
    drifted: list[str] = []
    unknown: list[str] = []
    seen: set[str] = set()
    for intent in intents:
        p = intent.path
        if (
            not p or p.startswith("/") or "\\" in p or "//" in p
            or any(part in ("", ".", "..") for part in p.split("/"))
            or p in seen
        ):
            raise ValueError("invalid or duplicate path")
        seen.add(p)
        if not isinstance(intent.after_sha, str) or not intent.after_sha:
            raise ValueError("after SHA required")
        if intent.before_sha is not None and (
            not isinstance(intent.before_sha, str) or not intent.before_sha
            or intent.before_sha == intent.after_sha
        ):
            raise ValueError("invalid or no-op before SHA")
        if p not in observed:
            unknown.append(p)
            continue
        current = observed[p]
        if current is not None and (not isinstance(current, str) or not current):
            raise ValueError("observed SHA must be a string or None")
        if current == intent.after_sha:
            applied.append(p)
        elif current == intent.before_sha:
            untouched.append(p)
        else:
            drifted.append(p)
    if unknown:
        status = "UNKNOWN"
    elif drifted:
        status = "CONFLICT"
    elif not untouched:
        status = "COMPLETE"
    elif not applied:
        status = "NO_APPLIED_WRITES"
    else:
        status = "PARTIAL"
    return Reconciliation(
        status, tuple(applied), tuple(untouched),
        tuple(drifted), tuple(unknown),
    )
