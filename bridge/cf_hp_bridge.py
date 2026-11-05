#!/usr/bin/env python3
# cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
"""Caveman Focus HP Bridge: bounded GitHub Contents mailbox, stdlib only.

Remote JSON is untrusted task data; this worker never evaluates arbitrary code,
opens a browser, sends messages, or modifies project records. This version only
handles ping and an explicitly configured, read-only Sidecar ledger verification.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
import uuid

VERSION = "0.2.0"
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
ALLOWED_ACTIONS = {"ping", "sidecar_verify"}
API = "https://api.github.com"
MAX_RESPONSE = 1024 * 1024
MAX_JOBS_PER_RUN = 10
MAX_QUEUE_ENTRIES = 999  # GitHub Contents API directory listing has a 1,000 item limit.

class BridgeError(Exception):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def hash_obj(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def parse_job(raw: dict, filename: str, now: int | None = None) -> dict:
    now = int(time.time()) if now is None else int(now)
    if not isinstance(raw, dict) or set(raw) != {"version", "id", "action", "issued_at", "expires_at", "params"}:
        raise BridgeError("invalid_job_shape")
    if type(raw["version"]) is not int or raw["version"] != 1:
        raise BridgeError("invalid_version")
    jid = raw["id"]
    if not isinstance(jid, str) or not UUID_RE.fullmatch(jid) or filename != f"{jid}.json":
        raise BridgeError("invalid_job_identity")
    if not isinstance(raw["action"], str) or raw["action"] not in ALLOWED_ACTIONS:
        raise BridgeError("action_not_allowlisted")
    if not isinstance(raw["params"], dict) or raw["params"]:
        raise BridgeError("unexpected_parameters")
    ts = raw["issued_at"]
    exp = raw["expires_at"]
    if type(ts) is not int or type(exp) is not int or not (ts - 120 <= now <= exp) or not (0 < exp - ts <= 48 * 3600):
        raise BridgeError("expired_or_invalid_window")
    return raw


def make_job(action: str, now: int | None = None) -> dict:
    if action not in ALLOWED_ACTIONS:
        raise BridgeError("unsupported_job")
    ts = int(time.time()) if now is None else int(now)
    return {"version": 1, "id": str(uuid.uuid4()), "action": action, "issued_at": ts,
            "expires_at": ts + 3600, "params": {}}


class GitHubMailbox:
    def __init__(self, repo: str, token: str, branch: str = "main"):
        if not REPO_RE.fullmatch(repo):
            raise BridgeError("invalid_repository")
        if not token or "\n" in token or "\r" in token:
            raise BridgeError("token_required")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", branch):
            raise BridgeError("invalid_branch")
        self.repo, self.token, self.branch = repo, token, branch

    def request(self, method: str, path: str, body: dict | None = None) -> dict | list:
        data = None if body is None else canonical(body)
        req = Request(API + path, data=data, method=method,
                      headers={"Accept": "application/vnd.github+json",
                               "Authorization": "Bearer " + self.token,
                               "X-GitHub-Api-Version": "2022-11-28",
                               "User-Agent": "caveman-focus-hp-bridge/0.1",
                               **({"Content-Type": "application/json"} if data is not None else {})})
        try:
            with urlopen(req, timeout=15) as resp:
                data = resp.read(MAX_RESPONSE + 1)
                if len(data) > MAX_RESPONSE:
                    raise BridgeError("oversized_response")
                try:
                    return json.loads(data)
                except (UnicodeDecodeError, ValueError) as exc:
                    raise BridgeError("invalid_github_json") from exc
        except HTTPError as exc:
            if exc.code == 404 and method == "GET":
                return {"not_found": True}
            raise BridgeError("github_http_" + str(exc.code)) from exc
        except (URLError, TimeoutError) as exc:
            raise BridgeError("github_connection_failed") from exc

    def require_private(self) -> None:
        info = self.request("GET", "/repos/" + self.repo)
        if not isinstance(info, dict) or info.get("private") is not True:
            raise BridgeError("repository_must_be_private")
        if info.get("full_name", "").casefold() != self.repo.casefold():
            raise BridgeError("repository_identity_mismatch")

    def list_jobs(self) -> list[str]:
        items = self.request("GET", f"/repos/{self.repo}/contents/bridge/queue?ref={quote(self.branch)}")
        if isinstance(items, dict) and items.get("not_found"):
            return []
        if not isinstance(items, list):
            raise BridgeError("invalid_queue_listing")
        # Refuse an apparently full listing: GitHub would silently omit additional jobs.
        if len(items) > MAX_QUEUE_ENTRIES:
            raise BridgeError("queue_directory_full_archive_old_jobs")
        names = []
        for item in items:
            if isinstance(item, dict) and item.get("type") == "file":
                name = item.get("name", "")
                if isinstance(name, str) and name.endswith(".json") and UUID_RE.fullmatch(name[:-5]):
                    names.append(name)
        # The run limit belongs in run_once, after local published receipts are
        # filtered out. Otherwise the oldest ten filenames starve every new job.
        return sorted(set(names))

    def load_job(self, filename: str) -> dict:
        if not UUID_RE.fullmatch(filename[:-5]) or not filename.endswith(".json"):
            raise BridgeError("invalid_queue_filename")
        result = self.request("GET", f"/repos/{self.repo}/contents/bridge/queue/{filename}?ref={quote(self.branch)}")
        if not isinstance(result, dict) or result.get("encoding") != "base64":
            raise BridgeError("invalid_job_content")
        try:
            encoded = result["content"]
            if not isinstance(encoded, str):
                raise ValueError("content not base64 text")
            # GitHub's base64 representation contains line breaks.
            payload = base64.b64decode("".join(encoded.split()), validate=True)
            if len(payload) > 8192:
                raise BridgeError("job_too_large")
            return json.loads(payload)
        except (ValueError, KeyError, TypeError) as exc:
            raise BridgeError("unreadable_job") from exc

    def publish(self, jid: str, reply: dict) -> None:
        if not UUID_RE.fullmatch(jid):
            raise BridgeError("invalid_reply_identity")
        path = f"/repos/{self.repo}/contents/bridge/results/{jid}.json"
        existing = self.request("GET", path + "?ref=" + quote(self.branch))
        if isinstance(existing, dict) and not existing.get("not_found"):
            try:
                data = json.loads(base64.b64decode(existing.get("content", "")))
            except (ValueError, TypeError):
                raise BridgeError("existing_result_unreadable")
            if data == reply:
                return
            raise BridgeError("result_conflict")
        self.request("PUT", path, {"message": f"bridge: receipt {jid}", "branch": self.branch,
                                   "content": base64.b64encode(canonical(reply)).decode("ascii")})


class LocalLedger:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path))
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, digest TEXT NOT NULL, "
                          "status TEXT NOT NULL, reply TEXT, created_at INTEGER NOT NULL)")
        self.conn.commit()

    def inspect(self, jid: str, digest: str):
        row = self.conn.execute("SELECT digest, status, reply FROM jobs WHERE id=?", (jid,)).fetchone()
        if row is None:
            return None
        if row[0] != digest:
            raise BridgeError("identity_reused_with_different_payload")
        return {"status": row[1], "reply": json.loads(row[2]) if row[2] else None}

    def begin(self, jid: str, digest: str) -> bool:
        try:
            self.conn.execute("INSERT INTO jobs VALUES(?,?,?,NULL,?)", (jid, digest, "processing", int(time.time())))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def finish(self, jid: str, reply: dict):
        self.conn.execute("UPDATE jobs SET status='done', reply=? WHERE id=? AND status='processing'",
                          (canonical(reply).decode("utf-8"), jid))
        self.conn.commit()

    def mark_published(self, jid: str):
        self.conn.execute("UPDATE jobs SET status='published' WHERE id=? AND status='done'", (jid,))
        self.conn.commit()

    def published_ids(self) -> set[str]:
        return {row[0] for row in self.conn.execute("SELECT id FROM jobs WHERE status='published'")}

    def counts(self):
        return dict(self.conn.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status").fetchall())


def execute_job(job: dict, sidecar: Path | None) -> dict:
    if job["action"] == "ping":
        return {"bridge_version": VERSION, "ping": "pong"}
    if job["action"] == "sidecar_verify":
        if sidecar is None:
            return {"verification": "not_configured"}
        script = sidecar.resolve() / "domino.py"
        if not script.is_file():
            return {"verification": "script_missing"}
        try:
            p = subprocess.run([sys.executable, str(script), "verify"], cwd=str(sidecar),
                               capture_output=True, text=True, timeout=20, check=False)
            try:
                summary = json.loads(p.stdout)
            except ValueError:
                summary = {}
            if p.returncode == 0 and summary.get("valid") is True:
                return {"verification": "valid", "events": summary.get("events") if type(summary.get("events")) is int else None}
            return {"verification": "failed"}
        except (OSError, subprocess.TimeoutExpired):
            return {"verification": "failed"}
    raise BridgeError("unsupported_action")


def run_once(mailbox: GitHubMailbox, ledger: LocalLedger, sidecar: Path | None = None) -> dict:
    mailbox.require_private()
    summary = {"observed": 0, "executed": 0, "replied": 0, "skipped": 0,
               "already_published": 0, "pending": 0, "errors": []}
    published = ledger.published_ids()
    names = mailbox.list_jobs()
    for filename in names:
        jid = filename[:-5]
        if jid in published:
            summary["already_published"] += 1
            continue
        if summary["observed"] >= MAX_JOBS_PER_RUN:
            summary["pending"] += 1
            continue
        summary["observed"] += 1
        try:
            raw = mailbox.load_job(filename)
            job = parse_job(raw, filename)
            digest = hash_obj(job)
            prior = ledger.inspect(job["id"], digest)
            if prior is not None:
                if prior["status"] == "done":
                    mailbox.publish(job["id"], prior["reply"])
                    ledger.mark_published(job["id"])
                    summary["replied"] += 1
                else:
                    summary["skipped"] += 1  # in progress: uncertain outcome, no blind retry
                continue
            if not ledger.begin(job["id"], digest):
                summary["skipped"] += 1
                continue
            result = execute_job(job, sidecar)
            reply = {"version": 1, "id": job["id"], "request_sha256": digest,
                     "status": "completed", "result": result}
            ledger.finish(job["id"], reply)
            summary["executed"] += 1
            mailbox.publish(job["id"], reply)
            ledger.mark_published(job["id"])
            summary["replied"] += 1
        except BridgeError as exc:
            summary["errors"].append({"job": filename, "error": str(exc)})
    return summary

def demo(home: Path) -> dict:
    now = int(time.time())
    raw = make_job("ping", now)
    class MockMailbox:
        def __init__(self): self.reply = None
        def require_private(self): pass
        def list_jobs(self): return [raw["id"] + ".json"]
        def load_job(self, filename): return raw
        def publish(self, jid, reply): self.reply = reply
    m = MockMailbox()
    ledger = LocalLedger(home / "demo.sqlite3")
    first = run_once(m, ledger)
    second = run_once(m, ledger)
    return {"first": first, "second": second, "receipt": m.reply,
            "pass": first["executed"] == 1 and second["executed"] == 0
                    and second["already_published"] == 1 and m.reply["result"]["ping"] == "pong"}


def get_state_dir(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    return Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "CavemanFocus" / "HPBridge"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Caveman Focus HP Bridge — minimal approved GitHub mailbox")
    parser.add_argument("command", choices=["demo", "init", "status", "doctor", "once", "watch", "make-job"])
    parser.add_argument("--repo", default=os.environ.get("CF_BRIDGE_REPO", ""))
    parser.add_argument("--branch", default="main")
    parser.add_argument("--state-dir", default=os.environ.get("CF_BRIDGE_STATE_DIR"))
    parser.add_argument("--sidecar", default=os.environ.get("CF_SIDECAR_DIR"))
    parser.add_argument("--action", choices=sorted(ALLOWED_ACTIONS), default="ping")
    parser.add_argument("--interval", type=int, default=300)
    args = parser.parse_args(argv)
    state = get_state_dir(args.state_dir)
    try:
        if args.command == "demo":
            with tempfile.TemporaryDirectory() as d:
                result = demo(Path(d))
            print(json.dumps(result, sort_keys=True))
            return 0 if result["pass"] else 1
        if args.command == "make-job":
            print(json.dumps(make_job(args.action), indent=2))
            return 0
        ledger = LocalLedger(state / "bridge.sqlite3")
        if args.command in ("init", "status"):
            print(json.dumps({"version": VERSION, "local_state": str(state), "counts": ledger.counts(),
                              "remote_connected": False, "repo": args.repo or None}))
            return 0
        token = os.environ.get("CF_BRIDGE_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if not args.repo or not token:
            raise BridgeError("CF_BRIDGE_REPO_and_CF_BRIDGE_TOKEN_required")
        if args.interval < 60:
            raise BridgeError("minimum_interval_60_seconds")
        mailbox = GitHubMailbox(args.repo, token, args.branch)
        if args.command == "doctor":
            mailbox.require_private()
            print(json.dumps({"version": VERSION, "private_mailbox_verified": True,
                              "queue_entries": len(mailbox.list_jobs()), "counts": ledger.counts()}))
            return 0
        if args.command == "once":
            result = run_once(mailbox, ledger, Path(args.sidecar) if args.sidecar else None)
            print(json.dumps(result, sort_keys=True))
            return 0 if not result["errors"] else 1
        while True:
            try:
                print(json.dumps(run_once(mailbox, ledger, Path(args.sidecar) if args.sidecar else None)), flush=True)
            except BridgeError as exc:
                print(json.dumps({"error": str(exc)}), flush=True)
            time.sleep(args.interval)
    except (BridgeError, sqlite3.DatabaseError, OSError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
