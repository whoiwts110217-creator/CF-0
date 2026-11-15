#!/usr/bin/env python3
"""Reconstruct the puzzle's complete, source-locked Spider program; do not install it.

python spider-puzzle/assemble.py --output /tmp/Spider-Assembled.zip
Only the Python standard library is required (Python 3.10+).
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter, deque
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
import zipfile

SOURCE_ARCHIVE = "438c442a781b028b1ef8fc336585e540e14dfb5e3828a8d2e8ab35857e2dec24"
SOURCE_REPOSITORY_COMMIT = "13e00e779280904476bc1573fa227dc481f0e350"
SOURCE_MANIFEST = "FRESH_FILES_SHA256.json"
SOURCE_MANIFEST_SHA256 = "59197a17d284df648c78cfe2b206d97065e5da6a3a20eaef6090e2a50f11fb3c"
MANIFEST = "ASSEMBLY_MANIFEST.json"
ATLAS = Path(__file__).resolve().parents[1] / "docs/spider-puzzle/index.html"
DATA_RE = re.compile(r'<script id="embedded-data" type="application/json">(.*?)</script>', re.S)


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def safe_path(name: str) -> str:
    """Use paths that have the same meaning on POSIX and ordinary Windows filesystems."""
    if not isinstance(name, str) or not name or "\\" in name or ":" in name or "\x00" in name:
        raise ValueError("Unsafe package path")
    path = PurePosixPath(name)
    if path.is_absolute() or str(path) != name:
        raise ValueError("Noncanonical package path: " + name)
    reserved = {"CON", "PRN", "AUX", "NUL"} | {f"{p}{i}" for p in ("COM", "LPT") for i in range(1, 10)}
    for part in path.parts:
        if part in (".", "..") or part.endswith((" ", ".")) or any(ord(c) < 32 or c in '<>"|?*' for c in part):
            raise ValueError("Unsafe package path: " + name)
        if part.split(".")[0].upper() in reserved:
            raise ValueError("Reserved Windows path: " + name)
    return name


def validate_paths(names):
    seen = set()
    for name in names:
        key = safe_path(name).casefold()
        if key in seen:
            raise ValueError("Duplicate/case-aliased package path: " + name)
        seen.add(key)
    for name in seen:
        if any(str(parent) in seen for parent in PurePosixPath(name).parents if str(parent) != "."):
            raise ValueError("File/directory path collision: " + name)


def read_catalog(atlas: Path = ATLAS):
    matches = DATA_RE.findall(Path(atlas).read_text(encoding="utf-8"))
    if len(matches) != 1:
        raise ValueError("Expected exactly one embedded source catalog")
    return json.loads(matches[0], object_pairs_hook=unique_object)


def verify_catalog(data):
    if data.get("source_sha256") != SOURCE_ARCHIVE:
        raise ValueError("Wrong original archive fingerprint")
    sources, pieces = data["sources"], data["pieces"]
    if not isinstance(sources, dict) or len(sources) != 94 or len(pieces) != 1289:
        raise ValueError("Expected all 94 files and 1,289 code pieces")
    validate_paths(sources)
    if any(not isinstance(text, str) for text in sources.values()):
        raise ValueError("Source content must be UTF-8 text")
    files = {name: text.encode("utf-8") for name, text in sources.items()}
    if sha256(files[SOURCE_MANIFEST]) != SOURCE_MANIFEST_SHA256:
        raise ValueError("Original full-file manifest changed")
    original = json.loads(sources[SOURCE_MANIFEST], object_pairs_hook=unique_object)
    digests = original["files"]
    if original["file_count"] != 93 or len(digests) != 93 or set(digests) != set(files) - {SOURCE_MANIFEST}:
        raise ValueError("Original full-file inventory mismatch")
    for name, digest in digests.items():
        if sha256(files[name]) != digest:
            raise ValueError("Original source hash mismatch: " + name)
    ids, kinds, file_cards = set(), Counter(), set()
    for piece in pieces:
        name, start, end = piece["path"], piece["line"], piece["end"]
        if name not in sources or type(start) is not int or type(end) is not int:
            raise ValueError("Unknown piece source/range")
        lines = sources[name].splitlines(keepends=True)
        if not 1 <= start <= end <= len(lines):
            raise ValueError("Piece range out of bounds")
        identity = f"{name}:{start}:{piece['kind']}:{piece['symbol']}"
        if piece["id"] != identity or identity in ids:
            raise ValueError("Duplicate or unstable piece identity")
        excerpt = "".join(lines[start - 1:end]).encode("utf-8")
        if len(excerpt) != piece["bytes"] or sha256(excerpt) != piece["sha256"]:
            raise ValueError("Piece hash/length mismatch: " + identity)
        if piece["kind"] == "FILE":
            if name in file_cards or excerpt != files[name]:
                raise ValueError("Incomplete/duplicate whole-file piece")
            file_cards.add(name)
        ids.add(identity)
        kinds[piece["kind"]] += 1
    if kinds != Counter({"FILE": 94, "FUNCTION": 1007, "CLASS": 181, "JS DECLARATION": 7}) or file_cards != set(files):
        raise ValueError("Incomplete source piece inventory")
    edges = data["dep_edges"]
    if len(edges) != 632 or any(e["from"] not in ids or e["to"] not in ids for e in edges):
        raise ValueError("Broken source dependency inventory")
    for name, content in sources.items():
        if name.endswith(".py"):
            ast.parse(content, filename=name)
    return files


def initial_500(pieces):
    """Match full.html's category round-robin, while including whole files for execution."""
    buckets = {}
    for piece in pieces:
        buckets.setdefault(piece["category"], deque()).append(piece["id"])
    result = []
    while len(result) < 500:
        for bucket in buckets.values():
            if bucket and len(result) < 500:
                result.append(bucket.popleft())
    return result


