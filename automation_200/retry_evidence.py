#!/usr/bin/env python3
"""CF-118 local retry evidence journal (public-safe IDs only).

Append-only, local-only diagnostic state. No HP commands, remote writes, task
execution, or verification authority. A local hash chain detects accidental
edits but is NOT authentication; untrusted journals must not grant execution.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import tempfile

GENESIS = "0" * 64
MAX_BYTES = 1024 * 1024


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _read_snapshot(path):
    try:
        with path.open("rb") as handle:
            data = handle.read(MAX_BYTES + 1)
    except FileNotFoundError:
        return b""
    if len(data) > MAX_BYTES:
        raise ValueError("retry journal too large")
    return data


def _parse_events(data, allowed_ids):
    # An interrupted write can leave a valid JSON object without its line
    # terminator. Never accept that ambiguous tail as completed evidence.
    if data and not data.endswith(b"\n"):
        raise ValueError("retry journal missing final newline")
    events, attempts, previous = [], {}, GENESIS
    for line in data.decode("utf-8").splitlines():
        if not line.strip():
            raise ValueError("retry journal contains an empty record")
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
        if digest != event["digest"] or (
            task not in attempts and failures != 1
        ) or (task in attempts and
            (failures != attempts[task]["failures"] + 1 or stamp < attempts[task]["failed_at"])):
            raise ValueError("retry journal integrity or sequence mismatch")
        previous = digest
        attempts[task] = {"failures": failures, "failed_at": stamp}
        events.append(event)
    return events, attempts


def read_events(path, allowed_ids):
    return _parse_events(_read_snapshot(Path(path)), allowed_ids)


@contextmanager
def _writer_lock(path):
    # Keep a stable lock file beside the journal because replacement changes
    # the journal's inode. Closing the handle releases the OS lock.
    lock_path = path.with_name(path.name + ".lock")
    with os.fdopen(os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600), "r+b") as handle:
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield


def _replace_snapshot(path, data):
    # Readers see either the previous journal or the complete new one.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".retry-journal-", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def append_failure(path, allowed_ids, task, stamp):
    """Append a local failure under an interprocess lock.

    Reject malformed existing state. Never use this as authorization to retry.
    """
    if type(stamp) is not int or not 0 <= stamp <= 10**12:
        raise ValueError("invalid failure time")
    if type(task) is not str or task not in allowed_ids:
        raise ValueError("unknown task")
    path = Path(path).resolve()
    with _writer_lock(path):
        data = _read_snapshot(path)
        events, attempts = _parse_events(data, allowed_ids)
        previous = events[-1]["digest"] if events else GENESIS
        old = attempts.get(task)
        if old and stamp < old["failed_at"]:
            raise ValueError("failure time regressed")
        failures = (old["failures"] if old else 0) + 1
        if failures > 10:
            raise ValueError("failure count exceeded")
        body = {"task": task, "failures": failures, "failed_at": stamp, "previous": previous}
        event = dict(body, digest=hashlib.sha256(_canonical(body).encode("ascii")).hexdigest())
        if data and not data.endswith((b"\r", b"\n")):
            data += b"\n"
        data += (_canonical(event) + "\n").encode("ascii")
        if len(data) > MAX_BYTES:
            raise ValueError("retry journal too large")
        _replace_snapshot(path, data)
    return event
