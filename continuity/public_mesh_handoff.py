#!/usr/bin/env python3
"""CF-MESH-001 public handoff chain: offline, source-only, fail-closed.

No ChatGPT session authentication, public publishing, browser control, private
transcripts, money movement or HP permission. Proposals are NOT acknowledgments
from another chat. GitHub writes must separately use authenticated SHA guards.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from .public_topic_router import ROOT, BOOT, GRAPH_PATH, GraphError, route_topic, validate_graph

SCHEMA = "cf0.mesh.handoff_event.v1"
LEDGER_PATH = ROOT / "docs/mesh/handoff_events.jsonl"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
EVENT_ID = re.compile(r"^MESH-[0-9]{6}$")
KINDS = {"handoff", "readback"}
WORKERS = {"A", "B", "C"}
MAX_EVENTS = 10000
MAX_LINE = 6000
EVENT_FIELDS = {
    "schema", "event_id", "kind", "worker_label", "active_topic_id",
    "related_ids", "read_main_commit", "read_graph_blob_sha1",
    "read_master_blob_shas", "topic_source_path", "topic_source_blob_sha1",
    "previous_event_sha256", "consumes_sha256", "evidence_scope",
    "provider_origin_verified", "event_sha256",
}


class HandoffError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")


def git_blob_sha(content):
    raw = content.replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()


def digest_event(event):
    return hashlib.sha256(canonical({
        k: v for k, v in event.items() if k != "event_sha256"
    })).hexdigest()


def _sha(value, size):
    pat = HEX40 if size == 40 else HEX64
    return type(value) is str and bool(pat.fullmatch(value))


def _related(topic, graph):
    route = route_topic(graph, topic, limit=32)
    return {item["id"] for item in route["related_context_only"]}


def validate_events(raw, graph, *, root=None):
    """Validate only public source claims; do not assert session provenance."""
    nodes = validate_graph(graph)
    if type(raw) is not str or len(raw.encode("utf-8")) > 5_000_000:
        raise HandoffError("invalid_or_oversized_ledger")
    lines = raw.splitlines()
    if len(lines) > MAX_EVENTS:
        raise HandoffError("too_many_handoffs")
    prior_hash = "0" * 64
    seen_ids = set()
    by_digest = {}
    acknowledged = set()
    result = []
    for lineno, line in enumerate(lines, 1):
        if not line.strip():
            raise HandoffError("blank_or_invalid_event_line")
        if len(line.encode("utf-8")) > MAX_LINE:
            raise HandoffError("oversized_event_line")
        try:
            event = json.loads(line)
        except (ValueError, TypeError) as exc:
            raise HandoffError("invalid_jsonl_event") from exc
        if type(event) is not dict or set(event) != EVENT_FIELDS:
            raise HandoffError("invalid_event_fields")
        if event["schema"] != SCHEMA or type(event["kind"]) is not str or event["kind"] not in KINDS:
            raise HandoffError("invalid_event_kind")
        if type(event["worker_label"]) is not str or event["worker_label"] not in WORKERS:
            raise HandoffError("unknown_worker_label")
        eid = event["event_id"]
        if type(eid) is not str or not EVENT_ID.fullmatch(eid) or eid in seen_ids:
            raise HandoffError("invalid_or_duplicate_event_id")
        if eid != f"MESH-{lineno:06d}":
            raise HandoffError("event_id_out_of_sequence")
        seen_ids.add(eid)
        topic = event["active_topic_id"]
        if type(topic) is not str or topic not in nodes:
            raise HandoffError("unknown_active_topic")
        if event["topic_source_path"] != nodes[topic]["source"]:
            raise HandoffError("topic_source_mismatch")
        refs = event["related_ids"]
        if type(refs) is not list or len(refs) > 32 or any(
            type(x) is not str for x in refs
        ) or len(refs) != len(set(refs)) or not set(refs).issubset(_related(topic, graph)):
            raise HandoffError("unrelated_context_or_topic_drift")
        for field in ("read_main_commit", "read_graph_blob_sha1",
                      "topic_source_blob_sha1"):
            if not _sha(event[field], 40):
                raise HandoffError("invalid_git_source_sha")
        blobs = event["read_master_blob_shas"]
        if type(blobs) is not list or len(blobs) != len(BOOT) or any(
            not _sha(x, 40) for x in blobs
        ):
            raise HandoffError("invalid_master_source_shas")
        if event["previous_event_sha256"] != prior_hash:
            raise HandoffError("chain_parent_mismatch")
        if event["evidence_scope"] != "github_source_only" or event["provider_origin_verified"] is not False:
            raise HandoffError("unverified_provider_claim")
        consume = event["consumes_sha256"]
        if event["kind"] == "handoff":
            if consume is not None:
                raise HandoffError("handoff_cannot_acknowledge")
        else:
            if not _sha(consume, 64) or consume not in by_digest:
                raise HandoffError("readback_missing_prior_handoff")
            parent = by_digest[consume]
            if parent["kind"] != "handoff" or parent["active_topic_id"] != topic:
                raise HandoffError("readback_topic_mismatch")
            if parent["worker_label"] == event["worker_label"]:
                raise HandoffError("self_readback_not_cross_worker")
            ack_key = (consume, event["worker_label"])
            if ack_key in acknowledged:
                raise HandoffError("duplicate_readback_label")
            acknowledged.add(ack_key)
        computed = digest_event(event)
        if event["event_sha256"] != computed:
            raise HandoffError("event_hash_mismatch")
        prior_hash = computed
        by_digest[computed] = event
        result.append(event)
    return {
        "schema": "cf0.mesh.handoff_audit.v1",
        "valid": True,
        "events": len(result),
        "handoffs": sum(e["kind"] == "handoff" for e in result),
        "readbacks": sum(e["kind"] == "readback" for e in result),
        "last_event_sha256": prior_hash,
        "provider_origin_verified": False,
        "live_three_chat_acceptance": False,
        "events_data": result,
    }


def new_event(raw, graph, *, kind, worker, topic, read_main_commit,
              consumes=None, root=ROOT):
    """Pure proposal. Caller must separately write with GitHub blob SHA guard."""
    if kind not in KINDS or worker not in WORKERS or topic not in validate_graph(graph):
        raise HandoffError("invalid_proposal_scope")
    if not _sha(read_main_commit, 40):
        raise HandoffError("invalid_read_head")
    previous = validate_events(raw, graph)
    if len(previous["events_data"]) >= MAX_EVENTS:
        raise HandoffError("ledger_full")
    if kind == "handoff" and consumes is not None:
        raise HandoffError("unexpected_consume_ref")
    if kind == "readback" and not _sha(consumes, 64):
        raise HandoffError("readback_requires_digest")
    route = route_topic(graph, topic, root=root, limit=8)
    root = Path(root)
    events = previous["events_data"]
    new = {
        "schema": SCHEMA, "event_id": f"MESH-{len(events) + 1:06d}",
        "kind": kind, "worker_label": worker, "active_topic_id": topic,
        "related_ids": [x["id"] for x in route["related_context_only"]],
        "read_main_commit": read_main_commit,
        "read_graph_blob_sha1": git_blob_sha((root / "docs/PUBLIC_CONTEXT_GRAPH.json").read_bytes()),
        "read_master_blob_shas": [
            git_blob_sha((root / path).read_bytes()) for path in BOOT
        ],
        "topic_source_path": route["source_of_focus"],
        "topic_source_blob_sha1": git_blob_sha((root / route["source_of_focus"]).read_bytes()),
        "previous_event_sha256": previous["last_event_sha256"],
        "consumes_sha256": consumes,
        "evidence_scope": "github_source_only",
        "provider_origin_verified": False,
    }
    new["event_sha256"] = digest_event(new)
    appended = raw.rstrip("\n") + ("\n" if raw else "") + json.dumps(
        new, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ) + "\n"
    validate_events(appended, graph)
    return {"event": new, "proposed_ledger": appended,
            "instructions": "PROPOSAL ONLY: re-read ledger Git blob SHA, write via GitHub SHA-guard, then independently read back exact bytes and commit."}


def rehearsal(graph, root=ROOT):
    """Synthetic A/B/C exercise. Never recorded as live cross-chat verification."""
    scratch = ""
    head = "a" * 40  # synthetic, not actual main
    first = new_event(scratch, graph, kind="handoff", worker="A", topic="CF-MESH-001", read_main_commit=head, root=root)
    scratch = first["proposed_ledger"]
    second = new_event(scratch, graph, kind="readback", worker="B", topic="CF-MESH-001", consumes=first["event"]["event_sha256"], read_main_commit=head, root=root)
    scratch = second["proposed_ledger"]
    third = new_event(scratch, graph, kind="handoff", worker="B", topic="CF-MESH-001", read_main_commit=head, root=root)
    scratch = third["proposed_ledger"]
    fourth = new_event(scratch, graph, kind="readback", worker="C", topic="CF-MESH-001", consumes=third["event"]["event_sha256"], read_main_commit=head, root=root)
    audit = validate_events(fourth["proposed_ledger"], graph)
    audit.pop("events_data")
    return {"synthetic_only": True, "simulated_worker_labels": ["A", "B", "C"], **audit}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--rehearsal", action="store_true")
    mode.add_argument("--propose", choices=sorted(KINDS))
    p.add_argument("--worker", choices=sorted(WORKERS))
    p.add_argument("--topic")
    p.add_argument("--read-head")
    p.add_argument("--consumes")
    args = p.parse_args(argv)
    try:
        graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
        validate_graph(graph, root=ROOT)
        raw = LEDGER_PATH.read_text(encoding="utf-8") if LEDGER_PATH.exists() else ""
        if args.rehearsal:
            out = rehearsal(graph)
        elif args.check:
            out = validate_events(raw, graph)
            out.pop("events_data")
        else:
            if not all((args.worker, args.topic, args.read_head)):
                p.error("--propose requires --worker, --topic, --read-head")
            out = new_event(raw, graph, kind=args.propose, worker=args.worker,
                            topic=args.topic, read_main_commit=args.read_head,
                            consumes=args.consumes)
            out["proposed_ledger"] = "[omitted; use authenticated GitHub SHA-guard for append]"
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0
    except (HandoffError, GraphError, OSError, ValueError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
