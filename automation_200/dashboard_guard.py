#!/usr/bin/env python3
"""Offline CF-0 public dashboard consistency audit; no network or writes.

Checks a rendered summary against the exact local registry snapshot.
Does NOT establish real HP identity, live GitHub issue state or revenue.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
COUNTS_RE = re.compile(r"\*\*(\d+) verified / (\d+) total\*\*; (\d+) planned")
BLOB_RE = re.compile(r"source blob \`([a-f0-9]{40})\`")
ISSUE_COUNT_RE = re.compile(r"\| Open GitHub issues \| \*\*(\d+)\*\*")
ISSUE_URL_RE = re.compile(r"https://github\.com/whoiwts110217-creator/CF-0/issues/(\d+)")
CANDIDATE_RE = re.compile(r"^\|[^|\n]*\| \*\*(CF-\d{3})\*\* \|", re.M)
HELD_LOCAL = {"CF-042", "CF-077", "CF-184", "CF-190", "CF-191", "CF-194"}


def git_blob_sha(data: bytes) -> str:
    """Git's SHA-1 object identity for exact file contents."""
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def section(document: str, heading: str) -> str:
    """Extract a second-level Markdown section without interpreting its links."""
    chunks = document.split("## " + heading, 1)
    if len(chunks) != 2:
        return ""
    return chunks[1].split("\n## ", 1)[0]


def check(registry_bytes: bytes, board: str) -> list[str]:
    """Return diagnostics; never mutate the registry or mark work done."""
    errors: list[str] = []
    try:
        registry = json.loads(registry_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return ["Registry is not valid JSON: " + type(exc).__name__]
    if not isinstance(registry, dict) or not isinstance(registry.get("tasks"), list):
        return ["Registry lacks the expected tasks array"]
    tasks = registry["tasks"]
    try:
        target = registry["target"]
        verified = sum(t["status"] == "verified" for t in tasks)
        planned = sum(t["status"] == "planned" for t in tasks)
        by_id = {t["id"]: t for t in tasks}
    except (KeyError, TypeError) as exc:
        return ["Registry has invalid task entries: " + type(exc).__name__]
    if (type(target) is not int or len(tasks) != target
            or verified + planned != target or len(by_id) != target):
        errors.append("Registry task totals, IDs or statuses do not reconcile")
    if registry.get("completed") != verified:
        errors.append("Registry completed counter differs from verified task statuses")

    match = COUNTS_RE.search(section(board, "Status at a glance"))
    if not match:
        errors.append("Dashboard status table is missing machine-checkable verified/total/planned counts")
    elif tuple(map(int, match.groups())) != (verified, target, planned):
        errors.append("Dashboard work-order counts do not match current registry")

    reference = BLOB_RE.search(board)
    if not reference:
        errors.append("Dashboard lacks exact registry blob ID")
    elif reference.group(1) != git_blob_sha(registry_bytes):
        errors.append("Dashboard references an obsolete or mismatched registry blob")

    candidates = CANDIDATE_RE.findall(section(board, "What is being worked on next?"))
    if not candidates:
        errors.append("No candidate task IDs found in current-work table")
    if len(candidates) != len(set(candidates)):
        errors.append("Candidate task appears more than once")
    for task_id in candidates:
        task = by_id.get(task_id)
        if task is None:
            errors.append("Unknown dashboard candidate: " + task_id)
            continue
        if task["status"] != "planned":
            errors.append("Dashboard still offers completed/unplanned task: " + task_id)
        if (task.get("physical_hp_required") or task.get("stream") == "hp_install"
                or task_id in HELD_LOCAL):
            errors.append("Dashboard offers device/owner-only task as source-work candidate: " + task_id)
        if any(by_id.get(dep, {}).get("status") != "verified"
               for dep in task.get("depends_on", [])):
            errors.append("Candidate dependencies not yet verified: " + task_id)

    issue_section = section(board, "Open GitHub Issues (last checked: November 7)")
    if not issue_section:
        issue_section = section(board, "Open GitHub Issues")
    listed = ISSUE_URL_RE.findall(issue_section)
    match = ISSUE_COUNT_RE.search(section(board, "Status at a glance"))
    if match:
        if int(match.group(1)) != len(set(listed)):
            errors.append("Displayed GitHub issue count does not match distinct linked issue numbers")
    elif "| Open GitHub issues |" not in board:
        errors.append("Dashboard lacks a checked/unknown GitHub issue count")
    if len(listed) != len(set(listed)):
        errors.append("Duplicate issue URLs in GitHub Issues section")
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=ROOT / "automation_200" / "registry.json")
    parser.add_argument("--dashboard", type=Path, default=ROOT / "docs" / "TASKS_AND_ISSUES.md")
    args = parser.parse_args(argv)
    errors = check(args.registry.read_bytes(), args.dashboard.read_text(encoding="utf-8"))
    if errors:
        for error in errors:
            print("FAIL: " + error)
        return 1
    print("PASS: public dashboard and local registry are internally consistent")
    print("NOTE: this does not verify live GitHub Issues, HP status or payments")
    return 0


if __name__ == "__main__":
    sys.exit(main())
