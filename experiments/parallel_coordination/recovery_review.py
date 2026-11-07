"""Pure, fail-closed review for interrupted CF-0 experiment claims.

This does not acquire/release claims, authorize work, verify registry entries,
or contact GitHub/HP. Input evidence must be independently authenticated.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RecoveryReview:
    disposition: str
    blockers: tuple[str, ...]
    automatic_retry_allowed: bool = False
    automatic_release_allowed: bool = False
    task_verified: bool = False


def review_interrupted_claim(
    *,
    expected_claim_sha: str,
    observed_claim_sha: str | None,
    expires_at: datetime,
    now: datetime,
    write_status: str,
    registry_status: str,
    receipts_accounted_for: bool,
    hp_required: bool = False,
    hp_schedule_proven: bool = False,
) -> RecoveryReview:
    """Classify only; a review is not a transaction or an owner approval.

    Receipt accounting must cover every action, including uncertain attempts.
    `COMPLETE` describes observed file states, not acceptance of a work order.
    """
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("timezone-aware now required")
    if expires_at.tzinfo is None or expires_at.utcoffset() is None:
        raise ValueError("timezone-aware expiry required")
    if not expected_claim_sha:
        raise ValueError("expected claim blob SHA required")
    if write_status not in {
        "COMPLETE", "NO_APPLIED_WRITES", "PARTIAL", "CONFLICT", "UNKNOWN"
    }:
        raise ValueError("unknown write status")
    if registry_status not in {"planned", "verified", "unknown"}:
        raise ValueError("unknown registry status")
    blockers: list[str] = []
    if observed_claim_sha is None:
        blockers.append("claim_not_observed")
    elif observed_claim_sha != expected_claim_sha:
        blockers.append("claim_changed_since_snapshot")
    if registry_status == "unknown":
        blockers.append("registry_not_verified_from_live_source")
    elif registry_status == "verified":
        blockers.append("task_already_verified_do_not_repeat")
    if not receipts_accounted_for:
        blockers.append("unreconciled_or_unknown_side_effects")
    if write_status in ("PARTIAL", "CONFLICT", "UNKNOWN"):
        blockers.append("incomplete_or_divergent_writes")
    elif write_status == "COMPLETE":
        blockers.append("completed_files_require_independent_acceptance")
    if hp_required and not hp_schedule_proven:
        blockers.append("physical_hp_evidence_missing")
    if now < expires_at:
        blockers.append("claim_not_expired")
    else:
        blockers.append("expiry_does_not_transfer_authority")
    disposition = (
        "HOLD_CONFLICT" if any(b in blockers for b in (
            "claim_not_observed", "claim_changed_since_snapshot", "incomplete_or_divergent_writes",
        )) else
        "HOLD_EVIDENCE" if any(b in blockers for b in (
            "registry_not_verified_from_live_source", "unreconciled_or_unknown_side_effects",
            "physical_hp_evidence_missing",
        )) else
        "REVIEW_REQUIRED"
    )
    return RecoveryReview(disposition, tuple(blockers))
