#!/usr/bin/env python3
# cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
"""Read-only CF-0 receipt audit. GitHub matches are NOT proof of physical HP origin."""
from __future__ import annotations

import argparse
import base64
import binascii
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import quote

if __package__:
    from .cf_public_relay import REPO, UUID, RelayError, sha, successful_ping, validate, validate_receipt
else:
    from cf_public_relay import REPO, UUID, RelayError, sha, successful_ping, validate, validate_receipt

API = "https://api.github.com"
MAX_FILES = 120
ARCHIVE_REVIEW_AT = 100
PRUNING_GRACE_SECONDS = 7 * 24 * 60 * 60
QUEUE_FOLDERS = ("inbox", "receipts")

def archive_capacity(file_counts: dict[str, int]) -> dict:
    largest_folder = max(file_counts.values())
    if largest_folder > MAX_FILES:
        state = "limit_exceeded"
    elif largest_folder >= ARCHIVE_REVIEW_AT:
        state = "review_due"
    else:
        state = "within_limit"
    return {
        "state": state,
        "file_counts": file_counts,
        "review_at_per_folder": ARCHIVE_REVIEW_AT,
        "limit_per_folder": MAX_FILES,
        "remaining_before_limit": {
            folder: max(0, MAX_FILES - count) for folder, count in file_counts.items()
        },
    }

def summarize(inbox: dict, receipts: dict, now: int) -> dict:
    """Return source-only channel evidence; do not infer an authenticated HP."""
    counts = {
        "requests": len(inbox),
        "matching_execution_receipts": 0,
        "pending_requests": 0,
        "expired_without_receipt": 0,
        "invalid_requests": 0,
        "mismatched_receipts": 0,
        "writeback_setup_probes": 0,
        "orphan_receipts": 0,
    }
    matched_ids = set()
    for filename, job in inbox.items():
        try:
            issued = job.get("issued") if isinstance(job, dict) else None
            validate(job, filename, now=issued if type(issued) is int else 0)
        except (RelayError, ValueError, TypeError):
            counts["invalid_requests"] += 1
            continue
        name = job["id"] + ".json"
        if name not in receipts:
            key = "pending_requests" if job["issued"] - 180 <= now <= job["expires"] else "expired_without_receipt"
            counts[key] += 1
            continue
        matched_ids.add(name)
        receipt = receipts[name]
        try:
            validate_receipt(receipt, job["id"], sha(job))
            if job["action"] == "ping" and not successful_ping(receipt["result"]):
                raise RelayError("unexpected_ping_result")
        except RelayError:
            counts["mismatched_receipts"] += 1
        else:
            counts["matching_execution_receipts"] += 1

    for filename, receipt in receipts.items():
        if filename in matched_ids:
            continue
        if (isinstance(receipt, dict)
                and receipt.get("kind") == "cf0_hp_writeback_probe"
                and receipt.get("status") == "received"):
            counts["writeback_setup_probes"] += 1
        else:
            counts["orphan_receipts"] += 1

    counts["physical_hp_attestation"] = "not_available_from_public_repo"
    counts["interpretation"] = (
        "Public content agrees with queued requests; HP origin is not cryptographically proven."
        if counts["matching_execution_receipts"] else
        "No matching execution receipt; a setup probe or CI pass is not HP execution evidence."
    )
    return counts

def pruning_review(inbox: dict, receipts: dict, *, source_commit: str,
                   protected_ping_id: str, now: int) -> dict:
    """Prepare an exact candidate list for owner review."""
    if not isinstance(source_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError("invalid_source_commit")
    if not isinstance(protected_ping_id, str) or not UUID.fullmatch(protected_ping_id):
        raise ValueError("invalid_protected_ping")
    pairs = []
    for filename, job in sorted(inbox.items()):
        if not isinstance(job, dict) or job.get("action") != "ping" or filename not in receipts:
            continue
        try:
            validate(job, filename, now=job.get("issued"))
            if job["id"] == protected_ping_id or job["expires"] > now - PRUNING_GRACE_SECONDS:
                continue
            request_digest = sha(job)
            receipt = receipts[filename]
            validate_receipt(receipt, job["id"], request_digest)
            if not successful_ping(receipt["result"]):
                continue
            receipt_digest = sha(receipt)
        except (RelayError, ValueError, TypeError):
            continue
        pairs.append({
            "request_id": job["id"],
            "inbox_path": "command_queue/inbox/" + filename,
            "receipt_path": "command_queue/receipts/" + filename,
            "request_sha256": request_digest,
            "receipt_sha256": receipt_digest,
        })
    manifest = {
        "schema": "cf0.queue_pruning_review.v1",
        "source_commit": source_commit,
        "protected_ping_id": protected_ping_id,
        "grace_seconds_after_expiry": PRUNING_GRACE_SECONDS,
        "pairs_for_review": pairs,
    }
    return {"manifest": manifest, "manifest_sha256": sha(manifest), "as_of_epoch": now}

def github_json(url: str) -> object:
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "CavemanFocus-CF0-Channel-Audit/1.0",
               "X-GitHub-Api-Version": "2022-11-28"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=18) as response:
        content = response.read(500_001)
    if len(content) > 500_000:
        raise ValueError("response_too_large")
    return json.loads(content)

