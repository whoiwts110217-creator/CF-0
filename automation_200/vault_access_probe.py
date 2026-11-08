#!/usr/bin/env python3
"""Read-only probe of the CF-0 Folder Drop Vault's root from an external runner.

No upload, private share URL, credentials, bearer tokens, user files, or site mutation.
Results do NOT attest archive retrieval by this ChatGPT session.
"""
from __future__ import annotations

import argparse
import http.client
import json
import socket
import ssl

HOST = "folder-drop-vault.whoiwts110217.chatgpt.site"


def classify(status: int, *, redirect: str = "") -> str:
    if status in (401, 403):
        return "access_denied"
    if 200 <= status < 300:
        return "root_reachable"
    if 300 <= status < 400:
        if any(term in redirect.lower() for term in ("login", "signin", "sign-in", "oauth")):
            return "login_redirect"
        return "redirect_needs_review"
    if status == 404:
        return "root_not_found"
    if status == 405:
        return "method_not_allowed"
    return "http_error"


def probe(timeout: float = 12.0) -> dict:
    conn = http.client.HTTPSConnection(HOST, timeout=timeout)
    method = "HEAD"
    try:
        conn.request("HEAD", "/", headers={"User-Agent": "CF0-vault-availability-audit/1"})
        response = conn.getresponse()
        status = response.status
        location = response.getheader("Location") or ""
        # A 405 is not evidence of an inaccessible site: some sites disallow HEAD.
        if status == 405:
            conn.close()
            conn = http.client.HTTPSConnection(HOST, timeout=timeout)
            method = "GET"
            conn.request("GET", "/", headers={
                "Range": "bytes=0-0",
                "User-Agent": "CF0-vault-availability-audit/1",
            })
            response = conn.getresponse()
            status = response.status
            location = response.getheader("Location") or ""
        return {"host": HOST, "method": method, "http_status": status,
                "state": classify(status, redirect=location),
                "share_files_fetched": 0, "end_to_end_archive_access_verified": False}
    except socket.gaierror:
        state = "dns_unavailable"
    except ssl.SSLError:
        state = "tls_error"
    except (OSError, http.client.HTTPException):
        state = "connection_unavailable"
    finally:
        conn.close()
    return {"host": HOST, "method": method, "http_status": None, "state": state,
            "share_files_fetched": 0, "end_to_end_archive_access_verified": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=12.0)
    args = parser.parse_args()
    if not 0.2 <= args.timeout <= 30.0:
        parser.error("timeout must be between 0.2 and 30 seconds")
    print(json.dumps(probe(args.timeout), sort_keys=True))


if __name__ == "__main__":
    main()
