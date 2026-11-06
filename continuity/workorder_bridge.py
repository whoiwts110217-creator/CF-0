#!/usr/bin/env python3
"""Read-only CF-200 snapshots and explicit project/work-order relationships.

Never changes the public CF-200 registry, its evidence/events or project statuses.
A suggested relationship is NOT a confirmed project completion or owner decision.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

from . import local_index as c

# These are *suggestions*, not authorizations to link or merge. Single, strong
# stream families only; ambiguous streams deliberately have no automatic guess.
SUGGESTED_STREAMS = {
    "chat_command": "AUTO-03",
    "sidecar": "AUTO-05",
    "receipt": "AUTO-12",
    "priority_logic": "AUTO-11",
    "archive": "CF-ARCH",
}
VALID_RELATIONS = frozenset({"implements", "supports", "related"})


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS cf200_snapshots (
        source_id TEXT PRIMARY KEY REFERENCES sources(id),
        completed INTEGER NOT NULL, target INTEGER NOT NULL,
        imported_at TEXT NOT NULL, scope TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS cf200_orders (
        source_id TEXT NOT NULL REFERENCES cf200_snapshots(source_id),
        task_id TEXT NOT NULL, stream TEXT NOT NULL,
        title TEXT NOT NULL, status TEXT NOT NULL,
        evidence_sha256 TEXT NOT NULL, PRIMARY KEY(source_id, task_id)
    );
    CREATE TABLE IF NOT EXISTS cf200_project_links (
        source_id TEXT NOT NULL, task_id TEXT NOT NULL,
        project_id TEXT NOT NULL REFERENCES projects(id),
        relation TEXT NOT NULL, event_id TEXT NOT NULL REFERENCES events(event_id),
        PRIMARY KEY(source_id, task_id, project_id, relation),
        FOREIGN KEY(source_id,task_id) REFERENCES cf200_orders(source_id,task_id)
    );
    CREATE TRIGGER IF NOT EXISTS cf200_snapshots_no_update BEFORE UPDATE ON cf200_snapshots
        BEGIN SELECT RAISE(ABORT,'immutable_workorder_snapshot'); END;
    CREATE TRIGGER IF NOT EXISTS cf200_snapshots_no_delete BEFORE DELETE ON cf200_snapshots
        BEGIN SELECT RAISE(ABORT,'immutable_workorder_snapshot'); END;
    CREATE TRIGGER IF NOT EXISTS cf200_orders_no_update BEFORE UPDATE ON cf200_orders
        BEGIN SELECT RAISE(ABORT,'immutable_workorder_snapshot'); END;
    CREATE TRIGGER IF NOT EXISTS cf200_orders_no_delete BEFORE DELETE ON cf200_orders
        BEGIN SELECT RAISE(ABORT,'immutable_workorder_snapshot'); END;
    CREATE TRIGGER IF NOT EXISTS cf200_links_no_update BEFORE UPDATE ON cf200_project_links
        BEGIN SELECT RAISE(ABORT,'immutable_project_workorder_link'); END;
    CREATE TRIGGER IF NOT EXISTS cf200_links_no_delete BEFORE DELETE ON cf200_project_links
        BEGIN SELECT RAISE(ABORT,'immutable_project_workorder_link'); END;
    """)


def validate_registry(value: object) -> dict:
    if not isinstance(value, dict) or not isinstance(value.get("tasks"), list):
        raise ValueError("invalid_cf200_registry_shape")
    tasks = value["tasks"]
    target = value.get("target")
    completed = value.get("completed")
    if type(target) is not int or type(completed) is not int or target < 1 or target > 10000:
        raise ValueError("invalid_cf200_counts")
    if len(tasks) != target:
        raise ValueError("cf200_target_tasks_mismatch")
    task_ids = set()
    count = 0
    for x in tasks:
        if not isinstance(x, dict):
            raise ValueError("cf200_task_not_object")
        identifier, stream, title, status = (x.get(key) for key in ("id","stream","title","status"))
        if (not isinstance(identifier,str) or not identifier.startswith("CF-")
                or not identifier[3:].isdigit() or identifier in task_ids):
            raise ValueError("duplicate_or_invalid_cf200_id")
        if (not isinstance(stream,str) or not stream.strip()
                or not isinstance(title,str) or not title.strip()
                or status not in {"planned","verified"}):
            raise ValueError("invalid_cf200_task_fields")
        evidence = x.get("evidence")
        if status == "verified" and (not isinstance(evidence,str) or not evidence.strip()):
            raise ValueError("verified_cf200_task_without_evidence")
        task_ids.add(identifier)
        count += status == "verified"
    if count != completed:
        raise ValueError("cf200_completed_count_mismatch")
    return {"tasks":tasks,"target":target,"completed":count}


