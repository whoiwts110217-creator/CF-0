#!/usr/bin/env python3
"""CF-0 local-first source provenance, ChatGPT export index and project event graph.

Python standard library only; NO network, remote execution or public publishing.
All raw source files and searchable chat content stay in an explicit private
local state directory, outside the public CF-0 checkout.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sqlite3
import sys
import tempfile
import time
import uuid
import zipfile

MAX_SOURCE_BYTES = 1_073_741_824  # 1 GiB; one user's explicit file at a time
MAX_EXPORT_BYTES = 536_870_912  # 512 MiB unpacked conversations.json
MAX_CONVERSATION_BYTES = 16_777_216  # memory guard per one JSON conversation
MAX_ZIP_MEMBERS = 10000
CHUNK = 65536
PROJECT_ID = re.compile(r"^[A-Z0-9][A-Z0-9_-]{2,63}$")
ROOT = Path(__file__).resolve().parents[1]


def default_state() -> Path:
    local = os.environ.get("LOCALAPPDATA")
    return (Path(local) / "CavemanFocus" / "Continuity") if local else (Path.home() / ".caveman_focus_continuity")


def safe_state(path: Path) -> Path:
    state = path.expanduser().resolve()
    # Never write a private chat database or originals into the public source tree.
    if state == ROOT or ROOT in state.parents or state in ROOT.parents:
        raise ValueError("private_state_must_be_outside_public_repo")
    return state


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _private_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    try:
        path.chmod(0o700)
    except OSError:
        pass  # Windows ACLs remain the current Windows user's responsibility.


def open_db(state: Path) -> sqlite3.Connection:
    state = safe_state(state)
    _private_dir(state)
    _private_dir(state / "originals")
    db = state / "continuity.sqlite3"
    conn = sqlite3.connect(str(db), timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sources (
            id TEXT PRIMARY KEY, sha256 TEXT NOT NULL UNIQUE, byte_size INTEGER NOT NULL,
            kind TEXT NOT NULL, imported_at TEXT NOT NULL, archive_path TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS source_origins (
            id INTEGER PRIMARY KEY, source_id TEXT NOT NULL REFERENCES sources(id),
            source_path TEXT NOT NULL, label TEXT NOT NULL, observed_at TEXT NOT NULL,
            UNIQUE(source_id, source_path, label)
        );
        CREATE TABLE IF NOT EXISTS conversations (
            source_id TEXT NOT NULL REFERENCES sources(id), conversation_id TEXT NOT NULL,
            title TEXT NOT NULL, created_at TEXT, updated_at TEXT,
            ordinal INTEGER NOT NULL, PRIMARY KEY(source_id, conversation_id)
        );
        CREATE TABLE IF NOT EXISTS messages (
            source_id TEXT NOT NULL, conversation_id TEXT NOT NULL, message_id TEXT NOT NULL,
            role TEXT NOT NULL, sent_at TEXT, body TEXT NOT NULL,
            PRIMARY KEY(source_id, conversation_id, message_id),
            FOREIGN KEY(source_id, conversation_id) REFERENCES conversations(source_id, conversation_id)
        );
        CREATE TABLE IF NOT EXISTS import_status (
            source_id TEXT PRIMARY KEY REFERENCES sources(id),
            status TEXT NOT NULL, indexed_conversations INTEGER NOT NULL DEFAULT 0,
            indexed_messages INTEGER NOT NULL DEFAULT 0, detail TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY, title TEXT NOT NULL, original_intent TEXT NOT NULL,
            parent_id TEXT REFERENCES projects(id), state TEXT NOT NULL DEFAULT 'concept',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS project_sources (
            project_id TEXT NOT NULL REFERENCES projects(id),
            source_id TEXT NOT NULL REFERENCES sources(id), relation TEXT NOT NULL,
            note TEXT NOT NULL DEFAULT '', PRIMARY KEY(project_id, source_id, relation)
        );
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
            predicate TEXT NOT NULL, value TEXT NOT NULL,
            source_id TEXT NOT NULL REFERENCES sources(id), status TEXT NOT NULL DEFAULT 'proposed',
            recorded_at TEXT NOT NULL, UNIQUE(project_id, predicate, value, source_id)
        );
        CREATE TABLE IF NOT EXISTS conflicts (
            id INTEGER PRIMARY KEY, first_claim_id INTEGER NOT NULL REFERENCES claims(id),
            second_claim_id INTEGER NOT NULL REFERENCES claims(id),
            status TEXT NOT NULL DEFAULT 'open', opened_at TEXT NOT NULL,
            UNIQUE(first_claim_id, second_claim_id)
        );
        CREATE TABLE IF NOT EXISTS external_references (
            id TEXT PRIMARY KEY, source_type TEXT NOT NULL,
            locator TEXT NOT NULL, limitation TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS project_external_refs (
            project_id TEXT NOT NULL REFERENCES projects(id),
            reference_id TEXT NOT NULL REFERENCES external_references(id),
            evidence_grade TEXT NOT NULL,
            PRIMARY KEY(project_id, reference_id)
        );
        CREATE TABLE IF NOT EXISTS project_reconstruction (
            project_id TEXT PRIMARY KEY REFERENCES projects(id),
            archive_group TEXT NOT NULL, source_coverage TEXT NOT NULL,
            original_37_membership TEXT NOT NULL,
            original_transcript_found INTEGER NOT NULL,
            verification_owed TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS events (
            seq INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL UNIQUE,
            occurred_at TEXT NOT NULL, kind TEXT NOT NULL, actor TEXT NOT NULL,
            authority TEXT NOT NULL, payload TEXT NOT NULL,
            previous_sha256 TEXT NOT NULL, event_sha256 TEXT NOT NULL
        );
        CREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON events
        BEGIN SELECT RAISE(ABORT, 'append_only_events'); END;
        CREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON events
        BEGIN SELECT RAISE(ABORT, 'append_only_events'); END;
    """)
    try:
        if db.is_file():
            db.chmod(0o600)
    except OSError:
        pass
    return conn


