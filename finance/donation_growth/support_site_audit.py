#!/usr/bin/env python3
"""Read-only HTML-level support-site check. No requests to payment links.

Opt-in --live required. This cannot establish JS-rendered site functionality,
accessibility, actual payment-link behavior, traffic, or donations.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

TARGET = "https://caveman-focus-support.whoiwts110217.chatgpt.site/"
MAX_BYTES = 256 * 1024

class SiteHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.html_lang = None
        self.title_parts = []
        self.in_title = False
        self.viewport = False
        self.links = []
        self.text_parts = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.html_lang = a.get("lang")
        if tag == "title":
            self.in_title = True
        if tag == "meta" and (a.get("name") or "").lower() == "viewport":
            self.viewport = bool(a.get("content"))
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)
        self.text_parts.append(data)

def inspect_html(content: str) -> dict:
    """Presence signals in static markup, not proof of browser display."""
    parser = SiteHTML()
    parser.feed(content)
    text = " ".join(parser.text_parts).lower()
    return {
        "title_present": bool(" ".join(parser.title_parts).strip()),
        "html_lang": parser.html_lang,
        "viewport_meta_present": parser.viewport,
        "static_cash_app_anchor_present": any(
            urlsplit(unquote(h)).hostname == "cash.app" for h in parser.links
        ),
        "static_caveman_focus_text_present": "caveman focus" in text,
        "static_voluntary_support_text_present": "if you don't want to give" in text,
        "static_html_only": True,
    }

class SameHostHTTPSRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        original = urlsplit(TARGET)
        destination = urlsplit(newurl)
        if destination.scheme != "https" or destination.hostname != original.hostname:
            raise URLError("redirect_outside_support_site")
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def audit_live(timeout: float = 12.0) -> dict:
    result = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "target": TARGET,
        "site_access": "unverified",
        "live_browser_verification": False,
        "payments_checked": False,
        "note": "Read-only HTML probe; no payment requests or browser simulation.",
    }
    opener = build_opener(SameHostHTTPSRedirect())
    req = Request(TARGET, headers={"User-Agent": "CavemanFocusSiteAudit/1.0", "Accept": "text/html"})
    try:
        with opener.open(req, timeout=timeout) as response:
            raw = response.read(MAX_BYTES + 1)
            result["http_status"] = response.status
            result["site_access"] = "http_response_received"
            result["html_truncated"] = len(raw) > MAX_BYTES
            result["html_bytes_read"] = min(len(raw), MAX_BYTES)
            kind = response.headers.get_content_type()
            result["content_type"] = kind
            if kind == "text/html":
                charset = response.headers.get_content_charset() or "utf-8"
                result.update(inspect_html(raw[:MAX_BYTES].decode(charset, errors="replace")))
            else:
                result["note"] = "HTTP response received but content type was not HTML."
    except HTTPError as error:
        result.update({"site_access": "http_error", "http_status": error.code, "error_kind": "HTTPError"})
    except (URLError, TimeoutError, OSError, LookupError) as error:
        result.update({"site_access": "network_error", "error_kind": type(error).__name__})
    return result

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="one read-only HTTPS request")
    parser.add_argument("--timeout", type=float, default=12.0)
    args = parser.parse_args()
    if not args.live:
        parser.error("Explicit --live required; use unittest for offline tests")
    result = audit_live(timeout=max(1, min(args.timeout, 30)))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["site_access"] == "http_response_received" else 2

if __name__ == "__main__":
    raise SystemExit(main())
