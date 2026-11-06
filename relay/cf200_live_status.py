#!/usr/bin/env python3
"""Owner-launched, read-only CF-200 live desktop status. No remote command channel."""
import json
import queue
import threading
import tkinter as tk
import urllib.request
from datetime import datetime
from tkinter.scrolledtext import ScrolledText

REPO = "whoiwts110217-creator/CF-0"
BASE = "https://raw.githubusercontent.com/" + REPO + "/main/"
API = "https://api.github.com/repos/" + REPO
INTERVAL_MS = 30000
PROBE_ID = "aeccc8a2-217f-4786-aaaf-19b2fc9ff35a"
PROBE_DIGEST = "f669747a15956dd273c00afc3d84e543196ff6d5347cf861a0c4f9802275b2db"

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "CF200-Local-Status/1.0"})
    with urllib.request.urlopen(req, timeout=12) as response:
        return json.load(response)

def probe_summary(fetch=None):
    """Public receipt evidence is not unattended scheduler evidence."""
    reader = fetch or fetch_json
    try:
        receipt = reader(BASE + "command_queue/receipts/" + PROBE_ID + ".json")
    except Exception:
        return "HP ping receipt: unavailable"
    valid = (isinstance(receipt, dict) and receipt.get("id") == PROBE_ID
             and receipt.get("request_sha256") == PROBE_DIGEST
             and receipt.get("status") == "completed"
             and receipt.get("result") == {"pong": True, "protocol": 1})
    return ("HP ping receipt: matching completed ping; scheduler origin UNVERIFIED"
            if valid else "HP ping receipt: mismatched or invalid")


def snapshot():
    registry = fetch_json(BASE + "automation_200/registry.json")
    commits = fetch_json(API + "/commits?per_page=1")
    if not isinstance(commits, list) or not commits:
        raise ValueError("No public commit metadata")
    head = commits[0]
    sha = head["sha"][:12]
    message = head["commit"]["message"].splitlines()[0][:140]
    runs = fetch_json(API + "/actions/runs?per_page=1")
    recent = runs.get("workflow_runs", []) if isinstance(runs, dict) else []
    if recent:
        run = recent[0]
        ci = (str(run.get("name", "Workflow"))[:70] + ": "
              + str(run.get("conclusion") or run.get("status") or "unknown")
              + " (" + str(run.get("html_url", "")) + ")")
    else:
        ci = "No recent workflow result available"
    return ("CAVEMAN FOCUS — LIVE STATUS\n"
            + "Updated locally: " + datetime.now().astimezone().isoformat(timespec="seconds") + "\n"
            + "Verified: " + str(registry["completed"]) + " / " + str(registry["target"]) + "\n"
            + "Registry: " + str(registry["status"]) + "\n"
            + "Latest commit: " + sha + " — " + message + "\n"
            + "Source: https://github.com/" + REPO + "\n"
            + "Latest GitHub Actions: " + ci + "\n"
            + "Next HP verification: correlate Windows scheduled run and wrapper outcome with ping receipt.\n\n"
            + probe_summary() + "\n"
            + "HP unattended schedule: NOT VERIFIED without Windows scheduler evidence\n"
            + "This window runs on your Windows desktop only after local launch.\n"
            + "Public commit metadata does not prove CI passed or HP ran.\n")

def main():
    root = tk.Tk()
    root.title("Caveman Focus — Live Status (read-only)")
    root.geometry("820x410")
    view = ScrolledText(root, wrap="word", font=("Consolas", 11))
    view.pack(fill="both", expand=True)
    view.insert("1.0", "Connecting to public CF-0...\n")
    view.configure(state="disabled")
    state = {"busy": False, "last": ""}
    results = queue.SimpleQueue()
    def display(message):
        view.configure(state="normal")
        view.delete("1.0", "end")
        view.insert("1.0", message)
        view.configure(state="disabled")
    def refresh():
        if not state["busy"]:
            state["busy"] = True
            def work():
                try:
                    result = snapshot()
                except Exception as exc:
                    result = state["last"] + "\nREFRESH FAILED: " + type(exc).__name__ + "\n" if state["last"] else "REFRESH FAILED: " + type(exc).__name__
                # Worker never touches Tk; main thread consumes completed results.
                results.put(result)
            threading.Thread(target=work, daemon=True).start()
        root.after(INTERVAL_MS, refresh)
    def drain_results():
        try:
            while True:
                result = results.get_nowait()
                state["busy"] = False
                if "REFRESH FAILED:" not in result:
                    state["last"] = result
                display(result)
        except queue.Empty:
            pass
        root.after(200, drain_results)
    root.after(200, drain_results)
    refresh()
    root.mainloop()

if __name__ == "__main__":
    main()
