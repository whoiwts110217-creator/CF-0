"""Correlate a watchdog readback with a separately recorded executor response.

Read-only and source-level. The caller must obtain the actual automation record
from an authorized provider, not from a public issue or a generated suggestion.
Even a match in supplied JSON does not cryptographically attest provider origin,
a Windows computer, permission to execute, or task completion.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta

from .watchdog_consumer_ack import verify_consumer_ack

MARKER = "CF0_EXECUTOR_PACKET_DECISION="
MAX_RESULT_CHARACTERS = 120_000
MAX_MARKER_CHARACTERS = 4_096
# Deliberately only accept a standalone machine-readable line, not a markdown
# quote, example, code block with indentation, or an HTML attribute.
LINE = re.compile(r"(?m)^CF0_EXECUTOR_PACKET_DECISION=(\{[^\r\n]*\})$")


def _utc_stamp(value: object) -> datetime:
    if not isinstance(value, str) or len(value) > 48 or "T" not in value:
        raise ValueError("invalid completed or packet timestamp")
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("invalid completed or packet timestamp") from None
    if stamp.utcoffset() != timedelta(0):
        raise ValueError("timestamp must be UTC")
    return stamp


def _no_duplicate_keys(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate decision key")
        obj[key] = value
    return obj


def correlate_recorded_executor_result(readback: dict, automation: dict) -> dict:
    """Check exact packet ID/digest against a completed provider-recorded reply.

    The automation argument is one task object returned by an authorized lookup.
    This function cannot authenticate where a caller obtained that object.
    Do not publish the original automation object, its prompt or its reply.
    """
    if not isinstance(automation, dict):
        raise ValueError("missing automation result")
    details = automation.get("run_details")
    if not isinstance(details, dict):
        raise ValueError("missing recorded automation run")
    last, latest = details.get("last_run"), details.get("latest_result")
    if not isinstance(last, dict) or not isinstance(latest, dict):
        raise ValueError("missing last run or result")
    run_id = last.get("id")
    if (last.get("recorded_status") != "completed"
            or not isinstance(run_id, str)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", run_id)
            or latest.get("run_id") != run_id
            or latest.get("content_truncated") is not False
            or latest.get("is_failure_message") is not False):
        raise ValueError("unusable or mismatched recorded executor result")
    content = latest.get("content_text")
    if not isinstance(content, str) or len(content) > MAX_RESULT_CHARACTERS:
        raise ValueError("executor result missing or over limit")
    lines = [line for line in content.splitlines()
             if line.startswith(MARKER)]
    if len(lines) != 1 or len(lines[0]) > MAX_MARKER_CHARACTERS:
        raise ValueError("exactly one bounded executor decision line required")
    match = LINE.fullmatch(lines[0])
    if match is None:
        raise ValueError("malformed executor decision line")
    try:
        ack = json.loads(match.group(1), object_pairs_hook=_no_duplicate_keys,
                         parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite value")))
    except (TypeError, ValueError, RecursionError):
        raise ValueError("invalid executor decision JSON") from None
    correlation = verify_consumer_ack(readback, ack)
    if correlation["executor_run_id"] != run_id:
        raise ValueError("executor decision was not made by this recorded run")
    if (not isinstance(readback, dict)
            or "packet_assembled_utc" not in readback):
        raise ValueError("missing original packet timestamp")
    packet_time = _utc_stamp(readback["packet_assembled_utc"])
    ended = _utc_stamp(last.get("completed_at"))
    latest_ended = _utc_stamp(latest.get("completed_at"))
    if ended != latest_ended or ended < packet_time:
        raise ValueError("decision predates packet or result times disagree")
    # The exact provider result is stronger source evidence than an arbitrary
    # self-declared JSON acknowledgment, but this parser does not verify the
    # provider connection or authenticate a physical machine.
    return {
        **correlation,
        "recorded_completed_result_matched": True,
        "provider_origin_cryptographically_attested": False,
        "hp_identity_attested": False,
        "execution_authorized": False,
    }
