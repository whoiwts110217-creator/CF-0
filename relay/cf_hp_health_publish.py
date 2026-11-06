#!/usr/bin/env python3
"""Publish an allowlisted HP health summary using the existing relay token.

Opt-in integration only: never runs commands, installs tasks, or reads private
files beyond the existing relay SQLite database. Fixed GitHub destination.
A public report is self-reported evidence, not cryptographic HP attestation.
"""
import base64
import json
import os
import pathlib
import sys

from cf_hp_health_snapshot import snapshot
from cf_public_relay import HttpRepo, RelayError, dump

PATH = "/repos/whoiwts110217-creator/CF-0/contents/relay/health/latest.json"
FIELDS = frozenset(("schema", "collected_utc", "db_exists", "receipt_count",
                    "ping_receipt_count", "last_receipt_status", "error"))
MAX_BYTES = 1024


def sanitized(report):
    if not isinstance(report, dict) or set(report) != FIELDS:
        raise ValueError("invalid_health_schema")
    if report["schema"] != "cf0.hp_health.v1":
        raise ValueError("invalid_health_version")
    if type(report["db_exists"]) is not bool:
        raise ValueError("invalid_health_db_exists")
    for key in ("receipt_count", "ping_receipt_count"):
        value = report[key]
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError("invalid_health_count")
    if report["last_receipt_status"] not in (None, "completed", "failed", "other"):
        raise ValueError("invalid_health_status")
    if report["error"] not in (None, "malformed_receipt", "state_unavailable"):
        raise ValueError("invalid_health_error")
    from datetime import datetime, timezone
    try:
        stamp = datetime.fromisoformat(report["collected_utc"])
        if stamp.tzinfo is None or stamp.utcoffset() != timezone.utc.utcoffset(stamp):
            raise ValueError("not_utc")
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid_health_time") from exc
    data = dump(report)
    if len(data) > MAX_BYTES:
        raise ValueError("health_report_too_large")
    return data


def publish(repo, report):
    data = sanitized(report)
    current = repo.request("GET", PATH + "?ref=main")
    payload = {
        "message": "Update CF-0 public-safe HP health snapshot",
        "branch": "main",
        "content": base64.b64encode(data).decode("ascii"),
    }
    if current is not None:
        if not isinstance(current, dict) or not isinstance(current.get("sha"), str):
            raise RelayError("health_destination_invalid")
        # Avoid an unnecessary commit when retrying identical report content.
        try:
            previous = base64.b64decode("".join(current["content"].split()), validate=True)
        except (KeyError, AttributeError, TypeError, ValueError) as exc:
            raise RelayError("health_destination_invalid") from exc
        if previous == data:
            return "unchanged"
        # The Windows relay polls every five minutes. Avoid a new public
        # commit on every poll when the health metrics have not changed.
        # Still publish a heartbeat at least every 30 minutes.
        try:
            old = json.loads(previous)
            new = json.loads(data)
            from datetime import datetime, timezone
            old_time = datetime.fromisoformat(old["collected_utc"])
            new_time = datetime.fromisoformat(new["collected_utc"])
            same_metrics = all(old.get(key) == new.get(key)
                               for key in FIELDS if key != "collected_utc")
            age = (new_time - old_time).total_seconds()
            if (old_time.tzinfo is not None and new_time.tzinfo is not None
                    and same_metrics and 0 <= age < 1800):
                return "unchanged"
        except (ValueError, TypeError, KeyError, AttributeError):
            # Untrusted previous content must never suppress a fresh report.
            pass
        payload["sha"] = current["sha"]
    repo.request("PUT", PATH, payload)
    return "published"


def main():
    token = os.environ.get("CF_RELAY_GITHUB_TOKEN")
    if not token:
        print(json.dumps({"health": "skipped", "reason": "writeback_not_configured"}))
        return 0
    try:
        report = snapshot()
        outcome = publish(HttpRepo(token=token), report)
        print(json.dumps({"health": outcome, "schema": "cf0.hp_health.v1"}))
        return 0
    except (RelayError, ValueError, OSError) as exc:
        # Never print HTTP bodies, secrets, local paths, or raw exception messages.
        print(json.dumps({"health": "failed", "reason": "publication_unavailable"}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
