#!/usr/bin/env python3
"""Owner-launched, read-only CF-200 live desktop status. No remote command channel."""
import json
import threading
import tkinter as tk
import urllib.request
from datetime import datetime
from tkinter.scrolledtext import ScrolledText

REPO = "whoiwts110217-creator/CF-0"
BASE = "https://raw.githubusercontent.com/" + REPO + "/main/"
API = "https://api.github.com/repos/" + REPO
INTERVAL_MS = 30000
PROBE_ID = "1bd3a644-9b80-4d05-8cb1-7043c7853d54"
PROBE_DIGEST = "bdd1b0e1c0b45e1b1618c16e814fc9a606e6530bf2419978ee9c510055f8ce16"

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
    return ("CAVEMAN FOCUS — LIVE STATUS\n"
            + "Updated locally: " + datetime.now().astimezone().isoformat(timespec="seconds") + "\n"
            + "Verified: " + str(registry["completed"]) + " / " + str(registry["target"]) + "\n"
            + "Registry: " + str(registry["status"]) + "\n"
            + "Latest commit: " + sha + " — " + message + "\n"
            + "Source: https://github.com/" + REPO + "\n\n"
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
                def done():
                    state["busy"] = False
                    if not result.startswith("REFRESH FAILED:") and "\\nREFRESH FAILED:" not in result:
                        state["last"] = result
                    display(result)
                try:
                    root.after(0, done)
                except RuntimeError:
                    pass
            threading.Thread(target=work, daemon=True).start()
        root.after(INTERVAL_MS, refresh)
    refresh()
    root.mainloop()

if __name__ == "__main__":
    main()
