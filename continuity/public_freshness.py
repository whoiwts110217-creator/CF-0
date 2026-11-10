#!/usr/bin/env python3
"""Read-only, universal freshness routing for public CF-0 sources.

Does not read unpublished archives, private account data, credentials, or
external providers. 'Latest public file' never means 'live operation verified'.
An arbitrary historical public file remains history even on current main.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path, PurePosixPath
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
REPO = "whoiwts110217-creator/CF-0"
CATALOG_PATH = "docs/FRESHNESS_CATALOG.json"
GRAPH_PATH = "docs/PUBLIC_CONTEXT_GRAPH.json"
ALLOWED_TYPES = {
    "public", "public_index_only", "public_aggregate_only",
    "private_originals_not_published",
}


def safe_public_file(path: str, root: Path = ROOT) -> Path:
    """Validate one repo-relative public file, never follow outside/hidden paths."""
    if not isinstance(path, str) or not path or "\\" in path or "://" in path:
        raise ValueError("INVALID_PUBLIC_PATH")
    pure = PurePosixPath(path)
    if pure.is_absolute() or any(piece in (".", "..") for piece in path.split("/")):
        raise ValueError("INVALID_PUBLIC_PATH")
    resolved_root = root.resolve()
    resolved = (resolved_root / path).resolve()
    if not resolved.is_relative_to(resolved_root) or not resolved.is_file():
        raise ValueError("UNAVAILABLE_OR_OUTSIDE_PUBLIC_SOURCE")
    if (resolved_root / path).is_symlink():
        raise ValueError("SYMLINK_PUBLIC_SOURCE_REQUIRES_REVIEW")
    return resolved


def latest_public_url(path: str, root: Path = ROOT) -> str:
    """Return moving main URL only for a present, contained public source."""
    safe_public_file(path, root)
    return "https://github.com/" + REPO + "/blob/main/" + quote(path, safe="/")


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def source_freshness(path: str, recorded_blob_sha: str | None,
                     root: Path = ROOT) -> dict:
    """Compare a dated snapshot's *exact file bytes* to current checkout bytes.

    'same_source_bytes' means matching local checked-out source only. It is
    not proof this checkout is current online main or the service is active.
    """
    local = safe_public_file(path, root)
    digest = git_blob_sha(local.read_bytes())
    if not recorded_blob_sha:
        state = "snapshot_age_unknown"
    elif not isinstance(recorded_blob_sha, str) or len(recorded_blob_sha) != 40:
        state = "unverifiable_snapshot_id"
    elif recorded_blob_sha == digest:
        state = "same_source_bytes_in_this_checkout"
    else:
        state = "stale_source_snapshot"
    return {"source": path, "source_blob_sha": digest, "snapshot_state": state,
            "latest_public_url": latest_public_url(path, root),
            "live_operation_proven": False}


def tracked_public_files(root: Path = ROOT) -> list[str]:
    """Enumerate the public git checkout without printing or reading file data."""
    try:
        res = subprocess.run(["git", "ls-files", "-z"], cwd=root,
                             capture_output=True, check=True, timeout=10)
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError("PUBLIC_GIT_TRACKING_UNAVAILABLE") from exc
    out = [x.decode("utf-8") for x in res.stdout.split(b"\0") if x]
    if not out:
        raise ValueError("EMPTY_PUBLIC_GIT_TRACKING")
    return sorted(out)


def audit_catalog(root: Path = ROOT) -> dict:
    """Guarantee catalog is only a source router, not an invented state store."""
    catalog = json.loads(safe_public_file(CATALOG_PATH, root).read_text(encoding="utf-8"))
    graph = json.loads(safe_public_file(GRAPH_PATH, root).read_text(encoding="utf-8"))
    if catalog.get("schema") != "cf0.public_freshness_catalog.v1":
        raise ValueError("CATALOG_SCHEMA_CHANGED")
    if catalog.get("canonical_branch") != "main":
        raise ValueError("CANONICAL_SOURCE_BRANCH_CHANGED")
    entries = catalog.get("entries")
    if not isinstance(entries, list):
        raise ValueError("CATALOG_ENTRIES_MISSING")
    ids: set[str] = set()
    areas: set[str] = set()
    for e in entries:
        if not isinstance(e, dict) or not isinstance(e.get("id"), str) or not e["id"]:
            raise ValueError("INVALID_CATALOG_ENTRY")
        if e["id"] in ids:
            raise ValueError("DUPLICATE_CATALOG_ID")
        ids.add(e["id"])
        if e.get("area") not in {"P0", "P1", "P2", "P3"}:
            raise ValueError("INVALID_CATALOG_PRIORITY")
        areas.add(e["area"])
        if e.get("source_type") not in ALLOWED_TYPES:
            raise ValueError("INVALID_CATALOG_PRIVACY_TYPE")
        if e.get("status_origin") != "read_on_demand":
            raise ValueError("CATALOG_IS_NOT_A_LIVE_STATUS_STORE")
        if any(k in e for k in ("private_path", "private_url", "account_id", "credential",
                                 "last_known_payment", "live_status", "completed")):
            raise ValueError("PRIVATE_OR_DUPLICATED_STATUS_IN_CATALOG")
        latest_public_url(e.get("public_anchor", ""), root)
    expected={n["id"] for n in graph.get("nodes", [])}
    if not expected.issubset(ids):
        raise ValueError("PUBLIC_TOPIC_NODE_WITHOUT_FRESHNESS_ROUTE")
    if areas != {"P0", "P1", "P2", "P3"}:
        raise ValueError("MISSING_PRIORITY_LANE")
    # Every tracked repo path has the *generic* resolver, not just these
    # known topic anchors. No automatic classification of private originals.
    files = tracked_public_files(root)
    return {
        "schema": "cf0.public_freshness_audit.v1",
        "catalog_topics": len(entries),
        "public_topic_graph_nodes": len(expected),
        "git_tracked_public_paths": len(files),
        "generic_main_resolver": True,
        "private_origins_auto_discovered": False,
        "runtime_and_payment_status_attested": False,
    }


def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", help="Public repo-relative file to route to current main")
    parser.add_argument("--snapshot-blob", help="Optional dated Git blob SHA to compare")
    args=parser.parse_args(argv)
    if args.path:
        print(json.dumps(source_freshness(args.path, args.snapshot_blob), sort_keys=True))
    else:
        print(json.dumps(audit_catalog(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
