#!/usr/bin/env python3
"""Read back a GitHub Pages release. No account, browser, or third-party API needed.

The deployed manifest is source evidence, not proof of human visits or payments.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

SCHEMA = "cf0.pages_deployment.v1"
ROUTES = {
    "": "Caveman Focus",
    "mission-control/": "Mission Control",
    "clarity-card/": "Clarity Card",
    "clarity-brief/": "Clarity Brief",
    "clarity-check/": "Clarity Check",
    "link-vault/": "LINK VAULT",
}


def write_manifest(site_directory: str, source_commit: str, workflow_run_id: str) -> Path:
    if len(source_commit) != 40 or any(c not in "0123456789abcdef" for c in source_commit.lower()):
        raise ValueError("source commit must be a 40-character Git SHA")
    if not workflow_run_id.isdecimal():
        raise ValueError("run ID must be decimal")
    site = Path(site_directory)
    if not site.is_dir():
        raise ValueError("staged public site does not exist")
    dest = site / "deployment-manifest.json"
    dest.write_text(json.dumps({"schema": SCHEMA, "source_commit": source_commit,
                                "workflow_run_id": workflow_run_id}, sort_keys=True) + "\n", encoding="utf-8")
    return dest


def fetch_public_bytes(url: str) -> bytes:
    # Limit response size; public static HTML and manifest are small.
    req = Request(url, headers={"Cache-Control": "no-cache", "User-Agent": "CF0-Pages-Release-Readback/1.0"})
    with urlopen(req, timeout=12) as response:
        if response.status != 200:
            raise ValueError(f"HTTP {response.status} for {url}")
        raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError(f"Public response too large: {url}")
        return raw


def verify_once(base_url: str, commit: str, run_id: str, fetch=fetch_public_bytes, *, expected_catalog: bytes | None = None) -> None:
    base = base_url.rstrip("/") + "/"
    parts = urlparse(base)
    if parts.scheme != "https" or not parts.netloc:
        raise ValueError("Pages base URL must be https")
    manifest_url = urljoin(base, "deployment-manifest.json")
    manifest = json.loads(fetch(manifest_url).decode("utf-8"))
    if manifest != {"schema": SCHEMA, "source_commit": commit, "workflow_run_id": run_id}:
        raise ValueError("Live deployment manifest is stale, unexpected or mismatched")
    for route, marker in ROUTES.items():
        url = urljoin(base, route)
        body = fetch(url).decode("utf-8")
        if "<html" not in body.lower() or marker not in body:
            raise ValueError(f"Live route {route or '/'} lacks expected page marker {marker!r}")
    if expected_catalog is not None:
        live_catalog = fetch(urljoin(base, "link-vault/links.json"))
        if live_catalog != expected_catalog:
            raise ValueError("Live Link Vault public catalog is stale or mismatched against the release checkout")
        catalog = json.loads(live_catalog.decode("utf-8"))
        if catalog.get("schema") != "cf.link.vault.public.v2" or len(catalog.get("links", [])) < 78:
            raise ValueError("Live Link Vault public catalog schema or entries invalid")


def verify_with_retry(base_url: str, commit: str, run_id: str, *, fetch=fetch_public_bytes,
                      sleep=time.sleep, attempts: int = 6, delay: float = 12,
                      expected_catalog: bytes | None = None) -> None:
    if attempts < 1:
        raise ValueError("at least one attempt is required")
    for i in range(attempts):
        try:
            verify_once(base_url, commit, run_id, fetch=fetch, expected_catalog=expected_catalog)
        except (OSError, TimeoutError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
            if i == attempts - 1:
                raise RuntimeError(f"Live Pages readback not verified after {attempts} attempts; "
                                   f"the deploy job may have succeeded but the live site did not prove this release: {exc}") from exc
            print(f"Pages live-readback attempt {i+1}/{attempts} not verified: {exc}", flush=True)
            sleep(delay)
        else:
            print(f"Live Pages release verified: commit={commit} run={run_id}, "
                  f"routes={','.join('/'+r for r in ROUTES)}", flush=True)
            return


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    stage = sub.add_parser("write-manifest")
    stage.add_argument("site_dir")
    stage.add_argument("commit")
    stage.add_argument("run_id")
    check = sub.add_parser("verify")
    check.add_argument("base_url")
    check.add_argument("commit")
    check.add_argument("run_id")
    args = parser.parse_args(argv)
    if args.command == "write-manifest":
        print(write_manifest(args.site_dir, args.commit, args.run_id))
    else:
        catalog_path = Path("link-vault/links.json")
        if not catalog_path.is_file():
            raise ValueError("Expected Link Vault catalog missing from this release checkout")
        verify_with_retry(args.base_url, args.commit, args.run_id,
                          expected_catalog=catalog_path.read_bytes())
    return 0


if __name__ == "__main__":
    sys.exit(main())
