#!/usr/bin/env python3
"""Read-only CF-0 public HP health monitor.

A fresh public report is ONLY a claimed heartbeat, not attestation of HP
identity, Windows Task Scheduler origin, or seven-day unattended operation.
The monitor neither writes public state nor controls the HP.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import json
import re
import time
import urllib.error
from datetime import datetime, timezone

if __package__:
    from .channel_audit import github_json
else:
    from channel_audit import github_json

URL = ("https://api.github.com/repos/whoiwts110217-creator/CF-0/"
       "contents/relay/health/latest.json?ref=main")
FIELDS = frozenset({
    "schema", "collected_utc", "db_exists", "receipt_count",
    "ping_receipt_count", "last_receipt_status", "error",
})
MAX_REPORT_BYTES = 1024
FRESH_SECONDS = 45 * 60  # Publisher sends unchanged-metric heartbeats at 30 min.
STALE_SECONDS = 2 * 60 * 60
FUTURE_TOLERANCE_SECONDS = 5 * 60
EVIDENCE = {
    "physical_hp_identity": "not_attested_by_public_report",
    "scheduled_origin": "not_verified_by_public_report",
    "seven_day_unattended": "not_verified",
}


def status(state: str, **detail) -> dict:
    """Return only fixed, public-safe fields, with non-attestation always explicit."""
    return {"monitor": "cf0.hp_health.read_only.v1", "state": state,
            **EVIDENCE, **detail}


def classify(report: object, now: int | float) -> dict:
    """Validate exact v1 format, then classify freshness without overclaiming."""
    if not isinstance(report, dict) or set(report) != FIELDS:
        return status("invalid", reason="unexpected_schema")
    if report["schema"] != "cf0.hp_health.v1":
        return status("invalid", reason="unexpected_version")
    if type(report["db_exists"]) is not bool:
        return status("invalid", reason="invalid_db_presence")
    for field in ("receipt_count", "ping_receipt_count"):
        value = report[field]
        if value is not None and (type(value) is not int or value < 0):
            return status("invalid", reason="invalid_counts")
    # Ping receipts are a subset of total receipts (recent 200 at most).
    # Reject contradictory public evidence instead of reporting it as healthy.
    if (report["receipt_count"] is not None and report["ping_receipt_count"] is not None
            and report["ping_receipt_count"] > report["receipt_count"]):
        return status("invalid", reason="inconsistent_counts")
    if report["last_receipt_status"] not in (None, "completed", "failed", "other"):
        return status("invalid", reason="invalid_receipt_status")
    # A nonempty receipt ledger cannot have an absent last status. A zero-row
    # ledger cannot report a last receipt or any ping receipts. Reject rather
    # than presenting contradictory self-reported evidence as healthy.
    count = report["receipt_count"]
    last = report["last_receipt_status"]
    if ((count is not None and count > 0 and last is None)
            or (count == 0 and last is not None)):
        return status("invalid", reason="inconsistent_last_receipt")
    if report["error"] not in (None, "malformed_receipt", "state_unavailable"):
        return status("invalid", reason="invalid_error_field")
    try:
        collected = report["collected_utc"]
        if not isinstance(collected, str) or len(collected) > 48:
            raise ValueError("invalid timestamp")
        stamp = datetime.fromisoformat(collected)
        if stamp.tzinfo is None or stamp.utcoffset() != timezone.utc.utcoffset(stamp):
            raise ValueError("timestamp must be UTC")
        age = int(now - stamp.timestamp())
    except (ValueError, TypeError, OverflowError, OSError):
        return status("invalid", reason="invalid_timestamp")
    problem = (report["error"] is not None or report["db_exists"] is False
               or report["receipt_count"] is None or report["ping_receipt_count"] is None)
    evidence = {
        "collected_utc": collected,
        "report_age_seconds": max(0, age),
        "reported_db_exists": report["db_exists"],
        "reported_receipt_count": report["receipt_count"],
        "reported_ping_receipt_count": report["ping_receipt_count"],
        "reported_problem": problem,
    }
    if age < -FUTURE_TOLERANCE_SECONDS:
        return status("future_timestamp", **evidence)
    if age > STALE_SECONDS:
        return status("stale", **evidence)
    if age > FRESH_SECONDS:
        return status("late", **evidence)
    if problem:
        return status("reported_problem", **evidence)
    return status("fresh_public_report", **evidence)


def watch(*, now: int | float | None = None, getter=None, commit: str | None = None) -> dict:
    """Read a single fixed GitHub Contents URL; never print untrusted response text."""
    if commit is not None and not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("invalid_commit")
    url = URL if commit is None else URL.removesuffix("main") + commit
    if now is None:
        now = time.time()
    if getter is None:
        getter = github_json
    try:
        document = getter(url)
    except urllib.error.HTTPError as exc:
        return status("not_published" if exc.code == 404 else "unavailable")
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return status("unavailable")
    if not isinstance(document, dict) or document.get("encoding") != "base64":
        return status("invalid", reason="invalid_contents_response")
    body = document.get("content")
    if not isinstance(body, str) or len(body) > 4000:
        return status("invalid", reason="invalid_encoded_content")
    try:
        raw = base64.b64decode("".join(body.split()), validate=True)
        if len(raw) > MAX_REPORT_BYTES:
            return status("invalid", reason="oversized_report")
        report = json.loads(raw.decode("utf-8"))
    except (binascii.Error, UnicodeError, ValueError, TypeError):
        return status("invalid", reason="malformed_report")
    return classify(report, now)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true",
                        help="Inspect only the fixed public GitHub report path.")
    parser.add_argument("--commit", help="Read the report at a public Git commit SHA.")
    args = parser.parse_args(argv)
    if not args.live:
        parser.error("use --live to inspect public HP health")
    try:
        result = watch(commit=args.commit)
    except ValueError:
        parser.error("--commit must be a 40-character lowercase Git SHA")
    if args.commit:
        result["source_commit"] = args.commit
    print(json.dumps(result, sort_keys=True))
    # Missing, stale or invalid *device evidence* must not break source CI:
    # it stays visibly unverified until the owner HP activates a real report.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
