#!/usr/bin/env python3
"""Read-only, private Spider candidate exporter for existing CF-0 local index.

Uses ONLY conversations already indexed by continuity.local_index. No network,
new archive/database, status promotion, publishing, or private data on stdout.
All candidates require human review; this is not an NLP truth or action engine.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile

from .local_index import ROOT, default_state, safe_state

UUID = re.compile(r"^[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$")
SOURCE = re.compile(r"^sha256:[0-9a-f]{64}$")
IDENT = re.compile(r"^[A-Za-z0-9_.:-]{1,100}$")
DANGER = re.compile(
    r"(?i)\b(password|passcode|one.time passcode|otp|2fa|recovery code|"
    r"api key|secret key|private key|access.token|social security|ssn)\b"
    r"|\b\d{3}-\d{2}-\d{4}\b"
)
ASSISTANT_ACTION = re.compile(
    r"(?im)^\s*(?:ACTION REQUIRED(?:\s*\[[^\]\n]{1,45}\])?|"
    r"Your action|Owner action|You need to)\s*(?::|—|-)\s*(.{6,200})"
)
USER_ACTION = re.compile(
    r"(?im)\b(?:I need to|I have to|I should|I will|I'll|remind me to)\s+([^\n]{6,180})"
)
MAX_SCAN = 200_000
MAX_CANDIDATES = 100


def candidate_text(body: str, role: str) -> list[str]:
    if role not in {"assistant", "user"} or not isinstance(body, str):
        return []
    # Whole-message secret filter prevents accidentally exporting a fragment
    # from a message containing authentication or financial secrets.
    if len(body) > 100_000 or DANGER.search(body):
        return []
    regex = ASSISTANT_ACTION if role == "assistant" else USER_ACTION
    matches = []
    for match in regex.finditer(body[:30000]):
        snippet = re.sub(r"\s+", " ", match.group(1)).strip(" .:;-\t")
        if len(snippet) < 6 or "http://" in snippet or "https://" in snippet:
            continue
        if re.search(r"(?i)\b(?:example|sample|hypothetical|fictional)\b", snippet):
            continue
        if snippet.casefold() not in {x.casefold() for x in matches}:
            matches.append(snippet[:180])
        if len(matches) >= 3:
            break
    return matches


def private_pointer(source_id: str, conversation_id: str, message_id: str) -> str:
    if not SOURCE.fullmatch(source_id):
        raise ValueError("bad_index_source")
    if not IDENT.fullmatch(conversation_id) or not IDENT.fullmatch(message_id):
        raise ValueError("bad_private_message_pointer")
    return "indexed-chat:" + source_id + ":" + conversation_id + ":" + message_id


def stable_id(source_id: str, conversation_id: str, message_id: str, action: str) -> str:
    # UUID conversation IDs are stable across incremental ChatGPT exports.
    # Source-ordinal IDs aren't, so include the source content-addressed key.
    identity = ("" if UUID.fullmatch(conversation_id) else source_id + "|")
    identity += conversation_id + "|" + message_id + "|" + action.casefold()
    return "LOCAL-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24]


def read_private_index(state: Path, *, limit: int = 100,
                       source_id: str | None = None) -> tuple[dict, dict]:
    if not 1 <= limit <= MAX_CANDIDATES:
        raise ValueError("limit_must_be_1_to_100")
    state = safe_state(state)
    db = state / "continuity.sqlite3"
    if not db.is_file() or db.is_symlink():
        raise ValueError("existing_private_index_required")
    if source_id is not None and not SOURCE.fullmatch(source_id):
        raise ValueError("bad_source_id")
    conn = sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        sql = """SELECT m.source_id, m.conversation_id, m.message_id, m.role,
                        m.sent_at, m.body, c.title
                   FROM messages AS m
                   JOIN conversations AS c
                     ON c.source_id=m.source_id AND c.conversation_id=m.conversation_id
                   JOIN import_status AS i ON i.source_id=m.source_id
                  WHERE i.status='complete' AND m.role IN ('user','assistant')"""
        args: list[object] = []
        if source_id:
            sql += " AND m.source_id=?"
            args.append(source_id)
        sql += """ ORDER BY CAST(COALESCE(m.sent_at,'0') AS REAL) DESC,
                                m.conversation_id, m.message_id LIMIT ?"""
        args.append(MAX_SCAN + 1)
        rows = conn.execute(sql, args)
        by_id: dict[str, dict] = {}
        inspected = 0
        overflow = False
        for row in rows:
            inspected += 1
            if inspected > MAX_SCAN:
                overflow = True
                break
            for action in candidate_text(row["body"], row["role"]):
                cid, mid, sid = row["conversation_id"], row["message_id"], row["source_id"]
                try:
                    ref = private_pointer(sid, cid, mid)
                except ValueError:
                    continue  # invalid provider/source IDs cannot become links
                key = stable_id(sid, cid, mid, action)
                if key not in by_id:
                    link = ("https://chatgpt.com/c/" + cid) if UUID.fullmatch(cid) else ""
                    title = re.sub(r"[\r\n\t]+", " ", row["title"] or "Untitled")[:75]
                    by_id[key] = {
                        "id": key, "zone": "conditional", "owner": "owner",
                        "priority": "REVIEW", "title": "Review possible action · " + title,
                        "action": action,
                        "detail": "Heuristic candidate from indexed " + row["role"] +
                                  " text; may be old, quoted or already resolved.",
                        "source_ref": ref, "source_refs": [ref],
                        "link": link, "source": link,
                        "label": "Possible original conversation" if link else "",
                        "project_id": "UNRESOLVED", "task_ids": [],
                        "proof": "Owner checks the original and explicitly confirms it is still needed",
                        "caution": "Not verified, not automatically assigned, never shared to GitHub.",
                        "review_required": True,
                        "evidence_role": row["role"],
                    }
                elif ref not in by_id[key]["source_refs"]:
                    by_id[key]["source_refs"].append(ref)
        # Ordered most recent first, bounded output; no silent full-coverage claim.
        entries = list(by_id.values())[:limit]
        manifest = {
            "schema": "cf0.spider.action_manifest.v1",
            "generator": "cf0.existing_private_index.v1",
            "privacy": "owner_private_do_not_upload",
            "review_required": True,
            "coverage": "indexed_text_only_nonsemantic_heuristic",
            "actions": entries,
        }
        summary = {
            "messages_scanned": min(inspected, MAX_SCAN),
            "scan_limit_reached": overflow,
            "candidates_detected": len(by_id),
            "candidates_returned": len(entries),
            "candidates_omitted": max(0, len(by_id) - len(entries)),
            "heuristic_only": True,
            "private_index_read_only": True,
            "external_live_status_verified": False,
        }
        return manifest, summary
    finally:
        conn.close()


def write_private_manifest(output: Path, manifest: dict) -> Path:
    target = output.expanduser().resolve()
    if ROOT == target or ROOT in target.parents:
        raise ValueError("manifest_output_must_be_private_not_public_repo")
    if not target.parent.is_dir() or target.is_symlink():
        raise ValueError("private_output_directory_required")
    if target.exists():
        raise ValueError("refuse_to_overwrite_private_manifest")
    # Restrict best-effort file permissions; no source text printed to terminal.
    fd, name = tempfile.mkstemp(prefix=".spider-private-", dir=target.parent)
    try:
        try:
            os.chmod(name, 0o600)
        except OSError:
            pass
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(manifest, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, target)
        return target
    finally:
        if os.path.exists(name):
            os.unlink(name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=default_state())
    parser.add_argument("--output", required=True, type=Path, help="Private JSON destination outside public CF-0 repository")
    parser.add_argument("--source-id", help="Optional sha256:<digest> of an already indexed private export")
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args(argv)
    manifest, summary = read_private_index(args.state_dir, limit=args.limit, source_id=args.source_id)
    if manifest["actions"]:
        write_private_manifest(args.output, manifest)
        summary["private_manifest_written"] = True
    else:
        summary["private_manifest_written"] = False
    # Never print excerpt/title/path/source IDs. Log only bounded aggregate counts.
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
