"""Integrity-only evidence packet inspection for CF-0 coordination experiments.

Never grants execution, claim release, HP provenance or CF-200 verification.
Git blob SHA-1 detects accidental/stale bytes; it does NOT authenticate a
worker, trusted origin, approval or an independent physical-device receipt.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import re
from typing import Mapping, Sequence

_SHA1 = re.compile(r"[0-9a-f]{40}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_ACTION_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}\Z")


@dataclass(frozen=True)
class BlobEvidence:
    path: str
    blob_sha: str
    content: bytes


@dataclass(frozen=True)
class PacketInspection:
    status: str
    reasons: tuple[str, ...]
    matched_receipt_ids: tuple[str, ...]
    receipts_accounted_for: bool
    automatic_retry_allowed: bool = False
    automatic_release_allowed: bool = False
    task_verified: bool = False


def git_blob_sha(content: bytes) -> str:
    """Byte-exact Git blob SHA-1; no origin/authenticity guarantees."""
    if not isinstance(content, bytes):
        raise TypeError("blob content must be bytes")
    return hashlib.sha1(b"blob " + str(len(content)).encode("ascii") + b"\0" + content).hexdigest()


def _valid_path(path: str) -> bool:
    return (
        isinstance(path, str) and bool(path) and not path.startswith("/")
        and "\\" not in path
        and all(part not in ("", ".", "..") for part in path.split("/"))
    )


def _decode(record: BlobEvidence, expected_path: str) -> tuple[dict | None, str | None]:
    if not _valid_path(record.path) or record.path != expected_path:
        return None, "path_mismatch"
    if not isinstance(record.blob_sha, str) or not _SHA1.fullmatch(record.blob_sha):
        return None, "invalid_blob_sha"
    if not isinstance(record.content, bytes):
        return None, "invalid_content_type"
    if git_blob_sha(record.content) != record.blob_sha:
        return None, "blob_integrity_mismatch"
    try:
        payload = json.loads(record.content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, "invalid_json"
    if not isinstance(payload, dict):
        return None, "invalid_object"
    return payload, None


def inspect_packet(
    *,
    claim: BlobEvidence | None,
    expected_claim_path: str,
    expected_task: str,
    expected_operator: str,
    expected_base_sha: str,
    expected_paths: tuple[str, ...],
    now: datetime,
    receipts: Sequence[BlobEvidence],
    expected_receipts: Mapping[str, tuple[str, str]],
) -> PacketInspection:
    """Check readback integrity and expected request links, not authority.

    Receipts use the *experimental* normalized schema below, not an
    assertion that existing HP relay receipts have the same format.
    expected_receipts maps action ID to (source path, expected request SHA-256).
    The caller must obtain trusted expected values and source bytes separately.
    """
    if not _valid_path(expected_claim_path):
        raise ValueError("canonical expected claim path required")
    if expected_claim_path != f"experiments/parallel_coordination/claims/{expected_task}.json":
        raise ValueError("expected claim path must be canonical for task")
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("timezone-aware observation required")
    if not expected_paths or any(not _valid_path(p) for p in expected_paths):
        raise ValueError("canonical nonempty expected file scope required")
    if not expected_task or not expected_operator or not _SHA1.fullmatch(expected_base_sha):
        raise ValueError("expected claim identity and SHA required")
    issues: list[str] = []
    valid_ids: list[str] = []
    if claim is None:
        issues.append("missing_claim_readback")
    else:
        body, error = _decode(claim, expected_claim_path)
        if error:
            issues.append("claim_" + error)
        elif (
            body.get("schema") != "cf0.parallel_claim_experiment.v1"
            or body.get("task_id") != expected_task
            or body.get("operator_id") != expected_operator
            or body.get("base_blob_sha") != expected_base_sha
            or body.get("status") != "pending_unverified"
            or body.get("paths") != sorted(expected_paths)
            or body.get("release_policy") != "no_automatic_reclaim_or_remote_execution"
        ):
            issues.append("claim_identity_or_policy_mismatch")
        else:
            try:
                created = datetime.fromisoformat(body["created_at"])
                expires = datetime.fromisoformat(body["expires_at"])
                if (created.tzinfo is None or expires.tzinfo is None
                    or not created <= now < expires
                    or not 0 < (expires - created).total_seconds() <= 3600):
                    issues.append("claim_time_window_invalid_or_expired")
            except (KeyError, TypeError, ValueError):
                issues.append("claim_time_window_invalid_or_expired")
    observed_paths: set[str] = set()
    observed_ids: set[str] = set()
    for r in receipts:
        # One receipt path per expected action; never accept arbitrary paths.
        if not _valid_path(r.path):
            issues.append("invalid_receipt_path")
            continue
        if r.path in observed_paths:
            issues.append("duplicate_receipt_path")
            continue
        observed_paths.add(r.path)
        target = next(
            ((rid, request_sha) for rid, (path, request_sha) in expected_receipts.items()
             if path == r.path), None
        )
        if target is None:
            issues.append("unexpected_receipt_path")
            continue
        expected_id, expected_request_sha = target
        body, error = _decode(r, r.path)
        if error:
            issues.append("receipt_" + error)
            continue
        rid = body.get("action_id")
        if not isinstance(rid, str) or not _ACTION_ID.fullmatch(rid) or rid != expected_id:
            issues.append("receipt_action_id_mismatch")
            continue
        if rid in observed_ids:
            issues.append("duplicate_receipt_action")
            continue
        observed_ids.add(rid)
        if not isinstance(expected_request_sha, str) or not _SHA256.fullmatch(expected_request_sha):
            issues.append("invalid_expected_request_sha")
        elif body.get("request_sha256") != expected_request_sha:
            issues.append("receipt_request_mismatch")
        elif body.get("result_status") != "completed":
            issues.append("receipt_not_completed")
        else:
            valid_ids.append(rid)
    if len({p for p, _ in expected_receipts.values()}) != len(expected_receipts):
        issues.append("duplicate_expected_receipt_path")
    for rid in expected_receipts:
        if rid not in valid_ids:
            issues.append("missing_verified_receipt:" + rid)
    accounted = not issues and len(valid_ids) == len(expected_receipts)
    return PacketInspection(
        status="INTEGRITY_CHECKED_ONLY" if accounted else "HOLD_EVIDENCE",
        reasons=tuple(dict.fromkeys(issues)),
        matched_receipt_ids=tuple(sorted(valid_ids)),
        receipts_accounted_for=accounted,
    )
