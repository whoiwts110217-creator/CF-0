"""Read-only prompt change guard for CF-0's public operating instructions.

Checks structural invariants and commit-linked change records; it does not grant
approval or prove the owner accepted a proposal.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = (
    "automation_200/MASTER_OPERATOR_PROMPT.md",
    "automation_200/MASTER_CONTINUITY_PROMPT.md",
    "automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md",
)
LOG = "automation_200/PROMPT_CHANGE_LOG.jsonl"
BIN = "automation_200/PROMPT_CHANGE_BIN.md"
SHA = re.compile(r"[a-f0-9]{40}\Z")

REQUIRED = {
    PROMPTS[0]: (
        "P0 — Automation", "P1 — Priority intelligence",
        "P2 — Financial operations", "P3 — Concurrent branches",
        "OWNER_CAPABILITY_CONTRACT.json", "PROMPT_CHANGE_BIN.md",
        "MASTER_CONTINUITY_PROMPT.md", "WORK_COPY_PASTE_AUTOMATION_PROMPT.md",
        "ping", "hp_status", "sidecar_verify",
    ),
    PROMPTS[1]: (
        "MASTER_OPERATOR_PROMPT.md", "PROMPT_CHANGE_BIN.md",
        "provenance", "Source recovery", "Operational truth and evidence levels",
    ),
    PROMPTS[2]: (
        "MASTER_OPERATOR_PROMPT.md", "MASTER_CONTINUITY_PROMPT.md",
        "PROMPT_CHANGE_BIN.md", "PROMPT_CHANGE_LOG.jsonl",
        "CF-200", "ping", "hp_status", "sidecar_verify",
    ),
}


def git_blob_sha(raw: bytes) -> str:
    """Compare canonical prompt text despite Git checkout CRLF conversion on Windows.

    The tracked public prompts use LF in Git. Do not treat a Windows working-tree
    CRLF checkout as an unlogged modification; content edits still change the hash.
    """
    canonical = raw.replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob " + str(len(canonical)).encode() + b"\0" + canonical).hexdigest()


def audit(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for path in PROMPTS:
        file = root / path
        if not file.is_file():
            errors.append(f"Missing canonical prompt: {path}")
            continue
        body = file.read_text(encoding="utf-8")
        for term in REQUIRED[path]:
            if term not in body:
                errors.append(f"{path} missing invariant: {term}")
    bin_file = root / BIN
    if not bin_file.is_file():
        errors.append("Missing owner approval bin")
        bin_content = ""
    else:
        bin_content = bin_file.read_text(encoding="utf-8")
        for required in ("Needs owner approval", "Safe automatic changes", "Applied changes"):
            if required not in bin_content:
                errors.append(f"Approval bin missing section: {required}")

    log_file = root / LOG
    if not log_file.is_file():
        return errors + ["Missing append-only prompt change log"]
    lines = log_file.read_text(encoding="utf-8").splitlines()
    if not lines:
        errors.append("Empty prompt change log")
    seen: set[str] = set()
    latest: dict[str, str] = {}
    for n, line in enumerate(lines, 1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            errors.append(f"Invalid JSONL line {n}")
            continue
        if not isinstance(event, dict):
            errors.append(f"Non-object JSONL line {n}")
            continue
        event_id = event.get("id")
        if not isinstance(event_id, str) or not re.fullmatch(r"PCE-\d{3,}", event_id):
            errors.append(f"Invalid change ID at line {n}")
        elif event_id in seen:
            errors.append(f"Duplicate change ID {event_id}")
        else:
            seen.add(event_id)
        if not isinstance(event.get("authority"), str) or not event["authority"].strip():
            errors.append(f"Missing authority at line {n}")
        if event.get("status") != "applied":
            errors.append(f"Unexpected applied log status at line {n}")
        commit = event.get("commit")
        if not isinstance(commit, str) or not SHA.fullmatch(commit):
            errors.append(f"Invalid commit SHA at line {n}")
        prior = event.get("before_blob_sha")
        if prior is not None and (not isinstance(prior, str) or not SHA.fullmatch(prior)):
            errors.append(f"Invalid previous blob SHA at line {n}")
        changed = event.get("after_blob_sha")
        if changed is not None and (not isinstance(changed, str) or not SHA.fullmatch(changed)):
            errors.append(f"Invalid result blob SHA at line {n}")
        path = event.get("path")
        if isinstance(path, str) and path in PROMPTS and isinstance(changed, str):
            latest[path] = changed
        if isinstance(event_id, str) and event_id not in bin_content:
            errors.append(f"Change event {event_id} missing from approval bin")
    for path in PROMPTS:
        if (root / path).is_file() and path in latest:
            observed = git_blob_sha((root / path).read_bytes())
            if observed != latest[path]:
                errors.append(f"{path} no longer matches latest recorded blob; append a change event")
        elif path not in latest:
            errors.append(f"No recorded prompt change for {path}")
    return errors


if __name__ == "__main__":
    problems = audit()
    if problems:
        for problem in problems:
            print("PROMPT CHANGE GUARD:", problem)
        raise SystemExit(1)
    print("CF-0 prompt governance and change-log integrity: PASSED")
