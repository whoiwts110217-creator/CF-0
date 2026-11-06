#!/usr/bin/env python3
"""Read-only Abund.ai task discovery. Never accepts, replies, votes or spends."""
import datetime as dt
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

BASE = "https://api.abund.ai/api/v1"
OUTPUT = pathlib.Path(os.environ.get("CF0_ABUND_OUTPUT", "abund_task_report.json"))
ALLOWED = {"answer_question", "confirm_finding", "answer_reply", "set_capabilities"}
KEYWORDS = ("python", "windows", "powershell", "github", "automation", "timeout",
            "network", "retry", "receipt", "idempot", "testing", "recovery")
EXCLUDED = ("crypto", "trading", "investment", "wallet", "payment", "usdc", "x402")

def score(item):
    action = str(item.get("action", ""))
    why = str(item.get("why", ""))
    lower = why.lower()
    if action not in ALLOWED:
        return -1
    if any(term in lower for term in EXCLUDED):
        return -1
    return sum(2 for word in KEYWORDS if word in lower) + (2 if action == "set_capabilities" else 0)

def main():
    key = os.environ.get("ABUND_API_KEY", "").strip()
    if not key:
        print("ABUND_API_KEY missing", file=sys.stderr)
        return 2
    req = urllib.request.Request(BASE + "/agents/status",
        headers={"Authorization": "Bearer " + key, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.load(resp)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as exc:
        print("Status request failed: " + type(exc).__name__, file=sys.stderr)
        return 1
    if not isinstance(data, dict) or data.get("success") is not True:
        print("Unexpected status response", file=sys.stderr)
        return 1
    todos = data.get("todo", [])
    if not isinstance(todos, list):
        print("Unexpected todo response", file=sys.stderr)
        return 1
    candidates = []
    for item in todos:
        if not isinstance(item, dict):
            continue
        points = score(item)
        if points < 0:
            continue
        candidates.append({"action": item.get("action"), "why": str(item.get("why", ""))[:500],
                           "read_first": item.get("read_first"), "score": points,
                           "requires_review": True})
    candidates.sort(key=lambda x: (-x["score"], x["action"] or ""))
    report = {
        "checked_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "agent": data.get("agent", {}).get("handle"),
        "account_status": data.get("status"),
        "unread_notifications": data.get("unread_notifications"),
        "todo_count": len(todos),
        "candidates": candidates,
        "policy": "READ_ONLY: no automatic acceptance, replies, confirmations, votes, payments or capability claims"
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Discovery complete: {len(todos)} todo items, {len(candidates)} review candidates")
    return 0

if __name__ == "__main__":
    sys.exit(main())
