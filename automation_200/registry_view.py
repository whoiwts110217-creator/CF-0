#!/usr/bin/env python3
"""CF-120: read-only, deterministic HTML view of the authoritative CF-200 registry.

Usage: python -m automation_200.registry_view --registry automation_200/registry.json --output /tmp/cf200.html
No GitHub writes, HP commands, scheduler, network access, or status mutations.
"""
from __future__ import annotations
import argparse
import hashlib
from html import escape
import json
from pathlib import Path

from .validate_registry import check_registry

def render(registry_bytes: bytes) -> str:
    data = json.loads(registry_bytes)
    counts = check_registry(data)
    digest = hashlib.sha256(registry_bytes).hexdigest()
    rows = []
    for task in data["tasks"]:
        cells = (
            task["id"], task["title"], task["stream"], task["status"],
            ", ".join(task["depends_on"]) or "—",
            task["authority"], "yes" if task["physical_hp_required"] else "no",
            task.get("evidence") or "—",
        )
        rows.append("<tr>" + "".join("<td>" + escape(str(value), quote=True) + "</td>" for value in cells) + "</tr>")
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>CF-200 authoritative registry — read-only</title>'
        '<style>body{font:16px system-ui,sans-serif;max-width:100%;margin:2rem;color:#17212b}'
        'table{border-collapse:collapse;width:100%;font-size:.85rem}td,th{padding:.55rem;border:1px solid #aaa;'
        'text-align:left;vertical-align:top}th{background:#eee}main{overflow-x:auto}code{overflow-wrap:anywhere}</style>'
        '<h1>CF-200 registry — read-only source snapshot</h1>'
        '<p>This view is generated from one validated registry file; it does not approve tasks, '
        'prove HP operation, or provide live status.</p>'
        f'<p><strong>{counts["verified"]} verified / {counts["target"]} total; '
        f'{counts["planned"]} planned</strong></p>'
        f'<p>Exact input SHA-256: <code>{digest}</code></p>'
        '<main><table><thead><tr>'
        + "".join("<th scope=\"col\">" + x + "</th>" for x in
                  ("ID", "Title", "Stream", "Status", "Dependencies", "Authority", "Physical HP", "Evidence"))
        + '</tr></thead><tbody>' + "".join(rows) + '</tbody></table></main></html>'
    )

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path(__file__).with_name("registry.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.registry.read_bytes()
    html = render(source)  # validate before writing anything
    args.output.write_text(html, encoding="utf-8")
    print(json.dumps({"output": str(args.output), "source_sha256": hashlib.sha256(source).hexdigest(),
                      "counts": check_registry(json.loads(source))}, sort_keys=True))

if __name__ == "__main__":
    main()