def import_registry(conn: sqlite3.Connection, state: Path, source_file: Path,
                    *, origin: str | None = None) -> dict:
    # Validate all status/evidence constraints before preserving any source.
    # A data file is evidence, never a policy or arbitrary executable script.
    if source_file.stat().st_size > 10_000_000:
        raise ValueError("cf200_registry_size_limit")
    obj = validate_registry(json.loads(source_file.read_text(encoding="utf-8")))
    ensure_schema(conn)
    source = c.ingest(conn,state,source_file,"cf200_registry_snapshot",origin_ref=origin)
    sid = source["source_id"]
    if conn.execute("SELECT 1 FROM cf200_snapshots WHERE source_id=?",(sid,)).fetchone():
        return {"source_id":sid,"imported":False,"orders":obj["target"],
                "verified_source_statuses":obj["completed"],"project_links_added":0}
    with conn:
        conn.execute("INSERT INTO cf200_snapshots VALUES(?,?,?,?,?)",
                     (sid,obj["completed"],obj["target"],c.utc(),"source_snapshot_not_project_completion"))
        conn.executemany("INSERT INTO cf200_orders VALUES(?,?,?,?,?,?)",
                         [(sid,x["id"],x["stream"],x["title"],x["status"],
                           hashlib.sha256((x.get("evidence") or "").encode("utf-8")).hexdigest())
                          for x in obj["tasks"]])
        c.append_event(conn,"cf200_registry_snapshot_imported",
                       {"source_id":sid,"work_orders":obj["target"],
                        "verified_source_statuses":obj["completed"],
                        "owner_acceptance_inferred":False,"project_completion_inferred":False},
                       actor="local_workorder_bridge", authority="source_evidence_only")
    return {"source_id":sid,"imported":True,"orders":obj["target"],
            "verified_source_statuses":obj["completed"],"project_links_added":0}


def suggest_links(conn: sqlite3.Connection, source_id: str, *, limit: int=200) -> dict:
    ensure_schema(conn)
    if not conn.execute("SELECT 1 FROM cf200_snapshots WHERE source_id=?",(source_id,)).fetchone():
        raise ValueError("unknown_cf200_snapshot")
    rows = conn.execute("SELECT * FROM cf200_orders WHERE source_id=? ORDER BY task_id LIMIT ?",
                        (source_id,max(1,min(10000,limit)))).fetchall()
    matched=[]
    ambiguous=[]
    for x in rows:
        project_id = SUGGESTED_STREAMS.get(x["stream"])
        if project_id and conn.execute("SELECT 1 FROM projects WHERE id=?",(project_id,)).fetchone():
            matched.append({"task_id":x["task_id"],"stream":x["stream"],
                            "project_id":project_id,"status":"suggestion_only_requires_explicit_review"})
        else:
            ambiguous.append({"task_id":x["task_id"],"stream":x["stream"],
                              "status":"no_unambiguous_project_suggestion"})
    return {"source_id":source_id,"suggestions":matched,"unmapped":ambiguous,
            "all_suggestions_unapproved":True,"project_completion_inferred":False}


def link_workorder(conn: sqlite3.Connection, source_id: str, task_id: str,
                   project_id: str, relation: str, *, reason: str) -> dict:
    ensure_schema(conn)
    if relation not in VALID_RELATIONS:
        raise ValueError("unsupported_project_workorder_relation")
    if not isinstance(reason,str) or len(reason.strip()) < 15:
        raise ValueError("specific_owner_review_reason_required")
    if not conn.execute("SELECT 1 FROM cf200_orders WHERE source_id=? AND task_id=?",
                        (source_id,task_id)).fetchone():
        raise ValueError("unknown_cf200_task_in_snapshot")
    if not conn.execute("SELECT 1 FROM projects WHERE id=?",(project_id,)).fetchone():
        raise ValueError("unknown_project")
    prior=conn.execute("SELECT event_id FROM cf200_project_links WHERE source_id=? AND task_id=? AND project_id=? AND relation=?",
                       (source_id,task_id,project_id,relation)).fetchone()
    if prior:
        return {"linked":False,"event_id":prior["event_id"],"project_completed":False}
    with conn:
        event_id=c.append_event(conn,"cf200_project_link_explicit",
                                {"source_id":source_id,"task_id":task_id,
                                 "project_id":project_id,"relation":relation,
                                 "review_reason":reason.strip(),"project_completed":False},
                                actor="explicit_local_link_invocation",
                                authority="review_required_not_authorization_for_other_actions")
        conn.execute("INSERT INTO cf200_project_links VALUES(?,?,?,?,?)",
                     (source_id,task_id,project_id,relation,event_id))
    return {"linked":True,"event_id":event_id,"project_completed":False}


