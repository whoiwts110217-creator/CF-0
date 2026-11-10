#!/usr/bin/env python3
"""Read-only integrity check for the published CF-0 project index.

CF-141: A public index is a navigable, bounded source document, not the
private original archive or a real-time claim that linked software is deployed.
No network, permissions, GitHub token, transcript or HP access is required.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
INDEX = Path("docs/PROJECTS.md")
_LINK = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^\)\n]+)\)")

REQUIRED_CATEGORIES = (
    "### Operating system and continuity",
    "### Science, philosophy and inventions",
    "### Stories, worlds and games",
    "### Business, delivery and funding",
)
REQUIRED_WORKSTREAMS = (
    "AUTO-08",
    "CF-200",
    "Riemann Hypothesis",
    "Mushroomhead",
    "Caveman Focus Support",
    "Habit Automator",
)
MIN_LINKS = 25


def check_index(root: Path = ROOT, source: str | None = None) -> dict:
    """Return source-quality counts or raise ValueError with a safe reason.

    Only repo-relative file existence is checked; HTTPS destinations, link
    fragments, actual public deployment and private data are *not* validated.
    """
    root = root.resolve()
    index = (root / INDEX).resolve()
    if not index.is_relative_to(root) or not index.is_file():
        raise ValueError("PROJECT_INDEX_NOT_FOUND")
    if source is None:
        source = index.read_text(encoding="utf-8")
    if not isinstance(source, str):
        raise ValueError("INVALID_PROJECT_INDEX")
    if r"\n\n" in source:
        raise ValueError("LITERAL_ESCAPED_NEWLINES")

    for heading in REQUIRED_CATEGORIES:
        if heading not in source:
            raise ValueError("MISSING_PROJECT_CATEGORY")
    for name in REQUIRED_WORKSTREAMS:
        if name not in source:
            raise ValueError("MISSING_PROJECT_WORKSTREAM")
    # Preserve the distinction between inaccessible original project inventory
    # and the later, larger reconstruction of projects plus subworkstreams.
    if not re.search(r"original list[^\n]{0,220}37 projects[^\n]{0,100}unrecovered", source, re.I):
        raise ValueError("ORIGINAL_PROJECT_GAP_MISSING")
    if not re.search(r"62-entry reconstruction[^\n]{0,150}subprojects", source, re.I):
        raise ValueError("RECONSTRUCTION_GAP_MISSING")

    links = _LINK.findall(source)
    if len(links) < MIN_LINKS:
        raise ValueError("INSUFFICIENT_INDEX_LINKS")
    local_links = 0
    for raw in links:
        # External URLs and fragment-only anchors are outside this guard's
        # claims. Never follow them or assert that they are available.
        if raw.startswith("#") or raw.startswith(("https://", "http://", "mailto:")):
            continue
        target = unquote(urlsplit(raw).path)
        if not target:
            continue
        if target.startswith("/") or "\\" in target:
            raise ValueError("UNSAFE_PROJECT_LINK")
        candidate = (index.parent / target).resolve()
        if not candidate.is_relative_to(root):
            raise ValueError("UNSAFE_PROJECT_LINK")
        if not candidate.is_file():
            raise ValueError("BROKEN_PROJECT_LINK")
        local_links += 1
    return {
        "schema": "cf0.project_index_guard.v1",
        "public_index": str(INDEX).replace("\\", "/"),
        "sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "links_checked": local_links,
        "links_total": len(links),
        "archive_completeness": "unverified",
        "hp_identity_attested": False,
        "installed_extension_verified": False,
    }


if __name__ == "__main__":
    print(json.dumps(check_index(), sort_keys=True))