def utc() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def append_event(conn: sqlite3.Connection, kind: str, payload: dict,
                 *, actor: str = "local_index", authority: str = "local_metadata_only") -> str:
    # Must be called inside a transaction; callers never back-date decisions.
    previous = conn.execute("SELECT event_sha256 FROM events ORDER BY seq DESC LIMIT 1").fetchone()
    previous_sha = previous[0] if previous else "0" * 64
    event_id = str(uuid.uuid4())
    record = dict(event_id=event_id, occurred_at=utc(), kind=kind, actor=actor,
                  authority=authority, payload=payload, previous_sha256=previous_sha)
    digest = hashlib.sha256(canonical(record)).hexdigest()
    conn.execute("INSERT INTO events(event_id,occurred_at,kind,actor,authority,payload,previous_sha256,event_sha256) "
                 "VALUES(?,?,?,?,?,?,?,?)",
                 (event_id, record["occurred_at"], kind, actor, authority,
                  canonical(payload).decode("utf-8"), previous_sha, digest))
    return event_id


def ingest(conn: sqlite3.Connection, state: Path, source: Path, kind: str,
           label: str = "", origin_ref: str | None = None) -> dict:
    source = source.expanduser().resolve(strict=True)
    if not source.is_file():
        raise ValueError("source_must_be_a_regular_file")
    if source.stat().st_size > MAX_SOURCE_BYTES:
        raise ValueError("source_over_1_gib_limit")
    store = safe_state(state) / "originals"
    _private_dir(store)
    fd, temp_name = tempfile.mkstemp(prefix="cf0-import-", dir=store)
    h, n = hashlib.sha256(), 0
    try:
        with os.fdopen(fd, "wb") as out, source.open("rb") as inp:
            while data := inp.read(CHUNK):
                n += len(data)
                if n > MAX_SOURCE_BYTES:
                    raise ValueError("source_over_1_gib_limit")
                out.write(data)
                h.update(data)
            out.flush()
            os.fsync(out.fileno())
        digest = h.hexdigest()
        sid = "sha256:" + digest
        destination = store / digest[:2] / digest
        _private_dir(destination.parent)
        if not destination.exists():
            os.replace(temp_name, destination)
        # Same bytes but different origins remain individually visible.
        with conn:
            existing = conn.execute("SELECT sha256 FROM sources WHERE id=?", (sid,)).fetchone()
            if existing is None:
                conn.execute("INSERT INTO sources VALUES(?,?,?,?,?,?)",
                             (sid, digest, n, kind, utc(), str(destination.relative_to(safe_state(state)))))
                append_event(conn, "source_recovered", {"source_id":sid, "kind":kind, "bytes":n})
            conn.execute("INSERT OR IGNORE INTO source_origins(source_id,source_path,label,observed_at) VALUES(?,?,?,?)",
                         (sid, origin_ref or str(source), label, utc()))
        return dict(source_id=sid, sha256=digest, bytes=n,
                    duplicate=existing is not None, private_original=str(destination))
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def iter_json_array(stream: io.TextIOBase):
    """Bounded-memory streaming JSON array decoder, one ChatGPT conversation at a time."""
    decoder = json.JSONDecoder()
    buf = ""
    pos = 0
    eof = False
    total = 0

    def fill():
        nonlocal buf, eof, total, pos
        if eof:
            return False
        chunk = stream.read(CHUNK)
        if not chunk:
            eof = True
            return False
        total += len(chunk.encode("utf-8"))
        if total > MAX_EXPORT_BYTES:
            raise ValueError("export_unpacked_size_limit")
        if pos:
            buf = buf[pos:]
            pos = 0
        buf += chunk
        return True

    def seek():
        nonlocal pos
        while True:
            while pos < len(buf) and buf[pos].isspace():
                pos += 1
            if pos < len(buf):
                return buf[pos]
            if not fill():
                raise ValueError("incomplete_json_array")

    if seek() != "[":
        raise ValueError("expected_chatgpt_conversation_array")
    pos += 1
    def assert_only_trailing_whitespace():
        if buf[pos:].strip():
            raise ValueError("trailing_json_data")
        while remaining := stream.read(CHUNK):
            if remaining.strip():
                raise ValueError("trailing_json_data")

    if seek() == "]":
        pos += 1
        assert_only_trailing_whitespace()
        return
    while True:
        while True:
            try:
                value, end = decoder.raw_decode(buf, pos)
                if len(buf[pos:end].encode("utf-8")) > MAX_CONVERSATION_BYTES:
                    raise ValueError("single_conversation_exceeds_16_mib")
                pos = end
                break
            except json.JSONDecodeError as exc:
                if len(buf) - pos > MAX_CONVERSATION_BYTES:
                    raise ValueError("single_conversation_exceeds_16_mib") from exc
                if not fill():
                    raise ValueError("invalid_or_incomplete_conversation_json") from exc
        if not isinstance(value, dict):
            raise ValueError("conversation_is_not_object")
        yield value
        next_char = seek()
        if next_char == "]":
            pos += 1
            assert_only_trailing_whitespace()
            return
        if next_char != ",":
            raise ValueError("expected_conversation_separator")
        pos += 1
        if seek() == "]":
            raise ValueError("trailing_comma_in_json_array")


