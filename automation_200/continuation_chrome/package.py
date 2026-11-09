#!/usr/bin/env python3
"""Build only the allowlisted owner-installable AUTO-08 Chrome extension files.

No network, third-party dependency, account inspection, or private archive.
The output folder is the payload for GitHub Actions' downloadable ZIP artifact.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILES = (
    "manifest.json",
    "background.js",
    "core.mjs",
    "popup.html",
    "popup.js",
    "master-control.js",
    "README.md",
    "FIRST_RUN.txt",
)
EXPECTED_PERMISSIONS = {"tabs", "debugger", "scripting", "storage"}
EXPECTED_HOSTS = ["https://chatgpt.com/*"]
EXPECTED_DASHBOARD = ["https://whoiwts110217-creator.github.io/CF-0/mission-control/*"]


def package(destination: Path) -> dict[str, str]:
    config = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    if config.get("manifest_version") != 3:
        raise ValueError("Unexpected extension manifest version")
    if set(config.get("permissions", [])) != EXPECTED_PERMISSIONS:
        raise ValueError("Chrome permissions changed; package requires review")
    if config.get("host_permissions") != EXPECTED_HOSTS:
        raise ValueError("ChatGPT host scope changed; package requires review")
    if config.get("content_scripts", [{}])[0].get("matches") != EXPECTED_DASHBOARD:
        raise ValueError("Mission Control host scope changed; package requires review")
    if config.get("background", {}).get("service_worker") != "background.js":
        raise ValueError("Unexpected background worker")
    if config.get("action", {}).get("default_popup") != "popup.html":
        raise ValueError("Unexpected owner controls")
    if not str(config.get("version", "")).startswith("0.1."):
        raise ValueError("Unexpected extension version")

    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError("Package destination must be empty to avoid stale code")
    hashes: dict[str, str] = {}
    for file in FILES:
        src = ROOT / file
        if not src.is_file() or src.is_symlink():
            raise ValueError("Missing or linked required source: " + file)
        data = src.read_bytes()
        (destination / file).write_bytes(data)
        hashes[file] = hashlib.sha256(data).hexdigest()
    assert sorted(p.name for p in destination.iterdir()) == sorted(FILES)
    return hashes


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python package.py <empty-output-folder>")
    output = Path(sys.argv[1]).resolve()
    result = package(output)
    print(f"CF-0 AUTO-08 package: {len(result)} allowlisted files, no tests, no private data")
    for name, digest in result.items():
        print(f"  {name} sha256:{digest}")
