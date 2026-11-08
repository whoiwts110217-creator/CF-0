"""Read-only check of the existing CF-0 relay request/receipt contract.

This adapter reuses the relay's existing strict validators; it is not an
executor and cannot prove which physical machine produced a public receipt.
The supplied byte content and blob SHA must come from an independently
verified remote read at the intended ref; this function does no I/O.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sys

from evidence_packet import BlobEvidence, git_blob_sha

_RELAY_DIR = Path(__file__).resolve().parents[2] / "relay"
if str(_RELAY_DIR) not in sys.path:
    sys.path.insert(0, str(_RELAY_DIR))
import cf_public_relay as relay


@dataclass(frozen=True)
class RelayPairInspection:
    status: str
    blockers: tuple[str, ...]
    request_digest: str | None = None
    response_digest: str | None = None
    public_pair_consistent: bool = False
    physical_hp_proven: bool = False
    unattended_schedule_proven: bool = False
    automatic_retry_allowed: bool = False
    task_verified: bool = False


def _decode_blob(
    record: BlobEvidence | None, expected_path: str,
) -> tuple[dict | None, str | None]:
    if record is None:
        return None, "missing_readback"
    if not isinstance(record.path, str) or record.path != expected_path:
        return None, "wrong_path"
    if not isinstance(record.content, bytes) or len(record.content) > 8192:
        return None, "invalid_or_oversize_bytes"
    if not isinstance(record.blob_sha, str) or git_blob_sha(record.content) != record.blob_sha:
        return None, "blob_mismatch"
    def unique_pairs(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("duplicate_json_key")
            value[key] = item
        return value

    try:
        obj = json.loads(record.content.decode("utf-8"), object_pairs_hook=unique_pairs,
                         parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")))
    except (UnicodeDecodeError, ValueError):
        return None, "invalid_json"
    if not isinstance(obj, dict):
        return None, "not_an_object"
    return obj, None


def inspect_actual_relay_pair(
    *,
    job_id: str,
    request: BlobEvidence | None,
    receipt: BlobEvidence | None,
) -> RelayPairInspection:
    """Check canonical matching v1/v2 public data, NEVER assert HP origin.

    The request may be historical/expired; structural validation uses its
    recorded issue time, not the present time. Execution freshness is not
    established by this historical evidence inspection.
    """
    if not isinstance(job_id, str) or not relay.UUID.fullmatch(job_id):
        raise ValueError("valid canonical UUIDv4 required")
    inbox_path = f"command_queue/inbox/{job_id}.json"
    receipt_path = f"command_queue/receipts/{job_id}.json"

    job, err = _decode_blob(request, inbox_path)
    if err:
        return RelayPairInspection("HOLD_EVIDENCE", ("request_" + err,))
    if type(job.get("issued")) is not int:
        return RelayPairInspection("HOLD_EVIDENCE", ("request_invalid_issue_time",))
    try:
        relay.validate(job, job_id + ".json", now=job["issued"])
        request_digest = relay.sha(job)
    except (relay.RelayError, TypeError, ValueError, UnicodeError, RecursionError):
        return RelayPairInspection("HOLD_EVIDENCE", ("request_invalid_schema",))

    result, err = _decode_blob(receipt, receipt_path)
    if err:
        return RelayPairInspection(
            "HOLD_EVIDENCE", ("receipt_" + err,), request_digest=request_digest
        )
    try:
        response_digest = relay.validate_receipt(result, job_id, request_digest)
        relay.validate_public_result(result["result"], job["action"])
    except (relay.RelayError, TypeError, ValueError, UnicodeError, RecursionError):
        return RelayPairInspection(
            "HOLD_EVIDENCE", ("receipt_invalid_or_unmatched",),
            request_digest=request_digest
        )
    # The legacy format lacks a result digest bound in the receipt.
    # An accepted historical v1 receipt must still undergo human review.
    if result["v"] == 1:
        return RelayPairInspection(
            "LEGACY_REVIEW_REQUIRED", ("legacy_response_hash_unbound",),
            request_digest=request_digest, response_digest=response_digest
        )
    return RelayPairInspection(
        "CONSISTENT_PUBLIC_PAIR_ONLY", (),
        request_digest=request_digest, response_digest=response_digest,
        public_pair_consistent=True
    )