def _chat_stream(original: Path):
    if zipfile.is_zipfile(original):
        zf = zipfile.ZipFile(original)
        try:
            members = zf.infolist()
            if len(members) > MAX_ZIP_MEMBERS:
                raise ValueError("zip_member_count_limit")
            for item in members:
                if item.file_size > MAX_SOURCE_BYTES:
                    raise ValueError("zip_member_size_limit")
            candidates = [z for z in members if not z.is_dir() and
                          Path(z.filename.replace("\\", "/")).name == "conversations.json"]
            if len(candidates) != 1:
                raise ValueError("zip_requires_one_conversations_json")
            info = candidates[0]
            if info.file_size > MAX_EXPORT_BYTES:
                raise ValueError("export_unpacked_size_limit")
            # Never extract archive members into disk paths. Zip traversal is moot.
            with zf.open(info) as binary:
                with io.TextIOWrapper(binary, encoding="utf-8", errors="strict") as stream:
                    yield stream
        finally:
            zf.close()
    else:
        if original.stat().st_size > MAX_EXPORT_BYTES:
            raise ValueError("export_unpacked_size_limit")
        with original.open("r", encoding="utf-8") as stream:
            yield stream


_chat_stream = contextlib.contextmanager(_chat_stream)


def _text_parts(message: dict) -> str:
    content = message.get("content")
    if not isinstance(content, dict):
        return ""
    parts = content.get("parts")
    if isinstance(parts, list):
        return "\n".join(p for p in parts if isinstance(p, str))
    plain = content.get("text")
    return plain if isinstance(plain, str) else ""


