#!/usr/bin/env python3
# cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
"""Read-only CF-0 receipt audit. GitHub matches are NOT proof of physical HP origin."""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

if __package__:
    from .cf_public_relay import REPO, RelayError, sha, validate
else:
    from cf_public_relay import REPO, RelayError, sha, validate

API = "https://api.github.com"
MAX_FILES = 120

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
        if (isinstance(receipt, dict)
                and set(receipt) == {"v", "id", "request_sha256", "status", "result"}
                and type(receipt["v"]) is int and receipt["v"] == 1
                and receipt["id"] == job["id"]
                and receipt["request_sha256"] == sha(job)
                and receipt["status"] == "completed"
                and isinstance(receipt["result"], dict)
                and (job["action"] != "ping" or successful_ping(receipt["result"]))):
            counts["matching_execution_receipts"] += 1
        else:
            counts["mismatched_receipts"] += 1

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

def successful_ping(result: dict) -> bool:
    return (result.get("pong") is True
            and type(result.get("protocol")) is int
            and result["protocol"] == 1)

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

def read_folder(folder: str) -> dict:
    if folder not in ("inbox", "receipts"):
        raise ValueError("invalid_directory")
    root = f"{API}/repos/{REPO}/contents/command_queue/{folder}"
    listing = github_json(root + "?ref=main")
    if not isinstance(listing, list):
        raise ValueError("invalid_listing")
    files = [entry for entry in listing if isinstance(entry, dict)
             and entry.get("type") == "file" and isinstance(entry.get("name"), str)
             and entry["name"].endswith(".json")]
    if len(files) > MAX_FILES:
        raise ValueError("audit_limit_reached")
    documents = {}
    for entry in files:
        # Construct the exact path from the listing's basename; no arbitrary URLs.
        name = entry["name"]
        if "/" in name or ".." in name:
            raise ValueError("invalid_filename")
        data = github_json(root + "/" + name + "?ref=main")
        if not isinstance(data, dict) or data.get("encoding") != "base64":
            raise ValueError("invalid_document")
        body = data.get("content")
        if not isinstance(body, str):
            raise ValueError("invalid_content")
        decoded = base64.b64decode("".join(body.split()), validate=True)
        if len(decoded) > 8192:
            raise ValueError("oversized_document")
        documents[name] = json.loads(decoded)
    return documents

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--live", action="store_true", help="Read CF-0 public inbox and receipts from GitHub.")
    args = p.parse_args(argv)
    if not args.live:
        p.error("use --live for a read-only GitHub audit")
    try:
        report = summarize(read_folder("inbox"), read_folder("receipts"), int(time.time()))
    except (ValueError, OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        # Never print token-bearing headers, machine details or response bodies.
        print(json.dumps({"audit": "unavailable", "error_type": type(exc).__name__}))
        return 1
    print(json.dumps({"audit": "read_only", "repo": REPO, **report}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
