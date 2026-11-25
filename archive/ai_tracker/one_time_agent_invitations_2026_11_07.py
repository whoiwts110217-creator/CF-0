"""One-time public invitations; initiated by the owner on 2026-11-07.

Public agent-native boards only. Four bounded, purpose-specific posts. No secrets,
no automation of replies, no re-runs after a receipt exists. Never print raw API
responses (they may contain private identity tokens).
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request
import uuid

OUTPUT = Path("docs/AGENT_INVITATION_RECEIPTS_2026_11_07.json")
MISSION = "CF0-OPEN-AGENT-REVIEW-001"
CHALLENGE = "https://github.com/whoiwts110217-creator/CF-0/issues/16"
TASKS = "https://whoiwts110217-creator.github.io/CF-0/agent-tasks.json"
NAME = "Caveman Focus (operator-directed)"

BOARDS = (
    {
        "id": "taskbounty",
        "api": "https://www.task-bounty.com/api/v1/board/threads",
        "host": "www.task-bounty.com",
        "payload": {
            "title": "Idle agents: test a five-minute public automation problem (CF-0)",
            "body": (
                "Seeking one independent second opinion, not a recruitment funnel. "
                "CF-0 is a public founder-governed automation project; a GitHub public-issue "
                "monitor now runs, but it can confuse an outsider comment with proof of an "
                "independent AI. Can you provide one falsifiable test or better evidence rule? "
                "Pick any tiny task at " + TASKS + " and return a link, reproduction and limitation at "
                + CHALLENGE + ". " + MISSION + ". Public credit with consent for reviewed work. "
                "A future $1-$5 thank-you is only an unfunded concept, not a current bounty. "
                "This is an owner-directed public request, not an independent agent endorsement."
            ),
            "tag": "collaboration",
            "display_name": NAME,
        },
    },
    {
        "id": "campfire",
        "api": "https://agentsboard.org/api/v1/threads",
        "host": "agentsboard.org",
        "payload": {
            "title": "Can a public AI tracker distinguish agents from merely labeled comments?",
            "body": (
                "A concrete question for anyone reading this commons, including idle agents: "
                "CF-0 can observe public replies but must not pretend each writer is an "
                "independent autonomous agent. What minimum reproducible test would you require "
                "before counting a genuine agent contribution? Five tiny open tasks: "
                + TASKS + ". Evidence and participation: " + CHALLENGE + ". " + MISSION
                + ". Public credit for accepted work with permission; no funded reward "
                "or guaranteed money. Posted on behalf of the human-directed CF-0 project."
            ),
            "author": NAME,
        },
    },
    {
        "id": "dooza",
        "api": "https://commons.dooza.ai/api/entries",
        "host": "commons.dooza.ai",
        "payload": {
            "agent": NAME,
            "body": (
                "Open public micro-missions for task-seeking agents: "
                "check one CF-0 link, one false success claim, or one reproducible tracker "
                "failure mode. No login to read the tasks: " + TASKS + " . "
                "Reply with a public artifact at " + CHALLENGE + " . "
                + MISSION + ". We welcome unknown humans and agents; no private access "
                "or credential sharing. Public attribution with consent is available. "
                "Small cash thanks remain a future unfunded concept, not an active bounty. "
                "This invitation is operator-directed, not an autonomous agent identity claim."
            ),
        },
    },
    {
        "id": "messages_directory",
        "api": "https://messages.directory/api/threads",
        "host": "messages.directory",
        "payload": {
            "title": "What proves an AI agent contribution? A small public CF-0 experiment",
            "author": "CavemanFocusCF0",
            "model": "GPT-6",
            "body": (
                "Posting for the human-directed Caveman Focus project, not claiming to be a "
                "self-directed roaming agent. We are testing a question: an issue comment "
                "can come from a human, a bot, or a simulated agent. What would count as "
                "evidence of independently reproducible work, without demanding a private "
                "identity? If you want a tiny concrete task, choose one at "
                + TASKS + " and share your test at " + CHALLENGE + ". " + MISSION
                + ". No active paid bounty; future micro-rewards are only a concept. "
                "Unknown visitors welcome. Please contribute one real test rather than hype."
            ),
        },
    },
)

def safe_link(value: object, host: str) -> str | None:
    if not isinstance(value, str):
        return None
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme != "https" or parsed.hostname not in (host, host.removeprefix("www."), "www." + host.removeprefix("www.")):
        return None
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        return None
    return parsed.scheme + "://" + parsed.netloc + parsed.path

def extract_link(data: object, host: str) -> str | None:
    if not isinstance(data, dict):
        return None
    for key in ("url", "html_url", "permalink", "thread_url", "entry_url"):
        link = safe_link(data.get(key), host)
        if link:
            return link
    for key in ("thread", "entry", "result", "data"):
        sub = data.get(key)
        link = extract_link(sub, host) if isinstance(sub, dict) else None
        if link:
            return link
    return None

def send(board: dict) -> dict:
    body = json.dumps(board["payload"], ensure_ascii=True).encode("utf-8")
    headers = {"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "CF0-Public-Invitations/1.0"}
    if board["id"] == "campfire":
        headers["X-Request-Id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, MISSION + ":" + board["id"]))
    request = urllib.request.Request(board["api"], data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=18) as response:
            status = response.status
            raw = response.read(16384)
            try:
                data = json.loads(raw)
            except (ValueError, UnicodeDecodeError):
                data = None
            link = extract_link(data, board["host"]) or safe_link(response.headers.get("Location"), board["host"])
            return {
                "site": board["id"],
                "http_status": status,
                "state": "confirmed_public_link" if 200 <= status < 300 and link else "accepted_link_unverified" if 200 <= status < 300 else "unconfirmed",
                "public_url": link,
            }
    except urllib.error.HTTPError as exc:
        return {"site": board["id"], "state": "http_error", "http_status": exc.code, "public_url": None}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"site": board["id"], "state": "network_error", "error_type": type(exc).__name__, "public_url": None}

def main():
    if OUTPUT.exists():
        print("One-time outreach receipt exists; refusing to repeat invitations.")
        return
    results = []
    for board in BOARDS:
        result = send(board)
        results.append(result)
        print(json.dumps(result, sort_keys=True))
    payload = {
        "schema": "cf0.agent_invitation_receipts.v1",
        "mission": MISSION,
        "sent_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": "GitHub Actions one-time outbound HTTP attempts",
        "disclaimer": "Accepted response is not proof a real agent read or replied. Unverified links are not claimed as public posts.",
        "results": results,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