def import_conversations(conn: sqlite3.Connection, state: Path, export_file: Path) -> dict:
    source = ingest(conn, state, export_file, kind="chatgpt_export")
    sid = source["source_id"]
    if (row := conn.execute("SELECT * FROM import_status WHERE source_id=?", (sid,)).fetchone()) and row["status"] == "complete":
        return dict(source_id=sid, conversations=row["indexed_conversations"], messages=row["indexed_messages"], reindexed=False)
    # The exact archive is saved before parsing; invalid exports remain recoverable.
    original = Path(source["private_original"])
    ncon, nmsg = 0, 0
    try:
        with _chat_stream(original) as stream:
            for index, obj in enumerate(iter_json_array(stream)):
                cid = obj.get("id")
                if not isinstance(cid, str) or not cid:
                    cid = "source-ordinal:" + str(index)
                title = obj.get("title") if isinstance(obj.get("title"), str) else "[untitled]"
                mapping = obj.get("mapping")
                if not isinstance(mapping, dict):
                    mapping = {}
                with conn:
                    conn.execute("INSERT OR IGNORE INTO conversations VALUES(?,?,?,?,?,?)",
                                 (sid,cid,title,str(obj.get("create_time")) if obj.get("create_time") is not None else None,
                                  str(obj.get("update_time")) if obj.get("update_time") is not None else None,index))
                    for key, node in mapping.items():
                        if not isinstance(node, dict) or not isinstance(key, str):
                            continue
                        message = node.get("message")
                        if not isinstance(message, dict):
                            continue
                        body = _text_parts(message)
                        if not body:
                            continue
                        mid = message.get("id")
                        if not isinstance(mid, str) or not mid:
                            mid = key
                        author = message.get("author")
                        role = author.get("role", "unknown") if isinstance(author, dict) else "unknown"
                        if not isinstance(role, str):
                            role = "unknown"
                        conn.execute("INSERT OR IGNORE INTO messages VALUES(?,?,?,?,?,?)",
                                     (sid,cid,mid,role[:40],str(message.get("create_time")) if message.get("create_time") is not None else None,body))
                ncon += 1
        count = conn.execute("SELECT COUNT(*) FROM conversations WHERE source_id=?", (sid,)).fetchone()[0]
        messages = conn.execute("SELECT COUNT(*) FROM messages WHERE source_id=?", (sid,)).fetchone()[0]
        with conn:
            conn.execute("INSERT OR REPLACE INTO import_status VALUES(?,?,?,?,?)",
                         (sid,"complete",count,messages,"text_messages_only; other modality preserved in original"))
            append_event(conn,"conversation_export_indexed",{"source_id":sid,"conversations":count,"messages":messages})
        return dict(source_id=sid,conversations=count,messages=messages,reindexed=True)
    except Exception as exc:
        indexed_conversations = conn.execute("SELECT COUNT(*) FROM conversations WHERE source_id=?",(sid,)).fetchone()[0]
        indexed_messages = conn.execute("SELECT COUNT(*) FROM messages WHERE source_id=?",(sid,)).fetchone()[0]
        with conn:
            conn.execute("INSERT OR REPLACE INTO import_status VALUES(?,?,?,?,?)",
                         (sid,"partial",indexed_conversations,indexed_messages,str(exc)[:150]))
        raise


