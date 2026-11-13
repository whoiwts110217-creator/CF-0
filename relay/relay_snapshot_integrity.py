"""Read-only, standard-library validator for a local relay text snapshot.

This helper checks formatting and message-identity collisions in a *local*
plaintext export. It has no network access, account credentials, filesystem
writes, or background scheduling. Never commit private relay exports.

Usage:
    python relay/relay_snapshot_integrity.py local-export.txt --json
    python relay/relay_snapshot_integrity.py local-export.txt --bootstrap-uid YOUR_UID
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

BEGIN = re.compile(r"^BEGIN\s+(CF0-RELAY-[A-Za-z0-9_-]+)\s*$")
END = re.compile(r"(?:^|\s)END\s+(CF0-RELAY-[A-Za-z0-9_-]+)\s*$")
KEY = re.compile(r"^([A-Z_]+):\s*(.*?)\s*$")
METADATA = {"MESSAGE_ID", "MESSAGE_UID", "DOCK_TAG", "ACK_BOOTSTRAP", "REPLY_TO"}


def parse(text):
    """Return message metadata without retaining message-body content."""
    records = []
    current = None
    for lineno, source_line in enumerate(text.splitlines(), 1):
        line = source_line.strip()
        begin = BEGIN.fullmatch(line)
        if begin:
            current = {"begin": begin.group(1), "line": lineno,
                       "end": None, "fields": {}}
            records.append(current)
            continue
        if current is None:
            continue
        field = KEY.fullmatch(line)
        if field and field.group(1) in METADATA:
            current["fields"].setdefault(field.group(1), field.group(2))

        # Some legacy messages end with an inline END marker in BODY text.
        # A REPLY_TO or SUBJECT field ending in "END ..." is NOT a closer.
        match = END.search(line) if (not field or field.group(1) == "BODY") else None
        if match:
            current["end"] = match.group(1)
            current = None
    return records


def audit(text, bootstrap_uid=None):
    """Produce a snapshot-only report. Numbers are not proof of live activity."""
    records = parse(text)
    by_uid = Counter(row["fields"].get("MESSAGE_UID") for row in records
                     if row["fields"].get("MESSAGE_UID"))
    by_id = Counter(row["fields"].get("MESSAGE_ID") for row in records
                    if row["fields"].get("MESSAGE_ID"))
    by_begin = Counter(row["begin"] for row in records)
    index = next((i for i, row in enumerate(records)
                  if row["fields"].get("MESSAGE_UID") == bootstrap_uid),
                 None) if bootstrap_uid else None
    recent = records[index + 1:] if index is not None else []
    tags = {row["fields"].get("DOCK_TAG") for row in recent
            if row["fields"].get("DOCK_TAG")}
    ack_tags = {row["fields"].get("DOCK_TAG") for row in recent
                if row["fields"].get("DOCK_TAG") and row["fields"].get("ACK_BOOTSTRAP")}
    return {
        "schema": "cf0.public.relay_snapshot_integrity.v1",
        "entries": len(records),
        "duplicate_uid": sorted(x for x, n in by_uid.items() if n > 1),
        "duplicate_message_id": sorted(x for x, n in by_id.items() if n > 1),
        "duplicate_begin": sorted(x for x, n in by_begin.items() if n > 1),
        "missing_uid": [row["begin"] for row in records
                        if not row["fields"].get("MESSAGE_UID")],
        "unclosed": [row["begin"] for row in records if not row["end"]],
        "wrong_end": [row["begin"] for row in records
                      if row["end"] and row["end"] != row["begin"]],
        "bootstrap_seen": index is not None,
        "post_rollout_tags": len(tags),
        "post_rollout_ack_tags": len(ack_tags),
        "post_rollout_missing_ack_tags": sorted(tags - ack_tags),
        "limitations": (
            "Read-only local snapshot; historic collisions are not proof of "
            "message loss; a document append does not awaken other sessions."
        ),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="local text snapshot, or '-' for stdin")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--bootstrap-uid", default=None,
                        help="message UID whose later worker acknowledgements to assess")
    args = parser.parse_args(argv)
    try:
        content = (sys.stdin.read() if args.path == "-" else
                   Path(args.path).read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError) as exc:
        parser.error(str(exc))
    report = audit(content, args.bootstrap_uid)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("entries={entries} duplicate_uid={duplicate_uid} "
              "unclosed={unclosed} post_rollout_ack_tags={post_rollout_ack_tags}"
              .format(**report))
    return 2 if report["duplicate_uid"] or report["wrong_end"] or report["unclosed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
