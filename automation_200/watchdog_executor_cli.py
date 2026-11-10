"""Offline, fail-closed correlation of a GitHub watchdog packet with a privately
retrieved ChatGPT executor result.

Run data must be read through an authorized GitHub/provider connection and saved
locally by the operator. This CLI performs no network, account, HP, or GitHub
writes. In particular, it never prints the provider's private run identifier,
task title, prompt, or response.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .watchdog_readback import MAX_LOG_BYTES, record_readback
from .watchdog_executor_result import correlate_recorded_executor_result

MAX_METADATA_BYTES = 256_000
MAX_PROVIDER_BYTES = 256_000
OUTPUT_SCHEMA = "cf0.executor_provider_verification.v1"


def _read_json(path: Path, maximum: int) -> dict:
    with path.open("rb") as handle:
        raw = handle.read(maximum + 1)
    if len(raw) > maximum:
        raise ValueError("input exceeds size limit")
    obj = json.loads(raw.decode("utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("input is not a JSON object")
    return obj


def verify_documents(run: dict, job: dict, log: bytes, provider: dict) -> dict:
    """Return a public-safe status only if both independent validators pass."""
    if not isinstance(log, bytes) or len(log) > MAX_LOG_BYTES:
        raise ValueError("missing or oversized job log")
    producer = record_readback(run, job, log)
    match = correlate_recorded_executor_result(producer, provider)
    if (match.get("recorded_completed_result_matched") is not True
            or match.get("correlated") is not True
            or match.get("execution_authorized") is not False
            or match.get("hp_identity_attested") is not False):
        raise ValueError("non-authorizing source correlation not established")
    return {
        "schema": OUTPUT_SCHEMA,
        "watchdog_run_id": producer["watchdog_run_id"],
        "watchdog_run_attempt": producer["watchdog_run_attempt"],
        "watchdog_job_id": producer["watchdog_job_id"],
        "source_commit": producer["source_commit"],
        "packet_sha256": producer["packet_sha256"],
        "decision": match["decision"],
        "recorded_completed_result_matched": True,
        "executor_run_id_source": match["executor_run_id_source"],
        "execution_authorized": False,
        "provider_origin_cryptographically_attested": False,
        "hp_identity_attested": False,
        "hp_scheduled_origin_verified": False,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run-metadata", type=Path, required=True,
                   help="Native successful GitHub Actions watchdog run JSON")
    p.add_argument("--job-metadata", type=Path, required=True,
                   help="Exact native audit job JSON, not a normalized summary")
    p.add_argument("--job-log", type=Path, required=True,
                   help="Exact GitHub audit job log bytes")
    p.add_argument("--private-executor-result", type=Path, required=True,
                   help="PRIVATE native task record with run_details; never commit")
    args = p.parse_args(argv)
    try:
        run = _read_json(args.run_metadata, MAX_METADATA_BYTES)
        job = _read_json(args.job_metadata, MAX_METADATA_BYTES)
        provider = _read_json(args.private_executor_result, MAX_PROVIDER_BYTES)
        with args.job_log.open("rb") as handle:
            log = handle.read(MAX_LOG_BYTES + 1)
        result = verify_documents(run, job, log, provider)
    except (OSError, ValueError, UnicodeError, TypeError, json.JSONDecodeError):
        # In particular do not disclose private input paths, provider titles,
        # record IDs or message contents in errors or CI logs.
        p.exit(2, "Executor correlation: NOT VERIFIED (invalid or missing evidence).\n")
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