def seed_reconstructed_atlas(conn: sqlite3.Connection, state: Path,
                             atlas_path: Path, addendum_path: Path,
                             atlas_origin: str | None = None,
                             addendum_origin: str | None = None) -> dict:
    """Create *unverified* project/source links from a two-file private reconstruction.

    This deliberately does not convert second-hand reconstructions into original
    conversation proof, owner-approved decisions, verified deployments or revenue.
    The two source files must describe exactly the same item IDs, titles and hash.
    Existing project identities are never overwritten.
    """
    atlas = json.loads(atlas_path.read_text(encoding="utf-8"))
    addendum = json.loads(addendum_path.read_text(encoding="utf-8"))
    if (atlas.get("schema") != "caveman_focus.project_atlas.v1"
            or addendum.get("schema") != "caveman_focus.project_atlas.provenance.v2"):
        raise ValueError("unsupported_reconstructed_atlas_schema")
    raw_sha = hashlib.sha256(atlas_path.read_bytes()).hexdigest()
    if addendum.get("source_json_sha256") != raw_sha:
        raise ValueError("provenance_addendum_atlas_hash_mismatch")
    if atlas.get("original_37_list_recovered") is not False or addendum.get("original_37_list_recovered") is not False:
        raise ValueError("original_archive_recovery_status_unverified")
    originals = atlas.get("items")
    covered = addendum.get("items")
    catalog = addendum.get("source_catalog")
    if not isinstance(originals, list) or not isinstance(covered, list) or not isinstance(catalog, dict):
        raise ValueError("invalid_reconstruction_source_shape")
    base = {item.get("id"):item for item in originals if isinstance(item,dict)}
    seen = {item.get("id"):item for item in covered if isinstance(item,dict)}
    if (len(base)!=len(originals) or len(seen)!=len(covered) or set(base)!=set(seen)
            or not all(isinstance(i,str) and PROJECT_ID.fullmatch(i) for i in base)):
        raise ValueError("reconstruction_ids_missing_or_duplicated")
    for identifier, item in seen.items():
        orig = base[identifier]
        if not isinstance(item.get("title"),str) or item["title"] != orig.get("title"):
            raise ValueError("reconstruction_title_mismatch:"+identifier)
        if item.get("historical_original_transcript_found") is not False or item.get("original_37_membership") != "not_established":
            raise ValueError("reconstruction_false_original_evidence:"+identifier)
        if (not isinstance(item.get("working_summary"),str)
                or not item["working_summary"].strip()
                or not isinstance(item.get("source_references"),list)):
            raise ValueError("reconstruction_missing_source_details:"+identifier)
        for ref in item["source_references"]:
            if not isinstance(ref,dict) or ref.get("source_id") not in catalog:
                raise ValueError("reconstruction_unknown_external_source:"+identifier)
    for identifier, item in seen.items():
        prior = conn.execute("SELECT title,original_intent FROM projects WHERE id=?", (identifier,)).fetchone()
        if prior and prior["title"] != item["title"]:
            raise ValueError("existing_project_identity_mismatch:"+identifier)

    # Preserve source bytes before indexing references; these are explicitly
    # *secondary* records, not an automatic privilege or ownership grant.
    atlas_source = ingest(conn,state,atlas_path,"secondary_reconstructed_atlas",origin_ref=atlas_origin)
    addendum_source = ingest(conn,state,addendum_path,"derived_provenance_addendum",origin_ref=addendum_origin)
    registered,linked,ref_links = 0,0,0
    with conn:
        for ref_id, ref in catalog.items():
            if not isinstance(ref_id,str) or not isinstance(ref,dict):
                raise ValueError("invalid_source_catalog_entry")
            row=conn.execute("INSERT OR IGNORE INTO external_references VALUES(?,?,?,?)",
                             (ref_id,str(ref.get("type","unknown")),str(ref.get("locator","unknown")),str(ref.get("limit","not established"))))
        for identifier, item in seen.items():
            existing=conn.execute("SELECT id FROM projects WHERE id=?",(identifier,)).fetchone()
            if existing is None:
                desc="[RECONSTRUCTED WORKING SUMMARY; original user wording unverified] " + item["working_summary"]
                conn.execute("INSERT INTO projects(id,title,original_intent,parent_id,state,created_at) VALUES(?,?,?,?,?,?)",
                             (identifier,item["title"],desc,None,"reconstructed_unverified",utc()))
                append_event(conn,"project_reconstructed",{"project_id":identifier,
                            "source_id":atlas_source["source_id"],"verified_original":False},
                             actor="private_atlas_ingest",authority="secondary_reconstruction_not_owner_approval")
                registered+=1
            for source_id in (atlas_source["source_id"],addendum_source["source_id"]):
                row=conn.execute("INSERT OR IGNORE INTO project_sources(project_id,source_id,relation) VALUES(?,?,?)",
                                 (identifier,source_id,"secondary"))
                linked+=int(bool(row.rowcount))
            row=conn.execute("INSERT OR IGNORE INTO project_reconstruction VALUES(?,?,?,?,?,?)",
                             (identifier,item.get("group","uncategorized"),
                              item.get("source_coverage","unknown"),
                              "not_established",0,item.get("verification_owed","original verification pending")))
            for ref in item["source_references"]:
                row=conn.execute("INSERT OR IGNORE INTO project_external_refs VALUES(?,?,?)",
                                 (identifier,ref["source_id"],ref.get("source_type","unknown")))
                ref_links+=int(bool(row.rowcount))
        if registered or linked or ref_links:
            append_event(conn,"reconstruction_seeded",{"project_count":len(seen),
                        "new_projects":registered,"external_source_references":ref_links,
                        "atlas_sha256":raw_sha,"original_37_recovered":False},
                         actor="private_atlas_ingest",authority="reconstruction_only")
    return dict(projects_seen=len(seen),new_projects=registered,private_source_links=linked,
                external_source_links=ref_links,external_catalog=len(catalog),
                atlas_source_id=atlas_source["source_id"],addendum_source_id=addendum_source["source_id"],
                source_coverage="mixed_secondary_and_metadata; original_37_not_recovered")


def add_project(conn: sqlite3.Connection, identifier: str, title: str, intent: str, parent: str | None = None) -> dict:
    if not PROJECT_ID.fullmatch(identifier):
        raise ValueError("invalid_project_id")
    if not title.strip() or not intent.strip():
        raise ValueError("project_title_and_user_intent_required")
    with conn:
        if parent and not conn.execute("SELECT 1 FROM projects WHERE id=?", (parent,)).fetchone():
            raise ValueError("unknown_parent_project")
        conn.execute("INSERT INTO projects(id,title,original_intent,parent_id,created_at) VALUES(?,?,?,?,?)",
                     (identifier,title.strip(),intent.strip(),parent,utc()))
        event_id = append_event(conn,"project_created",{"project_id":identifier,"parent_id":parent,"status":"concept"},
                                actor="owner_supplied_project_record", authority="explicit_local_invocation")
    return dict(project_id=identifier,event_id=event_id)


