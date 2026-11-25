"""Read-only public GitHub issue monitor; stdlib only. Does not contact agents."""
import datetime as dt
import json
import os
import re
import urllib.request
from pathlib import Path

OWNER = "whoiwts110217-creator"
REPO = "CF-0"
ISSUE = 16
REPOSITORY = f"{OWNER}/{REPO}"
GITHUB = f"https://github.com/{REPOSITORY}"
ISSUE_URL = f"{GITHUB}/issues/{ISSUE}"
API = f"https://api.github.com/repos/{OWNER}/{REPO}/issues/{ISSUE}/comments?per_page=100"
MAX_PAGES = 5
REPORT_BASIS = (
    "Public Issue #16 comment observations. external_responses_verified is a compatibility alias "
    "for non_owner_comments_observed. An incomplete scan does not replace the last "
    "complete observation totals."
)


def fetch_comments():
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "CF0-AI-Tracker/1.0"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    comments = []
    for page in range(1, MAX_PAGES + 1):
        request = urllib.request.Request(f"{API}&page={page}", headers=headers)
        with urllib.request.urlopen(request, timeout=20) as response:
            batch = json.load(response)
            if not isinstance(batch, list) or len(batch) > 100:
                raise ValueError("Invalid GitHub issue comment page")
            comments.extend(batch)
            if 'rel="next"' not in response.headers.get("Link", ""):
                return comments, True
    return comments, False


def summarize(comments):
    if not isinstance(comments, list):
        raise ValueError("Expected GitHub comments list")
    by_id = {}
    for comment in comments:
        identifier = comment.get("id") if isinstance(comment, dict) else None
        if type(identifier) is not int or identifier <= 0:
            raise ValueError("Invalid GitHub issue comment ID")
        by_id[identifier] = comment
    non_owner_urls = []
    for identifier, comment in by_id.items():
        user = comment.get("user")
        login = user.get("login") if isinstance(user, dict) else None
        if isinstance(login, str) and login and login.casefold() != OWNER.casefold():
            non_owner_urls.append(f"{ISSUE_URL}#issuecomment-{identifier}")
    return {
        "public_comments_observed": len(by_id),
        "non_owner_comments_observed": len(non_owner_urls),
        "external_responses_verified": len(non_owner_urls),  # Compatibility for existing v1 readers.
        "external_response_urls": non_owner_urls,
    }


def main():
    output = Path(os.environ.get("AI_TRACKER_OUTPUT", "docs/AI_TRACKER_STATUS.json"))
    previous = json.loads(output.read_text(encoding="utf-8"))
    if previous.get("schema") != "cf0.ai_tracker.status.v1" or previous.get("issue_url") != ISSUE_URL:
        raise ValueError("Unexpected AI Tracker status source")
    comments, complete = fetch_comments()
    result = summarize(comments)
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    if complete:
        # Only an exhaustive scan may replace the published observation totals.
        previous.update(result)
        previous["last_complete_scan_utc"] = now
        previous.pop("partial_comment_scan", None)
    else:
        # Preserve the previously published complete snapshot and its URLs.
        # A bounded scan is only a diagnostic sample, never an authoritative total.
        if (previous.get("comment_scan_complete") is True
                and not previous.get("last_complete_scan_utc")
                and previous.get("updated_utc")):
            previous["last_complete_scan_utc"] = previous["updated_utc"]
        previous["partial_comment_scan"] = {
            "observed_utc": now,
            "public_comments_observed": result["public_comments_observed"],
            "non_owner_comments_observed": result["non_owner_comments_observed"],
            "page_cap_reached": True,
        }
    previous["updated_utc"] = now
    previous["phase"] = "scheduled_public_issue_monitor"
    previous["comment_scan_complete"] = complete
    previous["report_basis"] = REPORT_BASIS
    previous["limitations"] = f"Up to {MAX_PAGES * 100} public comments. Agent identity and contributions require separate evidence."

    previous.pop("last_check_run_url", None)
    previous.pop("last_check_event", None)
    event = os.environ.get("GITHUB_EVENT_NAME")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    if (os.environ.get("GITHUB_REPOSITORY", "").casefold() == REPOSITORY.casefold()
            and event in {"push", "schedule", "workflow_dispatch"}
            and re.fullmatch(r"[1-9][0-9]{0,19}", run_id)):
        previous["last_check_run_url"] = f"{GITHUB}/actions/runs/{run_id}"
        previous["last_check_event"] = event
        if event == "schedule":
            previous["last_scheduled_run_url"] = previous["last_check_run_url"]
            previous["unattended_running_verified"] = True
            previous["monitor_scheduled_run_verified"] = True

    output.write_text(json.dumps(previous, indent=2) + "\n", encoding="utf-8")
    run_summary = {
        "public_comments_observed": previous.get("public_comments_observed"),
        "non_owner_comments_observed": previous.get("non_owner_comments_observed"),
        "scan_complete": complete,
    }
    if not complete:
        run_summary["partial_public_comments_observed"] = result["public_comments_observed"]
        run_summary["partial_non_owner_comments_observed"] = result["non_owner_comments_observed"]
    print(json.dumps(run_summary, sort_keys=True))

if __name__ == "__main__":
    main()