def snapshot_diff(conn: sqlite3.Connection, before: str, after: str) -> dict:
    ensure_schema(conn)
    first={x["task_id"]:x for x in conn.execute("SELECT * FROM cf200_orders WHERE source_id=?",(before,))}
    last={x["task_id"]:x for x in conn.execute("SELECT * FROM cf200_orders WHERE source_id=?",(after,))}
    if not first or not last:
        raise ValueError("unknown_cf200_snapshot")
    changed=[]
    for task_id in sorted(set(first)&set(last)):
        a,b=first[task_id],last[task_id]
        if a["status"]!=b["status"] or a["evidence_sha256"]!=b["evidence_sha256"]:
            changed.append({"task_id":task_id,"before":a["status"],"after":b["status"],
                            "evidence_changed":a["evidence_sha256"]!=b["evidence_sha256"],
                            "review_required":True})
    return {"from_source":before,"to_source":after,"changed":changed,
            "missing_tasks":sorted(set(first)-set(last)),
            "new_tasks":sorted(set(last)-set(first)),
            "source_observations_not_project_completion":True}


def audit_workorders(conn: sqlite3.Connection) -> dict:
    ensure_schema(conn)
    count=lambda table:conn.execute("SELECT COUNT(*) FROM "+table).fetchone()[0]
    bad=conn.execute("""SELECT COUNT(*) FROM cf200_project_links l
          LEFT JOIN cf200_orders w ON w.source_id=l.source_id AND w.task_id=l.task_id
          LEFT JOIN projects p ON p.id=l.project_id
          LEFT JOIN events e ON e.event_id=l.event_id
          WHERE w.task_id IS NULL OR p.id IS NULL OR e.event_id IS NULL""").fetchone()[0]
    if bad:
        raise ValueError("invalid_workorder_project_link")
    return {"cf200_snapshots":count("cf200_snapshots"),
            "cf200_order_versions":count("cf200_orders"),
            "explicit_project_links":count("cf200_project_links"),
            "link_integrity":True,"not_an_external_owner_approval":True}


def main(argv=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--state-dir",type=Path,default=c.default_state())
    sub=p.add_subparsers(dest="command",required=True)
    imp=sub.add_parser("import-registry")
    imp.add_argument("path",type=Path);imp.add_argument("--origin")
    suggest=sub.add_parser("suggest-links");suggest.add_argument("source_id");suggest.add_argument("--limit",type=int,default=200)
    link=sub.add_parser("link-workorder");link.add_argument("source_id");link.add_argument("task_id");link.add_argument("project_id");link.add_argument("--relation",choices=sorted(VALID_RELATIONS),required=True);link.add_argument("--reason",required=True)
    diff=sub.add_parser("compare");diff.add_argument("before");diff.add_argument("after")
    sub.add_parser("audit")
    args=p.parse_args(argv)
    try:
        state=c.safe_state(args.state_dir)
        with contextlib.closing(c.open_db(state)) as conn:
            if args.command=="import-registry":out=import_registry(conn,state,args.path,origin=args.origin)
            elif args.command=="suggest-links":out=suggest_links(conn,args.source_id,limit=args.limit)
            elif args.command=="link-workorder":out=link_workorder(conn,args.source_id,args.task_id,args.project_id,args.relation,reason=args.reason)
            elif args.command=="compare":out=snapshot_diff(conn,args.before,args.after)
            else:out=audit_workorders(conn)
        print(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True));return 0
    except (ValueError,FileNotFoundError,UnicodeError,sqlite3.Error,json.JSONDecodeError) as exc:
        print("CF0_WORKORDER_BRIDGE_ERROR:"+str(exc),file=sys.stderr);return 2

if __name__=="__main__":raise SystemExit(main())