def link_source(conn: sqlite3.Connection, project: str, source_id: str, relation: str) -> dict:
    if relation not in {"primary", "secondary", "related", "historical"}:
        raise ValueError("invalid_source_relation")
    with conn:
        if not conn.execute("SELECT 1 FROM projects WHERE id=?",(project,)).fetchone():
            raise ValueError("unknown_project")
        if not conn.execute("SELECT 1 FROM sources WHERE id=?",(source_id,)).fetchone():
            raise ValueError("unknown_source")
        result=conn.execute("INSERT OR IGNORE INTO project_sources(project_id,source_id,relation) VALUES(?,?,?)",
                            (project,source_id,relation))
        event_id=None
        if result.rowcount:
            event_id=append_event(conn,"source_linked",{"project_id":project,"source_id":source_id,"relation":relation},
                                  actor="owner_supplied_source_link",authority="explicit_local_invocation")
    return dict(linked=bool(result.rowcount),event_id=event_id)


def add_claim(conn: sqlite3.Connection, project: str, predicate: str, value: str, source_id: str) -> dict:
    if not predicate.strip() or not value.strip():
        raise ValueError("claim_value_and_predicate_required")
    with conn:
        if not conn.execute("SELECT 1 FROM projects WHERE id=?",(project,)).fetchone():
            raise ValueError("unknown_project")
        if not conn.execute("SELECT 1 FROM sources WHERE id=?",(source_id,)).fetchone():
            raise ValueError("unknown_source")
        old = conn.execute("SELECT id,value FROM claims WHERE project_id=? AND predicate=?",
                           (project,predicate)).fetchall()
        result=conn.execute("INSERT OR IGNORE INTO claims(project_id,predicate,value,source_id,recorded_at) VALUES(?,?,?,?,?)",
                            (project,predicate,value,source_id,utc()))
        current=conn.execute("SELECT id FROM claims WHERE project_id=? AND predicate=? AND value=? AND source_id=?",
                             (project,predicate,value,source_id)).fetchone()[0]
        new_conflicts=[]
        if result.rowcount:
            append_event(conn,"claim_proposed",{"project_id":project,"predicate":predicate,"claim_id":current,"source_id":source_id},
                         actor="owner_supplied_claim",authority="unverified_source_claim")
            for earlier in old:
                if earlier["value"] != value:
                    first,second=sorted((earlier["id"],current))
                    row=conn.execute("INSERT OR IGNORE INTO conflicts(first_claim_id,second_claim_id,opened_at) VALUES(?,?,?)",
                                     (first,second,utc()))
                    if row.rowcount:
                        new_conflicts.append([first,second])
                        append_event(conn,"conflict_opened",{"project_id":project,"predicate":predicate,"claims":[first,second]},
                                     actor="local_conflict_detector",authority="requires_owner_review")
    return dict(claim_id=current,created=bool(result.rowcount),open_conflicts=new_conflicts)


def search(conn: sqlite3.Connection, phrase: str, limit: int = 15) -> list[dict]:
    if not phrase.strip():
        raise ValueError("search_phrase_required")
    # Exact substring matching; does not infer project links or summarize contents.
    escaped = phrase.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    rows=conn.execute("""SELECT m.source_id, m.conversation_id, c.title, m.message_id,
                                 m.role, m.sent_at, m.body
                           FROM messages m JOIN conversations c USING(source_id,conversation_id)
                           WHERE m.body LIKE ? ESCAPE '\\' ORDER BY c.ordinal, m.message_id LIMIT ?""",
                      ("%" + escaped + "%",min(100,max(1,limit)))).fetchall()
    output=[]
    for r in rows:
        body=r["body"]
        hit=body.casefold().find(phrase.casefold())
        start=max(0,hit-75)
        output.append({"source_id":r["source_id"],"conversation_id":r["conversation_id"],
                       "title":r["title"],"message_id":r["message_id"],"role":r["role"],
                       "sent_at":r["sent_at"],"excerpt":body[start:start+200]})
    return output


def audit(conn: sqlite3.Connection, *, full_hash: bool=False) -> dict:
    previous="0"*64
    for row in conn.execute("SELECT * FROM events ORDER BY seq ASC"):
        record=dict(event_id=row["event_id"],occurred_at=row["occurred_at"],kind=row["kind"],
                    actor=row["actor"],authority=row["authority"],payload=json.loads(row["payload"]),
                    previous_sha256=row["previous_sha256"])
        if previous != row["previous_sha256"] or hashlib.sha256(canonical(record)).hexdigest()!=row["event_sha256"]:
            raise ValueError("event_chain_invalid_at_"+str(row["seq"]))
        previous=row["event_sha256"]
    all_sources=conn.execute("SELECT * FROM sources").fetchall()
    for s in all_sources:
        path=Path(s["archive_path"])
        if not path.is_absolute():
            path = Path(conn.execute("PRAGMA database_list").fetchone()[2]).parent / path
        if not path.is_file():
            raise ValueError("missing_private_original_"+s["id"])
        if full_hash:
            h=hashlib.sha256()
            with path.open("rb") as f:
                while chunk:=f.read(CHUNK):h.update(chunk)
            if h.hexdigest()!=s["sha256"]:
                raise ValueError("original_hash_changed_"+s["id"])
    def count(table):
        return conn.execute("SELECT COUNT(*) FROM "+table).fetchone()[0]
    return dict(sources=count("sources"),origins=count("source_origins"),
                conversations=count("conversations"),messages=count("messages"),
                projects=count("projects"),project_source_links=count("project_sources"),
                project_external_refs=count("project_external_refs"),
                reconstructed_unverified=count("project_reconstruction"),
                external_source_catalog=count("external_references"),
                claims=count("claims"),open_conflicts=conn.execute("SELECT COUNT(*) FROM conflicts WHERE status='open'").fetchone()[0],
                events=count("events"),chain_valid=True,originals_present=True,
                original_hashes_checked=full_hash,scope="private_local_only")


