"""Read-only public GitHub issue monitor; stdlib only. Does not contact agents."""
import datetime as dt
import json
import os
import urllib.request
from pathlib import Path

OWNER = "whoiwts110217-creator"
REPO = "CF-0"
ISSUE = 16
API = f"https://api.github.com/repos/{OWNER}/{REPO}/issues/{ISSUE}/comments?per_page=100"

def fetch_comments():
    request = urllib.request.Request(API, headers={"Accept": "application/vnd.github+json", "User-Agent": "CF0-AI-Tracker/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)

def summarize(comments):
    if not isinstance(comments, list):
        raise ValueError("Expected GitHub comments list")
    external = [c for c in comments if c.get("user", {}).get("login", "").lower() != OWNER.lower()]
    return {
        "public_comments_observed": len(comments),
        "external_responses_verified": len(external),
        "external_response_urls": [c["html_url"] for c in external if c.get("html_url", "").startswith("https://github.com/")],
    }

def main():
    output = Path(os.environ.get("AI_TRACKER_OUTPUT", "docs/AI_TRACKER_STATUS.json"))
    previous = json.loads(output.read_text(encoding="utf-8"))
    result = summarize(fetch_comments())
    previous.update(result)
    previous["updated_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    previous["phase"] = "scheduled_public_issue_monitor"
    previous["unattended_running_verified"] = False
    previous["report_basis"] = "GitHub public Issue #16 comment API; external means non-owner account, not verified independent AI."
    previous["limitations"] = "Counts cover only the first 100 public comments on Issue #16; no other platforms, private messages, proof of AI identity, or verified contributions."
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(previous, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
