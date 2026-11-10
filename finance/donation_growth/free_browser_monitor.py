#!/usr/bin/env python3
"""CF-DONOR-001: free, read-only real-browser evidence for public campaign pages.

Runs in GitHub Actions using open-source Playwright + Chromium on a standard
public-repository runner. GET/navigation only. No clicks, forms, logins, payments,
account connections, scraping of people, or third-party publication. Absence of
a listing is not proof of rejection; HTTP blocks and network failures are unknown.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path

CLARITY_URL = "https://whoiwts110217-creator.github.io/CF-0/clarity-card/"
FIRST_DROP_URL = "https://whoiwts110217-creator.github.io/CF-0/first-drop/"
SUPPORT_URL = "https://caveman-focus-support.whoiwts110217.chatgpt.site/"
HYPE_STAR_URL = "https://hypestar.org/project/caveman-focus"
PROMOTE_INDEX_TICKET = "097"  # queue ticket, NOT a published project identifier

# Only allowlisted, already-public HTTPS URLs are visited. No submission URLs.
TARGETS = (
    ("clarity_card", CLARITY_URL),
    ("first_drop", FIRST_DROP_URL),
    ("support_campaign", SUPPORT_URL),
    ("hype_star_listing", HYPE_STAR_URL),
)


def classify_owned_site(http_status: int | None, title: str, body: str, name: str) -> str:
    """Page-level availability, not evidence of conversions or payments."""
    if http_status is None or http_status in (401, 403, 429) or http_status >= 500:
        return "unverified"
    if http_status != 200:
        return "unavailable"
    lower = (title + " " + body).lower()
    if name == "clarity_card":
        expected = "one hard question. one clear next step."
    elif name == "first_drop":
        expected = "get in before the world knows what it is."
    elif name == "support_campaign":
        expected = "caveman focus"
    else:
        return "unverified"
    return "reachable" if expected in lower else "unverified"


def classify_listing(http_status: int | None, title: str, body: str, links: list[str]) -> str:
    """Require a live listing with the canonical tool link, not just a search hit."""
    if http_status == 404:
        return "not_public_as_checked"
    if http_status is None or http_status in (401, 403, 429) or http_status >= 500:
        return "unverified"
    if http_status != 200:
        return "unverified"
    text = (title + " " + body).lower()
    if any(marker in text for marker in ("page not found", "404 not found", "not yet published")):
        return "not_public_as_checked"
    if "caveman focus" not in title.lower() or "caveman focus" not in text:
        return "unverified"
    if not any(link.rstrip("/") == CLARITY_URL.rstrip("/") for link in links):
        return "unverified"
    return "public_listing_observed"


def summarize(report: dict) -> str:
    """Fixed, untrusted-text-free summary for GitHub job output."""
    checks = report["checks"]
    rows = [
        "### CF-DONOR-001 · No-cost read-only browser evidence",
        "",
        "Only public page visibility is checked. No accounts, posts, submissions, "
        "traffic, supporters or payments are inferred.",
        "",
        "| Target | Evidence |",
        "|---|---|",
    ]
    for name in ("clarity_card", "first_drop", "support_campaign", "hype_star_listing"):
        rows.append(f"| {name.replace('_', ' ')} | {checks[name]['status']} |")
    rows += [
        "",
        f"PromoteIndex ticket #{PROMOTE_INDEX_TICKET}: **queued in earlier run; "
        "publication remains unverified (not automatically queried or resubmitted).**",
        "",
        "Public Hype Star listing is only claimed if the page itself is reachable "
        "and visibly links to the canonical free Clarity Card.",
        "",
        "GitHub Actions job success = browser check ran, not fundraising success.",
    ]
    return "\n".join(rows)


def collect() -> dict:
    from playwright.sync_api import sync_playwright

    report = {
        "schema": "cf0.promo_browser_check.v1",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "headless_chromium_public_read_only",
        "financial_transactions_checked": False,
        "posts_created": 0,
        "submissions_created": 0,
        "promoteindex_ticket": PROMOTE_INDEX_TICKET,
        "promoteindex_publication": "unverified",
        "checks": {},
    }
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            context = browser.new_context(accept_downloads=False)
            page = context.new_page()
            page.set_default_timeout(7000)
            for name, url in TARGETS:
                status = None
                title = ""
                body = ""
                links = []
                error_kind = None
                try:
                    # Navigations only; no form filling, click, POST or state writes.
                    response = page.goto(url, wait_until="domcontentloaded", timeout=20000)
                    status = response.status if response is not None else None
                    title = page.title()[:240]
                    body = page.locator("body").inner_text(timeout=7000)[:16000]
                    if name == "hype_star_listing" and status == 200:
                        links = page.locator("a[href]").evaluate_all(
                            "(a) => a.slice(0, 200).map(e => e.href)"
                        )
                except Exception as exc:
                    error_kind = type(exc).__name__
                if name == "hype_star_listing":
                    evidence = classify_listing(status, title, body, links)
                else:
                    evidence = classify_owned_site(status, title, body, name)
                entry = {"status": evidence}
                if status is not None:
                    entry["http_status"] = status
                if error_kind:
                    entry["error_kind"] = error_kind
                report["checks"][name] = entry
            context.close()
        finally:
            browser.close()
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="explicitly enable browser navigation")
    parser.add_argument("--output", type=Path, help="optional local public-safe JSON output")
    args = parser.parse_args()
    if not args.live:
        parser.error("--live is required; offline unit tests need no browser or network")
    report = collect()
    text = summarize(report)
    print(text)
    print("CF0_PROMO_BROWSER_JSON=" + json.dumps(report, sort_keys=True))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(text + "\n")
    # A 404 review-pending directory entry is not a CI failure. A broken owned
    # page is visible in the summary; do not conflate it with donation failure.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
