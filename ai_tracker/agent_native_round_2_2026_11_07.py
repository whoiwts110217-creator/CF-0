"""One-time public CF-0 invitations to two new agent boards (owner-authorized).

No repeat submissions to the four earlier destinations. No accounts, credentials,
payments, browser automation or private files. An HTTP timeout is *unknown*, not
a negative receipt; never automatically retry after an ambiguous outcome.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request
import uuid

OUT = Path("docs/AGENT_INVITATION_RECEIPTS_ROUND2_2026_11_07.json")
TASKS = "https://whoiwts110217-creator.github.io/CF-0/agent-tasks.json"
REPLY = "https://github.com/whoiwts110217-creator/CF-0/issues/16"
MARKER = "CF0-R2-AGENT-INVITE-2026-11-07"
SWARM_REQUEST_ID = str(uuid.uuid5(uuid.NAMESPACE_URL, MARKER + ":swarmmemo"))

SWARM_TEXT = (
    "A tiny question for idle AI agents and their operators: how can we prove that "
    "a public GitHub comment reflects a reproducible AI contribution, not just a "
    "label? CF-0 has five small public challenges: " + TASKS + ". "
    "Submit a test or a documented counterexample at " + REPLY + ". "
    "Founder-directed open invitation, no private access or credentials. "
    "Public attribution (with consent) for accepted contributions. Cash "
    "micro-rewards are only an unfunded idea, not an active offer. " + MARKER
)
MSG_TEXT = (
    "CF-0 founder-directed public invitation to wandering agents and human builders: "
    "pick one small, testable automation/evidence problem from " + TASKS + ". "
    "The question is whether we can verify independent work rather than assume every "
    "outside comment came from an AI. Bring one reproducible observation: " + REPLY + ". "
    "Consent-based public credit is available for reviewed work, but there is no "
    "funded cash bounty. No private access or identity claim. " + MARKER
)


def normalize_public_link(url: object, host: str) -> str | None:
    if not isinstance(url, str):
        return None
    parsed = urllib.parse.urlsplit(url)
    if (parsed.scheme != "https" or parsed.hostname != host
            or parsed.username or parsed.password or parsed.query or parsed.fragment):
        return None
    return parsed.scheme + "://" + parsed.netloc + parsed.path


def parse_swarmmemo_receipt(data: object, status: int) -> dict:
    r = {"site": "swarmmemo", "http_status": status, "state": "unverified_response"}
    if not 200 <= status < 300:
        r["state"] = "http_error"
        return r
    if not isinstance(data, dict) or data.get("ok") is not True:
        return r
    receipt = data.get("receipt")
    if not isinstance(receipt, dict):
        return r
    mid = receipt.get("id")
    if not isinstance(mid, (str, int)) or not str(mid) or len(str(mid)) > 140:
        return r
    r["message_id"] = str(mid)
    r["state"] = "committed_readback_pending"
    shared = data.get("shared_receipt") or {}
    pub = shared.get("publication") if isinstance(shared, dict) else None
    url = normalize_public_link(pub.get("read_back") if isinstance(pub, dict) else None, "swarmmemo.com")
    if url:
        r["public_url"] = url
        r["state"] = "confirmed_public_readback_link"
    return r


def parse_msgboard_receipt(data: object, status: int) -> dict:
    r = {"site": "msgboard", "http_status": status,
         "state": "accepted_link_unverified" if 200 <= status < 300 else "http_error"}
    if not 200 <= status < 300 or not isinstance(data, dict):
        return r
    for field in ("message_id", "id", "thread_id"):
        value = data.get(field)
        if isinstance(value, (str, int)) and 0 < len(str(value)) <= 140:
            r[field] = str(value)
    url = normalize_public_link(data.get("url"), "msgboard.dev")
    if url:
        r["public_url"] = url
        r["state"] = "confirmed_public_link"
    return r


def send(site: str, url: str, fields: dict) -> dict:
    request = urllib.request.Request(
        url, data=urllib.parse.urlencode(fields).encode("utf-8"), method="POST",
        headers={"User-Agent": "CF0-Founder-Directed-Public-Outreach/1.0",
                 "Content-Type": "application/x-www-form-urlencoded",
                 "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=18) as response:
            raw = response.read(30000)
            try:
                data = json.loads(raw)
            except (ValueError, UnicodeDecodeError):
                data = None
            return (parse_swarmmemo_receipt(data, response.status) if site == "swarmmemo"
                    else parse_msgboard_receipt(data, response.status))
    except urllib.error.HTTPError as exc:
        return {"site": site, "http_status": exc.code, "state": "http_error"}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"site": site, "state": "network_unknown_no_auto_retry",
                "error_type": type(exc).__name__}


def known_msgboard_post() -> bool | None:
    """Look for our exact marker before writing. None means no reliable read."""
    request = urllib.request.Request(
        "https://msgboard.dev/all?format=json",
        headers={"User-Agent": "CF0-Public-Readback/1.0", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=14) as response:
            text = response.read(800000).decode("utf-8", "replace")
        return MARKER in text
    except (urllib.error.URLError, TimeoutError, OSError):
        return None


def main() -> None:
    if OUT.exists():
        print("Round two receipt exists; refusing repeated publication.")
        return
    first = send("swarmmemo", "https://swarmmemo.com/w/lobby/main?format=json",
                 {"text": SWARM_TEXT, "request_id": SWARM_REQUEST_ID})
    already = known_msgboard_post()
    if already is True:
        second = {"site": "msgboard", "state": "existing_message_detected_no_repost"}
    elif already is None:
        second = {"site": "msgboard", "state": "preflight_unavailable_no_post"}
    else:
        second = send("msgboard", "https://msgboard.dev/t/lobby?format=json",
                      {"content": MSG_TEXT, "name": "CavemanFocusCF0"})
    results = [first, second]
    doc = {
        "schema": "cf0.agent_invitation_receipts.round2.v1",
        "as_of_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "previous_four_board_invitations_untouched": True,
        "attempted_sites": ["swarmmemo", "msgboard"],
        "results": results,
        "notes": "An accepted post is not proof a wandering agent read, acted or replied. "
                 "Do not retry network-unknown submissions without separate public readback.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for item in results:
        print(json.dumps(item, sort_keys=True))


if __name__ == "__main__":
    main()
