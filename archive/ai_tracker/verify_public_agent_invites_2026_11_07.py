"""Read back public CF-0 invitations without posting anything."""
from __future__ import annotations
import datetime as dt
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

MARKERS = ("CF0-OPEN-AGENT-REVIEW-001", "Idle agents: test a five-minute", "Can a public AI tracker distinguish", "Open public micro-missions")
ENDPOINTS = {
    "taskbounty": "https://www.task-bounty.com/api/v1/board/threads?q=CF-0",
    "campfire": "https://agentsboard.org/api/v1/feed",
    "dooza": "https://commons.dooza.ai/api/entries",
    "messages_directory": "https://messages.directory/api/threads?limit=20",
}
OUT = Path("docs/AGENT_PUBLIC_LISTING_CHECK_2026_11_07.json")

def safe_url(value: object, host: str) -> str | None:
    if not isinstance(value, str) or not value.startswith("https://"):
        return None
    p = urllib.parse.urlsplit(value)
    if p.hostname != host or p.username or p.password or p.query or p.fragment:
        return None
    return p.scheme + "://" + p.netloc + p.path

def matches(node: object, out: list, host: str, depth: int = 0):
    if depth > 8 or len(out) > 15:
        return
    if isinstance(node, dict):
        direct_text = " ".join(str(node.get(k, "")) for k in ("title", "body", "content", "text", "message", "description"))
        if any(marker in direct_text for marker in MARKERS):
            result = {"title": str(node.get("title", ""))[:160]}
            for key in ("id", "thread_id", "slug", "entry_id"):
                val = node.get(key)
                if type(val) in (str, int) and len(str(val)) <= 150:
                    result[key] = val
            for key in ("url", "html_url", "permalink", "thread_url", "entry_url"):
                url = safe_url(node.get(key), host)
                if url:
                    result["url"] = url
                    break
            if result not in out:
                out.append(result)
        for value in node.values():
            if isinstance(value, (dict, list)):
                matches(value, out, host, depth + 1)
    elif isinstance(node, list):
        for item in node[:100]:
            matches(item, out, host, depth + 1)

def main():
    results = []
    for name, url in ENDPOINTS.items():
        host = urllib.parse.urlsplit(url).hostname
        request = urllib.request.Request(url, headers={"User-Agent": "CF0-Public-Readback/1.0", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                raw = response.read(750000)
                body = json.loads(raw)
                found = []
                matches(body, found, host)
                result = {"site": name, "http_status": response.status, "matching_public_records": found}
        except urllib.error.HTTPError as e:
            result = {"site": name, "http_status": e.code, "matching_public_records": [], "note": "Readback endpoint rejected request"}
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
            result = {"site": name, "matching_public_records": [], "error_type": type(e).__name__}
        results.append(result)
        print(json.dumps(result, ensure_ascii=False))
    payload = {"schema": "cf0.agent_invite_readback.v1", "checked_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "note": "Absence in a limited feed is not proof a 201 response was not published. Only returned public URLs count as verified links.", "results": results}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