def backup_private(conn: sqlite3.Connection, state: Path, archive: Path) -> dict:
    """Create a consistent portable private snapshot with hash manifest.

    Unlike publishing a public report, this archive contains complete private
    original sources and searchable chat text. It is NEVER auto-uploaded.
    """
    state = safe_state(state)
    output = archive.expanduser().resolve()
    if output == ROOT or ROOT in output.parents or state == output or state in output.parents:
        raise ValueError("backup_must_be_outside_public_repo_and_private_store")
    if not output.parent.is_dir():
        raise ValueError("backup_destination_parent_missing")
    if output.exists():
        raise ValueError("backup_destination_exists_use_versioned_name")
    audit(conn, full_hash=True)
    with tempfile.TemporaryDirectory(prefix="cf0-backup-snapshot-") as temp:
        snapshot = Path(temp) / "continuity.sqlite3"
        with contextlib.closing(sqlite3.connect(snapshot)) as copy:
            conn.backup(copy)
        files = {"continuity.sqlite3":snapshot}
        for row in conn.execute("SELECT archive_path FROM sources"):
            relative=Path(row["archive_path"])
            if relative.is_absolute():
                raise ValueError("legacy_absolute_original_path_requires_migration")
            path=(state / relative).resolve()
            if state not in path.parents or not path.is_file():
                raise ValueError("source_original_outside_private_store")
            files[relative.as_posix()] = path
        manifest={"schema":"cf0.private_continuity_backup.v1","created_at":utc(),
                  "file_count":len(files),"files":{}}
        for name,path in sorted(files.items()):
            h=hashlib.sha256()
            with path.open("rb") as f:
                while data:=f.read(CHUNK):h.update(data)
            manifest["files"][name]={"size":path.stat().st_size,"sha256":h.hexdigest()}
        fd,tmp=tempfile.mkstemp(prefix=".cf0-private-backup-",suffix=".zip",dir=output.parent)
        os.close(fd)
        try:
            with zipfile.ZipFile(tmp,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
                for name,path in sorted(files.items()):z.write(path,arcname=name)
                z.writestr("manifest.json",canonical(manifest))
            if output.exists():
                raise ValueError("backup_destination_created_concurrently")
            os.replace(tmp,output)
        finally:
            if os.path.exists(tmp):os.unlink(tmp)
    return {"backup_created":str(output),"files":len(files),
            "full_hash_audit":True,"scope":"private_complete_originals_not_public"}


def restore_private(archive: Path, state: Path) -> dict:
    """Restore a verified snapshot to a NEW private directory; never overwrite."""
    state=safe_state(state)
    if state.exists():
        raise ValueError("restore_target_must_not_exist")
    _private_dir(state.parent)
    archive=archive.expanduser().resolve(strict=True)
    if not zipfile.is_zipfile(archive):
        raise ValueError("not_a_backup_zip")
    with zipfile.ZipFile(archive) as z:
        infos=z.infolist()
        if len(infos)>MAX_ZIP_MEMBERS:
            raise ValueError("backup_member_limit")
        names=[info.filename for info in infos]
        if len(names)!=len(set(names)) or "manifest.json" not in names:
            raise ValueError("invalid_backup_members")
        for info in infos:
            name=Path(info.filename.replace("\\","/"))
            if (info.is_dir() or name.is_absolute() or '..' in name.parts
                    or '\\' in info.filename or stat.S_ISLNK(info.external_attr >> 16)):
                raise ValueError("unsafe_backup_entry")
        if z.getinfo("manifest.json").file_size > 2_000_000:
            raise ValueError("backup_manifest_too_large")
        manifest=json.loads(z.read("manifest.json"))
        if manifest.get("schema")!="cf0.private_continuity_backup.v1":
            raise ValueError("unsupported_backup_schema")
        expected=manifest.get("files")
        if (not isinstance(expected,dict) or set(expected)!=(set(names)-{"manifest.json"})
                or "continuity.sqlite3" not in expected):
            raise ValueError("backup_manifest_file_mismatch")
        if sum(int(e.get("size",0)) for e in expected.values())>2_147_483_648:
            raise ValueError("backup_size_limit")
        temp=Path(tempfile.mkdtemp(prefix="cf0-restore-",dir=state.parent))
        try:
            for name,metadata in expected.items():
                info=z.getinfo(name)
                if info.file_size>MAX_SOURCE_BYTES or info.file_size!=metadata.get("size"):
                    raise ValueError("backup_entry_size_mismatch")
                target=temp / name
                target.parent.mkdir(parents=True,exist_ok=True)
                h=hashlib.sha256()
                with z.open(info) as src, target.open("wb") as out:
                    n=0
                    while data:=src.read(CHUNK):
                        n+=len(data)
                        if n>info.file_size:raise ValueError("backup_entry_size_mismatch")
                        h.update(data);out.write(data)
                if n!=info.file_size or h.hexdigest()!=metadata.get("sha256"):
                    raise ValueError("backup_entry_digest_mismatch")
            with contextlib.closing(sqlite3.connect(temp/"continuity.sqlite3")) as recovered:
                recovered.row_factory=sqlite3.Row
                recovered.execute("PRAGMA foreign_keys=ON")
                validation=audit(recovered,full_hash=True)
            if state.exists():
                raise ValueError("restore_target_created_concurrently")
            os.replace(temp,state)
            temp=None
        finally:
            if temp is not None and temp.exists():shutil.rmtree(temp)
    return {"restored_to":str(state),"verified_manifest":True,
            "full_originals_hash_checked":True,"audit":validation}


def main(argv: list[str] | None=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir",type=Path,default=default_state(),help="PRIVATE local directory outside public git repo")
    sub=parser.add_subparsers(dest="action",required=True)
    sub.add_parser("init")
    s=sub.add_parser("ingest");s.add_argument("path",type=Path);s.add_argument("--kind",default="source_file");s.add_argument("--label",default="");s.add_argument("--origin",default=None)
    s=sub.add_parser("import-chatgpt");s.add_argument("path",type=Path)
    s=sub.add_parser("search");s.add_argument("phrase");s.add_argument("--limit",type=int,default=15)
    s=sub.add_parser("seed-atlas");s.add_argument("atlas",type=Path);s.add_argument("addendum",type=Path);s.add_argument("--atlas-origin");s.add_argument("--addendum-origin")
    s=sub.add_parser("add-project");s.add_argument("id");s.add_argument("title");s.add_argument("--intent",required=True);s.add_argument("--parent")
    s=sub.add_parser("link-source");s.add_argument("project_id");s.add_argument("source_id");s.add_argument("--relation",choices=["primary","secondary","related","historical"],default="primary")
    s=sub.add_parser("add-claim");s.add_argument("project_id");s.add_argument("predicate");s.add_argument("value");s.add_argument("--source",required=True)
    s=sub.add_parser("audit");s.add_argument("--full-hash",action="store_true")
    s=sub.add_parser("backup");s.add_argument("output",type=Path)
    s=sub.add_parser("restore");s.add_argument("archive",type=Path)
    args=parser.parse_args(argv)
    try:
        state=safe_state(args.state_dir)
        if args.action=="restore":
            out=restore_private(args.archive,state)
        else:
            with contextlib.closing(open_db(state)) as conn:
                out=run_private_action(conn,args,state)
        print(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2))
        return 0
    except (ValueError,sqlite3.Error,FileNotFoundError,UnicodeError,zipfile.BadZipFile) as exc:
        print("CF0_CONTINUITY_ERROR:"+str(exc),file=sys.stderr)
        return 2


def run_private_action(conn: sqlite3.Connection,args,state:Path):
            if args.action=="init":out=dict(private_state_created=True)
            elif args.action=="ingest":out=ingest(conn,state,args.path,args.kind,args.label,args.origin)
            elif args.action=="import-chatgpt":out=import_conversations(conn,state,args.path)
            elif args.action=="search":out=search(conn,args.phrase,args.limit)
            elif args.action=="seed-atlas":out=seed_reconstructed_atlas(conn,state,args.atlas,args.addendum,args.atlas_origin,args.addendum_origin)
            elif args.action=="add-project":out=add_project(conn,args.id,args.title,args.intent,args.parent)
            elif args.action=="link-source":out=link_source(conn,args.project_id,args.source_id,args.relation)
            elif args.action=="add-claim":out=add_claim(conn,args.project_id,args.predicate,args.value,args.source)
            elif args.action=="backup":out=backup_private(conn,state,args.output)
            else:out=audit(conn,full_hash=args.full_hash)
            return out


if __name__=="__main__":
    raise SystemExit(main())