LAUNCHER = r'''#!/usr/bin/env python3
"""Source-assembled Spider entrypoint. Default: integrity + real local smoke test."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
MANIFEST = "ASSEMBLY_MANIFEST.json"


def verify():
    manifest_path = ROOT / MANIFEST
    if manifest_path.is_symlink():
        raise RuntimeError("Assembly manifest must not be a symlink")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if data.get("schema") != "cf0.spider.source_assembly.v1" or data.get("source_archive_sha256") != "__SOURCE_SHA__":
        raise RuntimeError("Wrong assembly manifest/source")
    files = data["files"]
    if len(files) != 97:
        raise RuntimeError("Incomplete assembly manifest")
    folded = set()
    for name, digest in files.items():
        rel = Path(name)
        if (not isinstance(name, str) or "\\" in name or ":" in name or rel.is_absolute()
                or ".." in rel.parts or str(rel.as_posix()) != name or name.casefold() in folded):
            raise RuntimeError("Unsafe/duplicate package path")
        folded.add(name.casefold())
        target = ROOT / rel
        if any(p.is_symlink() for p in [target, *target.parents] if p != ROOT.parent):
            raise RuntimeError("Symlink in package: " + name)
        if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise RuntimeError("Assembly hash mismatch: " + name)
    for target in ROOT.rglob("*"):
        rel = target.relative_to(ROOT)
        if target.is_symlink():
            raise RuntimeError("Unreviewed symlink in package")
        if target.is_file() and "__pycache__" not in rel.parts and target.suffix.lower() in (".py", ".pyw", ".js", ".cmd", ".bat", ".ps1", ".pyd", ".dll", ".exe"):
            if rel.as_posix() not in files:
                raise RuntimeError("Unmanifested executable source: " + rel.as_posix())
    return data


def smoke():
    # Exercise the assembled application's actual objects; no mouse, network or installer.
    from spider.brain import SpiderBrain
    from spider.ledger import ExecutionLedger
    from spider.safety import StopRequestedError
    with tempfile.TemporaryDirectory(prefix="spider_assembly_smoke_") as folder:
        brain = SpiderBrain(Path(folder))
        try:
            if brain.hands.dry_run_ui is not True:
                raise RuntimeError("Unexpected live input default")
            brain.ledger.append(actor="assembly_self_test", module="assembly", action="local_smoke",
                                verification_status="Passed isolated automated tests", outcome="local objects exercised")
            valid, _ = ExecutionLedger(brain.ledger.path).verify_chain()
            if not valid or len(ExecutionLedger(brain.ledger.path).entries) != 1:
                raise RuntimeError("Ledger reload/chain check failed")
            old = brain.authority.start()
            brain.authority.stop("isolated assembly smoke")
            if not old.is_set():
                raise RuntimeError("STOP failed to cancel prior token")
            try:
                brain.authority.start()
            except StopRequestedError:
                pass
            else:
                raise RuntimeError("STOP auto-restarted")
            brain.authority.resume(owner_confirmed=True)  # isolated test object, no host task
            new = brain.authority.start()
            if new is old or new.is_set() or not old.is_set():
                raise RuntimeError("STOP token reused after resume")
            try:
                brain.authority.checkpoint(old)
            except StopRequestedError:
                pass
            else:
                raise RuntimeError("Stale work survived STOP/resume")
            brain.authority.checkpoint(new)
        finally:
            brain.close()
    return ["SpiderBrain imported/constructed", "dry-run input default", "ledger append/reload/hash chain", "STOP latch", "fresh resume token", "stale task rejected"]


def desktop(workspace):
    import tkinter as tk
    # The old GUI's silent fake-widget fallback must never count as a running app.
    root = tk.Tk()
    root.withdraw()
    root.destroy()
    from spider import gui_live
    def reject_stub(*args, **kwargs):
        raise RuntimeError("Real Tk display unavailable; simulated UI is not a desktop launch")
    gui_live._TkStub.Tk = reject_stub
    gui_live.launch_spider(workspace, auto_browser=False)


def main():
    parser = argparse.ArgumentParser(description="Assembled Spider candidate: verify and run local checks, or open the real desktop")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Default: package hashes and actual ledger/STOP smoke")
    mode.add_argument("--desktop", action="store_true", help="Open existing native Spider GUI; dedicated Chrome startup stays off")
    parser.add_argument("--workspace", type=Path, default=ROOT / "assembly_runtime_data")
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        raise RuntimeError("Python 3.10+ is required")
    verify()
    checks = smoke()
    print(json.dumps({"status": "LOCAL_SMOKE_PASSED", "checks": checks,
                      "original_files": 94, "source_pieces": 1289,
                      "evidence": "source-assembled/local-object tests; Windows HP behavior unverified"}, indent=2), flush=True)
    if args.desktop:
        desktop(args.workspace.resolve())
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("SPIDER ASSEMBLY BLOCKED: " + str(exc), file=sys.stderr)
        raise SystemExit(1)
'''.replace("__SOURCE_SHA__", SOURCE_ARCHIVE)