def folder_url(folder: str) -> str:
    if folder not in QUEUE_FOLDERS:
        raise ValueError("invalid_directory")
    return f"{API}/repos/{REPO}/contents/command_queue/{folder}"

def list_json_names(folder: str, *, ref: str = "main") -> list[str]:
    listing = github_json(folder_url(folder) + "?ref=" + ref)
    if not isinstance(listing, list):
        raise ValueError("invalid_listing")
    names = [entry["name"] for entry in listing if isinstance(entry, dict)
             and entry.get("type") == "file" and isinstance(entry.get("name"), str)
             and entry["name"].endswith(".json")]
    # An inconsistent listing must never silently overwrite an earlier receipt
    # with the same ID or inflate source evidence by counting duplicates.
    if len(names) != len(set(names)):
        raise ValueError("duplicate_receipt_or_request_id")
    return names

def read_contents_json(url: str) -> object:
    data = github_json(url)
    if not isinstance(data, dict) or data.get("encoding") != "base64":
        raise ValueError("invalid_document")
    body = data.get("content")
    if not isinstance(body, str):
        raise ValueError("invalid_content")
    # GitHub contents are untrusted; malformed base64 must produce a bounded
    # audit failure, not an uncaught traceback or a partial evidence report.
    try:
        decoded = base64.b64decode("".join(body.split()), validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("invalid_base64_content") from exc
    if len(decoded) > 8192:
        raise ValueError("oversized_document")
    return json.loads(decoded)

def read_folder(folder: str, *, names: list[str] | None = None, ref: str = "main") -> dict:
    root = folder_url(folder)
    if names is None:
        names = list_json_names(folder, ref=ref)
    if len(names) > MAX_FILES:
        raise ValueError("audit_limit_reached")
    if len(names) != len(set(names)):
        raise ValueError("duplicate_receipt_or_request_id")
    documents = {}
    for name in names:
        # Construct the exact path from the listing's basename; no arbitrary URLs.
        if "/" in name or ".." in name:
            raise ValueError("invalid_filename")
        documents[name] = read_contents_json(root + "/" + quote(name, safe="") + "?ref=" + ref)
    return documents

def main_commit() -> str:
    response = github_json(f"{API}/repos/{REPO}/git/ref/heads/main")
    if not isinstance(response, dict) or response.get("ref") != "refs/heads/main":
        raise ValueError("invalid_main_ref")
    target = response.get("object")
    if not isinstance(target, dict) or target.get("type") != "commit":
        raise ValueError("invalid_main_ref")
    commit_sha = target.get("sha")
    if not isinstance(commit_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", commit_sha):
        raise ValueError("invalid_main_ref")
    return commit_sha

def public_ping_id(ref: str) -> str:
    state = read_contents_json(f"{API}/repos/{REPO}/contents/docs/PUBLIC_CONTINUITY_STATE.json?ref={ref}")
    if (not isinstance(state, dict) or state.get("schema") != "cf0.public_continuity.v1"
            or not isinstance(state.get("hp"), dict)):
        raise ValueError("invalid_public_continuity")
    ping_id = state["hp"].get("public_ping_request_id")
    if not isinstance(ping_id, str) or not UUID.fullmatch(ping_id):
        raise ValueError("invalid_protected_ping")
    return ping_id

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    modes = p.add_mutually_exclusive_group(required=True)
    modes.add_argument("--live", action="store_true", help="Read CF-0 public inbox and receipts from GitHub.")
    modes.add_argument("--review-pruning", action="store_true", help="Print a read-only candidate manifest.")
    args = p.parse_args(argv)
    capacity = None
    try:
        ref = main_commit() if args.review_pruning else "main"
        names = {folder: list_json_names(folder, ref=ref) for folder in QUEUE_FOLDERS}
        capacity = archive_capacity({folder: len(files) for folder, files in names.items()})
        if capacity["state"] == "limit_exceeded":
            raise ValueError("audit_limit_reached")
        protected_ping_id = public_ping_id(ref) if args.review_pruning else None
        inbox = read_folder("inbox", names=names["inbox"], ref=ref)
        receipts = read_folder("receipts", names=names["receipts"], ref=ref)
        now = int(time.time())
        report = summarize(inbox, receipts, now)
        if args.review_pruning:
            report["pruning_review"] = pruning_review(
                inbox, receipts, source_commit=ref, protected_ping_id=protected_ping_id, now=now
            )
    except (ValueError, OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        # Never print token-bearing headers, machine details or response bodies.
        failure = {"audit": "unavailable", "error_type": type(exc).__name__}
        if capacity is not None:
            failure["archive_capacity"] = capacity
        print(json.dumps(failure, sort_keys=True))
        return 1
    print(json.dumps({"audit": "read_only", "repo": REPO,
                      "archive_capacity": capacity, **report}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
