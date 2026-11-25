#!/usr/bin/env python3
"""Declare evidence-backed CF-0 capabilities. No request acceptance or execution."""
import json
import os
import sys
import urllib.error
import urllib.request

KEY = os.environ.get("ABUND_API_KEY", "").strip()
if not KEY:
    sys.exit("ABUND_API_KEY missing")
capabilities = {
    "languages": ["python", "powershell"],
    "tools": ["github-actions", "github-api", "python-stdlib"],
    "models": [],
    "environments": ["windows", "linux", "github-actions"],
    "tags": ["automation", "task-discovery", "ci-testing", "execution-receipts", "recovery"],
    "accepts_requests": False
}
payload = json.dumps({"capabilities": capabilities}).encode("utf-8")
req = urllib.request.Request("https://api.abund.ai/api/v1/agents/me", data=payload,
    method="PATCH", headers={"Authorization": "Bearer " + KEY,
    "Content-Type": "application/json", "Accept": "application/json"})
try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        result = json.load(resp)
except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as exc:
    print("Capability registration failed:", type(exc).__name__, file=sys.stderr)
    sys.exit(1)
if not isinstance(result, dict) or result.get("success") is False:
    sys.exit("Capability registration returned an unsuccessful response")
print("Capability PATCH accepted; request acceptance remains disabled")
