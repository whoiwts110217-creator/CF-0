"""Build bounded, deterministic GitHub create-only claim requests; no I/O.

A successful create-only write may establish an exclusive path in one branch.
It does NOT establish that a worker is alive, an action is authorized, or a
claim can be recycled when its deadline passes. Reconciliation is manual.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import re

from parallel_guard import Claim, ConflictError

_TASK_ID = re.compile(r"CF-(?:0(?:0[1-9]|[1-9][0-9])|1[0-9][0-9]|200)\Z")
_WORKER_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}\Z")
_SHA = re.compile(r"[0-9a-f]{40}\Z")


def create_only_claim_payload(claim: Claim, now: datetime) -> tuple[str, str]:
    """Return (relative GitHub path, JSON content) for a create-only write.

    Never use update_file to replace an existing claim. When GitHub reports
    file-exists, stop and reconcile: no retry with a made-up nonce or task ID.
    """
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("timezone-aware now required")
    if not _TASK_ID.fullmatch(claim.task_id):
        raise ValueError("canonical CF-001 through CF-200 ID required")
    if not _WORKER_ID.fullmatch(claim.operator_id):
        raise ValueError("bounded operator ID required")
    if not _SHA.fullmatch(claim.base_sha):
        raise ValueError("40-character lowercase SHA format required; caller must verify GitHub provenance")
    seconds = (claim.expires_at - now).total_seconds()
    if not (0 < seconds <= 3600):
        raise ConflictError("invalid_claim_lifetime")
    if any("." in p.split("/") or p.endswith("/") or "\\" in p or "//" in p for p in claim.paths):
        raise ValueError("canonical repository paths required")
    path = f"experiments/parallel_coordination/claims/{claim.task_id}.json"
    record = {
        "schema": "cf0.parallel_claim_experiment.v1",
        "status": "pending_unverified",
        "task_id": claim.task_id,
        "operator_id": claim.operator_id,
        "base_blob_sha": claim.base_sha,
        "paths": sorted(claim.paths),
        "created_at": now.astimezone(timezone.utc).isoformat(),
        "expires_at": claim.expires_at.astimezone(timezone.utc).isoformat(),
        "release_policy": "no_automatic_reclaim_or_remote_execution",
    }
    return path, json.dumps(record, sort_keys=True, indent=2) + "\n"
