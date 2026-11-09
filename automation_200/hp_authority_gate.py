"""CF-119: cloud-side proof boundary for owner-HP work.

This is a *denial/diagnostic* boundary, not a credential issuer, signature
verifier, Windows task runner, or substitute for owner-local approval.
Public health, matched public receipts, overlapping scheduler timestamps, and
self-described owner approval cannot establish who controlled the HP.
No input accepted here can authorize a physical HP action.
"""
from __future__ import annotations

PUBLIC_HEALTH_STATES = frozenset({
    "not_published", "fresh_public_report", "reported_problem",
    "late", "stale", "future_timestamp", "invalid", "unavailable",
})
OWNER_LOCAL_EVIDENCE_IDS = frozenset({
    "CF-042", "CF-077", "CF-184", "CF-190", "CF-191", "CF-194",
})
SCHEMA = "cf0.hp_authority_proof_gate.v1"


def cloud_hold_reason(task: dict) -> str | None:
    """Return a cloud hold, or None for possible *source-work proposals*.

    Required physical evidence is not supplied by this function. In
    particular, None is NEVER authorization to operate an HP.
    """
    if type(task) is not dict:
        raise ValueError("invalid_hp_gate_task")
    tid, stream = task.get("id"), task.get("stream")
    if type(tid) is not str or not tid or type(stream) is not str or not stream:
        raise ValueError("invalid_hp_gate_identity")
    flag = task.get("physical_hp_required", False)
    if type(flag) is not bool:
        # Synthetic legacy tasks may omit the flag; a supplied invalid value
        # is always held rather than being coerced to False.
        return "invalid_hp_requirement"
    if flag:
        return "physical_hp_required"
    if stream == "hp_install":
        return "hp_install_needs_local_review"
    if tid in OWNER_LOCAL_EVIDENCE_IDS:
        return "owner_local_evidence_required"
    return None


def assess_public_proof(*, health_state: str,
                        receipt_digest_matched: bool = False,
                        scheduler_window_reported: bool = False,
                        owner_approval_claimed: bool = False) -> dict:
    """Describe evidence boundaries without granting any execution authority.

    Boolean claims are diagnostic inputs only. They are not authenticated,
    including when all three are True. Authoritative owner-local evidence
    requires a separately scoped trusted interface and owner-approved policy.
    """
    if type(health_state) is not str or health_state not in PUBLIC_HEALTH_STATES:
        raise ValueError("invalid_public_health_state")
    claims = (receipt_digest_matched, scheduler_window_reported, owner_approval_claimed)
    if any(type(x) is not bool for x in claims):
        raise ValueError("invalid_public_proof_claim")
    return {
        "schema": SCHEMA,
        "health_state": health_state,
        "public_receipt_digest_match_claimed": receipt_digest_matched,
        "scheduler_window_claimed": scheduler_window_reported,
        "owner_approval_claimed": owner_approval_claimed,
        "receipt_matching_proves_device_identity": False,
        "scheduler_overlap_proves_execution_origin": False,
        "public_claim_proves_owner_approval": False,
        "physical_hp_identity_attested": False,
        "owner_local_approval_verified": False,
        "hp_execution_authorized": False,
        "scope": "read_only_cloud_advisory",
        "unmet_proof": [
            "trusted_independent_hp_identity_and_scheduler_origin",
            "separate_authenticated_owner_local_opt_in",
            "approved_narrow_capability_and_rollback",
        ],
    }