START = '''@echo off\r
setlocal\r
cd /d "%~dp0"\r
where py >nul 2>nul\r
if errorlevel 1 (\r
  python "assembled_spider.py" --desktop\r
) else (\r
  py -3 "assembled_spider.py" --desktop\r
)\r
if errorlevel 1 pause\r
'''

README = """# Source-assembled Spider candidate — 2026-11-15

Creator/developer: David Smith. Intended owner/beneficiary: Kiara Lynn Rose Smith.
The owner's 500-tile assembly request is implemented using whole source modules.
All 1,289 overlapping symbols need their 94 complete original files: concatenating
500 snippets would duplicate classes, omit dependencies and break Python imports.

With Python 3.10+ installed, extract this ZIP to a NEW folder. Run:

    python assembled_spider.py --check

On a Windows desktop with Tk, double-click START_ASSEMBLED_SPIDER.cmd, or run:

    python assembled_spider.py --desktop

The launcher checks all package hashes and exercises the actual application's
ledger, SQLite-backed brain and STOP/resume before opening its original desktop.
It refuses a fake Tk fallback; dedicated Chrome is NOT auto-started. No installer,
new service, account pairing, scheduler, paid model or package download runs.
The source's existing controls remain available only when explicitly selected.

This reconstructs the public atlas snapshot, not the missing original ZIP bytes.
Original source version strings disagree (3.3.4/3.3.13/3.3.14); they are retained.
The original manifest verifies 93 files; ASSEMBLY_MANIFEST.json also covers that
manifest and the three new entry/guide files. Hashes establish consistency, not a
signed provenance guarantee or independent real-world success.

Known original-source defects remain: drag may omit mouse-up after an interrupt;
paste can proceed after failed focus; invalid mouse buttons can become left-clicks.
Mouse-follow, ordinary Chrome control, exact target binding and physical HP STOP
acceptance remain RED/unverified. Inspect docs/spider-puzzle/HANDS_REVIEW.md in CF-0
before live actuation. Local smoke PASS is NOT a complete application acceptance.
No canonical ZIP, prior board layout, HP installation or source was overwritten.
Rollback: close this separate candidate and remove its new folder; retain the
original installation and private data. Do not run two browser writers together.
"""


def package_files(data):
    files = verify_catalog(data)
    files.update({"assembled_spider.py": LAUNCHER.encode(), "START_ASSEMBLED_SPIDER.cmd": START.encode(),
                  "ASSEMBLY_README.md": README.encode()})
    validate_paths(files)
    manifest = {"schema": "cf0.spider.source_assembly.v1", "source_archive_sha256": SOURCE_ARCHIVE,
                "source_repository": "whoiwts110217-creator/CF-0", "source_repository_commit": SOURCE_REPOSITORY_COMMIT,
                "source_manifest_sha256": SOURCE_MANIFEST_SHA256, "original_files": 94, "source_pieces": 1289,
                "requested_table_piece_ids": initial_500(data["pieces"]),
                "assembly_rule": "Whole original files preserve imports, scopes and dependency closure; no snippet concatenation",
                "runtime_patches": [], "windows_hp_verified": False,
                "files": {name: sha256(content) for name, content in sorted(files.items())}}
    files[MANIFEST] = (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode()
    return files


def build(output: Path, atlas: Path = ATLAS):
    output = Path(output)
    if output.suffix.lower() != ".zip":
        raise ValueError("Output must be a .zip file")
    if output.exists() or output.is_symlink():
        raise FileExistsError("Refusing to overwrite output: " + str(output))
    files = package_files(read_catalog(atlas))  # Validate everything before any output writes.
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=output.parent, prefix=".spider_assembly_", suffix=".zip", delete=False) as handle:
        temporary = Path(handle.name)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name, content in sorted(files.items()):
                info = zipfile.ZipInfo(name, date_time=(2026, 11, 15, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        with zipfile.ZipFile(temporary) as archive:
            if archive.testzip() is not None:
                raise ValueError("Generated archive CRC check failed")
        # Publish a complete archive atomically. link() refuses concurrent/existing destinations.
        os.link(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    return {"output": str(output), "sha256": sha256(output.read_bytes()), "files": len(files),
            "source_files": 94, "source_pieces": 1289, "status": "assembled_not_HP_verified"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.output), indent=2))


if __name__ == "__main__":
    main()
