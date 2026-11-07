"""Pure, side-effect-free checks for parallel CF-0 operator proposals.

These checks are advisory preconditions, not GitHub atomic locks. Recheck
the expected blob SHA at the actual remote write boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping


class ConflictError(ValueError):
    """The proposal cannot safely proceed against observed state."""


@dataclass(frozen=True)
class Claim:
    task_id: str
    operator_id: str
    base_sha: str
    paths: tuple[str, ...]
    expires_at: datetime

    def __post_init__(self) -> None:
        if not self.task_id or not self.operator_id or not self.base_sha:
            raise ValueError("claim identity and base SHA required")
        if not self.paths or any(not p or p.startswith("/") or ".." in p.split("/") for p in self.paths):
            raise ValueError("safe relative paths required")
        if len(set(self.paths)) != len(self.paths):
            raise ValueError("duplicate paths")
        if self.expires_at.tzinfo is None or self.expires_at.utcoffset() is None:
            raise ValueError("timezone-aware expiry required")


def validate_proposal(
    claim: Claim,
    *,
    current_sha: str,
    now: datetime,
    active_claims: tuple[Claim, ...] = (),
    verified_task_ids: frozenset[str] = frozenset(),
) -> None:
    """Reject stale, overlapping or already-completed work; never execute writes.

    This is a local safety filter. Two independent operators can still race
    between this check and a remote write; GitHub SHA/branch protection must
    enforce the final mutation.
    """
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("timezone-aware now required")
    if claim.expires_at <= now:
        raise ConflictError("expired_claim")
    if claim.base_sha != current_sha:
        raise ConflictError("stale_source")
    if claim.task_id in verified_task_ids:
        raise ConflictError("already_verified")
    for other in active_claims:
        if other.operator_id == claim.operator_id and other.task_id == claim.task_id:
            continue
        if other.expires_at <= now:
            continue
        if other.task_id == claim.task_id:
            raise ConflictError("task_claimed")
        if set(other.paths).intersection(claim.paths):
            raise ConflictError("path_claimed")


def require_unique_receipt(
    action_id: str, receipt_index: Mapping[str, str]
) -> None:
    """Fail closed on a known idempotency key; caller owns durable storage."""
    if not action_id:
        raise ValueError("action ID required")
    if action_id in receipt_index:
        raise ConflictError("action_already_recorded")
