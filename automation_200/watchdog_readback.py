"""Identify one public watchdog packet using GitHub run metadata and its job log."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

from relay.channel_audit import REPO

from .watchdog_handoff import read_report

WORKFLOW = ".github/workflows/cf0-channel-watchdog.yml"
HANDOFF_STEP = "Propose next source-only work under founder policy"
MAX_LOG_BYTES = 512_000
MAX_PACKET_BYTES = 8192
DIGEST_LINE = re.compile(rb"(?:\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,9})?Z) CF0_WORK_HANDOFF_SHA256=([a-f0-9]{64})")
PACKET_LINE = re.compile(
    rb"(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,9})?Z) CF0_WORK_HANDOFF=(.*)"
)


def utc_time(value: object) -> datetime:
    if not isinstance(value, str) or len(value) > 48 or "T" not in value:
        raise ValueError("invalid UTC timestamp")
    try:
        stamp = datetime.fromisoformat(value)
    except ValueError:
        raise ValueError("invalid UTC timestamp") from None
    if stamp.utcoffset() != timedelta(0):
        raise ValueError("invalid UTC timestamp")
    return stamp


def record_readback(run: dict, job: dict, log: bytes) -> dict:
    """Bind the exact packet bytes to a successful run attempt. No task executes."""
    if not isinstance(run, dict) or not isinstance(job, dict):
        raise ValueError("invalid watchdog metadata")
    run_id, attempt, job_id = run.get("id"), run.get("run_attempt"), job.get("id")
    commit, event = run.get("head_sha"), run.get("event")
    if any(type(value) is not int or value <= 0 for value in (run_id, attempt, job_id)):
        raise ValueError("invalid watchdog run or job ID")
    for key in ("repository", "head_repository"):
        repo = run.get(key)
        if not isinstance(repo, dict) or repo.get("full_name") != REPO:
            raise ValueError("unexpected watchdog repository")
    if (run.get("path") != WORKFLOW or run.get("head_branch") != "main"
            or not isinstance(commit, str) or not re.fullmatch(r"[a-f0-9]{40}", commit)
            or event not in ("schedule", "push", "workflow_dispatch")):
        raise ValueError("unexpected watchdog workflow or source")
    if (type(job.get("run_id")) is not int or job["run_id"] != run_id
            or type(job.get("run_attempt")) is not int or job["run_attempt"] != attempt
            or job.get("name") != "audit" or job.get("head_sha") != commit
            or any(item.get("status") != "completed" or item.get("conclusion") != "success"
                   for item in (run, job))):
        raise ValueError("watchdog job does not match the successful run attempt")
    steps = job.get("steps")
    if not isinstance(steps, list):
        raise ValueError("missing watchdog handoff step")
    matches = [step for step in steps
               if isinstance(step, dict) and step.get("name") == HANDOFF_STEP]
    if (len(matches) != 1 or matches[0].get("status") != "completed"
            or matches[0].get("conclusion") != "success"):
        raise ValueError("watchdog handoff step did not succeed")
    step = matches[0]

    if len(log) > MAX_LOG_BYTES:
        raise ValueError("watchdog job log is too large")
    packets = [match.groups() for line in log.splitlines()
               if (match := PACKET_LINE.fullmatch(line))]
    if len(packets) != 1 or len(packets[0][1]) > MAX_PACKET_BYTES:
        raise ValueError("expected one bounded watchdog packet")
    log_stamp, raw = packets[0]
    # Older watchdog logs have no digest line; validate it when emitted.
    # Fail closed if an emitted digest marker is malformed rather than ignoring it.
    digest_markers = [line for line in log.splitlines()
                      if b" CF0_WORK_HANDOFF_SHA256=" in line]
    if any(DIGEST_LINE.fullmatch(line) is None for line in digest_markers):
        raise ValueError("malformed watchdog digest marker")
    digest_lines = [DIGEST_LINE.fullmatch(line).group(1).decode("ascii")
                    for line in digest_markers]
    if len(digest_lines) > 1 or (digest_lines and digest_lines[0] != hashlib.sha256(raw).hexdigest()):
        raise ValueError("watchdog logged digest does not match packet bytes")
    try:
        packet = json.loads(raw)
        canonical = json.dumps(packet, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")
    except (ValueError, RecursionError):
        raise ValueError("invalid watchdog packet JSON") from None
    if (not isinstance(packet, dict) or canonical != raw
            or packet.get("schema") != "cf0.work_handoff.v1"
            or packet.get("source_commit") != commit or packet.get("watchdog_event") != event):
        raise ValueError("packet does not match the watchdog source")
    hp = packet.get("hp")
    if (packet.get("execution_authorized") is not False or not isinstance(hp, dict)
            or hp.get("identity_attested") is not False
            or hp.get("scheduled_receipt_origin") != "unverified"):
        raise ValueError("packet crosses the watchdog evidence boundary")
    assembled = utc_time(packet.get("assembled_utc"))
    # GitHub's step timestamps are whole seconds, while log lines have fractions.
    logged = utc_time(log_stamp.decode("ascii")).replace(microsecond=0)
    if not utc_time(step.get("started_at")) <= assembled <= logged <= utc_time(step.get("completed_at")):
        raise ValueError("packet falls outside the watchdog handoff step")
    return {
        "schema": "cf0.work_handoff_readback.v1",
        "watchdog_run_id": run_id,
        "watchdog_run_attempt": attempt,
        "watchdog_job_id": job_id,
        "watchdog_event": event,
        "source_commit": commit,
        "packet_assembled_utc": assembled.isoformat(),
        "packet_sha256": hashlib.sha256(raw).hexdigest(),
        "execution_authorized": False,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-metadata", type=Path, required=True)
    parser.add_argument("--job-metadata", type=Path, required=True)
    parser.add_argument("--job-log", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        with args.job_log.open("rb") as source:
            log = source.read(MAX_LOG_BYTES + 1)
        result = record_readback(read_report(args.run_metadata), read_report(args.job_metadata), log)
    except OSError:
        parser.error("watchdog job log unavailable")
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
