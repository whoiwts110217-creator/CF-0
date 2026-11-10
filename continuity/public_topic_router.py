#!/usr/bin/env python3
"""Read-only public topic graph router for CF-MESH-001.

The selected topic stays the anchor. Adjacent nodes are reading suggestions,
never implicit topic switches, new memory, tool authority, or private sources.
Standard library only. No network, accounts, writes or background actions.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "docs/PUBLIC_CONTEXT_GRAPH.json"
SCHEMA = "cf0.public_topic_graph.v1"
ID = re.compile(r"^[A-Z0-9][A-Z0-9_-]{2,63}$")
BOOT = [
    "automation_200/MASTER_OPERATOR_PROMPT.md",
    "automation_200/MASTER_CONTINUITY_PROMPT.md",
    "automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md",
]


class GraphError(ValueError):
    pass


def safe_public_path(value):
    if type(value) is not str or not value or "\\" in value or "\x00" in value:
        raise GraphError("invalid_public_source_path")
    p = PurePosixPath(value)
    if p.is_absolute() or any(part in ("", ".", "..") for part in value.split("/")):
        raise GraphError("path_escapes_public_repo")
    if p.suffix not in (".md", ".json"):
        raise GraphError("non_document_source")
    return value


def validate_graph(data, root=None):
    if type(data) is not dict or data.get("schema") != SCHEMA or data.get("contract") != "CF-MESH-001":
        raise GraphError("invalid_public_topic_graph_schema")
    if data.get("boot_sources") != BOOT:
        raise GraphError("boot_sequence_changed")
    nodes = data.get("nodes")
    if type(nodes) is not list or not 1 <= len(nodes) <= 256:
        raise GraphError("invalid_node_count")
    found = {}
    seen_aliases = {}
    sources = set(BOOT)
    for node in nodes:
        if type(node) is not dict or set(node) != {"id", "title", "source", "parent", "related", "depends_on", "aliases"}:
            raise GraphError("invalid_node_shape")
        name = node["id"]
        if type(name) is not str or not ID.fullmatch(name) or name in found:
            raise GraphError("duplicate_or_invalid_node_id")
        if type(node["title"]) is not str or not node["title"].strip() or len(node["title"]) > 180:
            raise GraphError("invalid_node_title")
        sources.add(safe_public_path(node["source"]))
        if node["parent"] is not None and (type(node["parent"]) is not str or not ID.fullmatch(node["parent"])):
            raise GraphError("invalid_parent_reference")
        for field in ("related", "depends_on"):
            refs = node[field]
            if type(refs) is not list or len(refs) > 32 or len(refs) != len(set(str(x) for x in refs)):
                raise GraphError("invalid_graph_edges")
            if any(type(x) is not str or not ID.fullmatch(x) for x in refs):
                raise GraphError("invalid_graph_edges")
        aliases = node["aliases"]
        if type(aliases) is not list or len(aliases) > 20:
            raise GraphError("invalid_aliases")
        for alias in [name, *aliases]:
            if type(alias) is not str or not alias.strip() or len(alias) > 80:
                raise GraphError("invalid_alias")
            label = " ".join(alias.casefold().split())
            if label in seen_aliases and seen_aliases[label] != name:
                raise GraphError("ambiguous_topic_alias")
            seen_aliases[label] = name
        found[name] = node
    for node in nodes:
        name = node["id"]
        refs = ([node["parent"]] if node["parent"] else []) + node["related"] + node["depends_on"]
        if name in refs or any(ref not in found for ref in refs):
            raise GraphError("missing_or_self_referential_node_link")
    # Directed parent and dependency edges must not create a dependency loop.
    checked = set()
    def visit(name, visiting):
        if name in visiting:
            raise GraphError("cycle_in_parent_or_dependency_links")
        if name in checked:
            return
        for ref in ([found[name]["parent"]] if found[name]["parent"] else []) + found[name]["depends_on"]:
            visit(ref, visiting | {name})
        checked.add(name)
    for name in found:
        visit(name, set())
    if root is not None:
        root = Path(root)
        for source in sources:
            if not (root / source).is_file():
                raise GraphError("missing_public_source:" + source)
    return found


def route_topic(data, topic, *, root=None, limit=8):
    """Return a deterministic, non-executing reading route that retains focus."""
    nodes = validate_graph(data, root=root)
    if type(topic) is not str:
        raise GraphError("invalid_topic")
    if type(limit) is not int or not 0 <= limit <= 32:
        raise GraphError("invalid_neighbor_limit")
    key = " ".join(topic.casefold().split())
    matches = [
        node for node in nodes.values()
        if key in [" ".join(a.casefold().split()) for a in [node["id"], *node["aliases"]]]
    ]
    if len(matches) != 1:
        raise GraphError("unknown_or_ambiguous_topic")
    focus = matches[0]
    fid = focus["id"]
    candidates = {}
    def add(ref, rank, relation):
        if ref != fid and (ref not in candidates or rank < candidates[ref][0]):
            candidates[ref] = (rank, relation)
    if focus["parent"]:
        add(focus["parent"], 0, "parent")
    for ref in focus["depends_on"]:
        add(ref, 0, "dependency")
    for ref in focus["related"]:
        add(ref, 2, "related")
    for other in nodes.values():
        if other["id"] == fid:
            continue
        if other["parent"] == fid:
            add(other["id"], 1, "child")
        if fid in other["depends_on"]:
            add(other["id"], 1, "dependent")
        if fid in other["related"]:
            add(other["id"], 3, "incoming_related")
    chosen = sorted(candidates.items(), key=lambda item: (item[1][0], item[0]))[:limit]
    links = [
        {"id": name, "relationship": why, "title": nodes[name]["title"],
         "public_source": nodes[name]["source"]}
        for name, (_, why) in chosen
    ]
    read_sources = []
    for source in [*BOOT, focus["source"], *(item["public_source"] for item in links)]:
        if source not in read_sources:
            read_sources.append(source)
    return {
        "schema": "cf0.public_topic_route.v1",
        "contract": "CF-MESH-001",
        "selected_topic": fid,
        "focus_preserved": True,
        "source_of_focus": focus["source"],
        "related_context_only": links,
        "read_order": read_sources,
        "source_level_only": True,
        "execution_authorized": False,
        "known_nodes_in_this_public_slice": len(nodes),
        "unknown_history_not_reconstructed": True,
        "next_step": "Read current source and any new owner direction; advance the selected topic, not its neighbors.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, default=GRAPH_PATH)
    parser.add_argument("--topic", help="Existing node ID or unambiguous alias")
    parser.add_argument("--check-all", action="store_true", help="Validate known links and local public sources")
    parser.add_argument("--max-neighbors", type=int, default=8)
    args = parser.parse_args(argv)
    if not args.topic and not args.check_all:
        parser.error("select --topic or --check-all")
    try:
        data = json.loads(args.graph.read_text(encoding="utf-8"))
        root = args.graph.resolve().parents[1] if args.graph.resolve() == GRAPH_PATH.resolve() else None
        if args.check_all and not args.topic:
            nodes = validate_graph(data, root=root)
            result = {"schema": SCHEMA, "nodes_checked": len(nodes), "valid": True,
                      "live_cross_chat_test": False, "source_level_only": True}
        elif args.topic:
            result = route_topic(data, args.topic, root=root, limit=args.max_neighbors)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (GraphError, OSError, ValueError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
