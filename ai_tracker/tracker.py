"""CF-0 public-safe agent outreach tracker. Standard library only."""
import argparse
import datetime as dt
import json
from pathlib import Path

STATES = {"discovered", "drafted", "posted", "responded", "verified", "rejected"}
EVENTS = {"discover": "discovered", "draft": "drafted", "post": "posted",
          "reply": "responded", "verify": "verified", "reject": "rejected"}
TRANSITIONS = {
    None: {"discovered"},
    "discovered": {"drafted", "rejected"},
    "drafted": {"posted", "rejected"},
    "posted": {"responded", "rejected"},
    "responded": {"verified", "rejected"},
    "verified": set(),
    "rejected": set(),
}
REQUIRED = {"timestamp", "event", "target", "evidence", "operator"}
FORBIDDEN = ("password", "api_key", "secret", "token", "private_chat", "cash_tag")

def read_events(path):
    if not Path(path).exists():
        return []
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]

def validate(event, history):
    if not isinstance(event, dict) or REQUIRED - event.keys():
        raise ValueError("missing required fields")
    if event["event"] not in EVENTS:
        raise ValueError("invalid event")
    if any(not isinstance(event[k], str) or not event[k].strip() for k in REQUIRED):
        raise ValueError("required fields must be nonempty strings")
    dt.datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
    if any(word in json.dumps(event).lower() for word in FORBIDDEN):
        raise ValueError("potential private or credential content")
    previous = next((EVENTS[e["event"]] for e in reversed(history) if e["target"] == event["target"]), None)
    state = EVENTS[event["event"]]
    if state not in TRANSITIONS[previous]:
        raise ValueError(f"invalid transition {previous} -> {state}")
    if event["event"] in {"post", "reply", "verify"} and not event["evidence"].startswith("https://"):
        raise ValueError("posting, replies and verification require a public evidence URL")
    if event["event"] == "verify" and not event.get("test"):
        raise ValueError("verification requires a reproducible test")
    return event

def append(path, event):
    history = read_events(path)
    validate(event, history)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("a", encoding="utf-8") as out:
        out.write(json.dumps(event, sort_keys=True, ensure_ascii=False) + "\n")

def report(path):
    events = read_events(path)
    latest = {}
    for event in events:
        validate(event, [e for e in events if e is not event and events.index(e) < events.index(event)])
        latest[event["target"]] = EVENTS[event["event"]]
    return {"targets": len(latest), "states": {s: sum(v == s for v in latest.values()) for s in sorted(STATES)},
            "verified_agents": sum(v == "verified" for v in latest.values())}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ledger", default="ai_tracker/events.jsonl")
    sub = p.add_subparsers(dest="action", required=True)
    sub.add_parser("report")
    add = sub.add_parser("record")
    for flag in ("event", "target", "evidence", "operator"):
        add.add_argument("--" + flag, required=True)
    add.add_argument("--test", default="")
    args = p.parse_args()
    if args.action == "report":
        print(json.dumps(report(args.ledger), indent=2))
    else:
        append(args.ledger, {"timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
            "event": args.event, "target": args.target, "evidence": args.evidence,
            "operator": args.operator, "test": args.test})
        print(json.dumps(report(args.ledger), indent=2))

if __name__ == "__main__":
    main()
