#!/usr/bin/env python3
"""Windows-only validation of the OS byte lock used by HP Control v1.3.

Uses a disposable temp directory. It does NOT import or operate an HP task,
GitHub account, credential, relay or private file.
"""
import os
import pathlib
import subprocess
import sys
import tempfile

if os.name != "nt":
    raise SystemExit("WINDOWS_ONLY_PROBE")

import msvcrt

CHILD = r"""
import msvcrt, sys
with open(sys.argv[1], 'r+b') as stream:
    stream.seek(0)
    try:
        msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        sys.exit(73)  # another process correctly owns the byte lock
    msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
    sys.exit(0)
"""

with tempfile.TemporaryDirectory(prefix="cf0_hp_lock_ci_") as folder:
    path = pathlib.Path(folder) / "operations.lock"
    with path.open("w+b") as stream:
        stream.write(b"\0")
        stream.flush()
        os.fsync(stream.fileno())
        stream.seek(0)
        msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        blocked = subprocess.run([sys.executable, "-c", CHILD, str(path)], check=False, timeout=15)
        if blocked.returncode != 73:
            raise AssertionError(f"Concurrent process did not block: {blocked.returncode}")
        msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)

    allowed = subprocess.run([sys.executable, "-c", CHILD, str(path)], check=False, timeout=15)
    if allowed.returncode != 0:
        raise AssertionError(f"Lock did not release: {allowed.returncode}")

print("WINDOWS_CROSS_PROCESS_BYTE_LOCK=PASSED")
print("SCOPE=ephemeral_ci_only")
print("REAL_HP_DEPLOYMENT=NOT_TESTED")
