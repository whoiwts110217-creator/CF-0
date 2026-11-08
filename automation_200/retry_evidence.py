#!/usr/bin/env python3
"""CF-118 local retry evidence journal (public-safe IDs only).

Append-only, local-only diagnostic state. No HP commands, remote writes, task
execution, or verification authority. A local hash chain detects accidental
edits but is NOT authentication; untrusted journals must not grant execution.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

GENESIS = "0" * 64
MAX_BYTES = 1024 * 1024


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def read_events(path, allowed_ids):
    path = Path(path)
    if not path.exists():
        return [], {}
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("retry journal too large")
    events, attempts, previous = [], {}, GENESIS
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except (ValueError, TypeError) as exc:
            raise ValueError("invalid retry journal JSON") from exc
        if not isinstance(event, dict) or set(event) != {"task", "failures", "failed_at", "previous", "digest"}:
            raise ValueError("invalid retry journal event")
        task, failures, stamp = event["task"], event["failures"], event["failed_at"]
        if (type(task) is not str or task not in allowed_ids or
                type(failures) is not int or not 1 <= failures <= 10 or
                type(stamp) is not int or not 0 <= stamp <= 10**12 or
                event["previous"] != previous):
            raise ValueError("invalid retry journal values or chain")
        body = {key: event[key] for key in ("task", "failures", "failed_at", "previous")}
        digest = hashlib.sha256(_canonical(body).encode("ascii")).hexdigest()
        if digest != event["digest"] or (task in attempts and
            (failures != attempts[task]["failures"] + 1 or stamp < attempts[task]["failed_at"])):
            raise ValueError("retry journal integrity or sequence mismatch")
        previous = digest
        attempts[task] = {"failures": failures, "failed_at": stamp}
        events.append(event)
    return events, attempts


def append_failure(path, allowed_ids, task, stamp):
    """Local-only append; caller must serialize writers and protect the file.

    Reject malformed existing state. Never use this as authorization to retry.
    """
    if type(stamp) is not int or not 0 <= stamp <= 10**12:
        raise ValueError("invalid failure time")
    if type(task) is not str or task not in allowed_ids:
        raise ValueError("unknown task")
    path = Path(path)
    events, attempts = read_events(path, allowed_ids)
    previous = events[-1]["digest"] if events else GENESIS
    old = attempts.get(task)
    if old and stamp < old["failed_at"]:
        raise ValueError("failure time regressed")
    failures = (old["failures"] if old else 0) + 1
    if failures > 10:
        raise ValueError("failure count exceeded")
    body = {"task": task, "failures": failures, "failed_at": stamp, "previous": previous}
    event = dict(body, digest=hashlib.sha256(_canonical(body).encode("ascii")).hexdigest())
    # Exclusive creation on first write; single-writer precondition is explicit.
    flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT
    with os.fdopen(os.open(path, flags, 0o600), "a", encoding="utf-8") as handle:
        handle.write(_canonical(event) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    return event
