"""Build a public-only, commit-pinned fallback for CF-0 Mission Control.

No network, credentials, private data or HP control. Reads four allowlisted
public repository paths and writes only the dashboard's small JSON baseline.
"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "automation_200/mission_control/dist/snapshot.json"
UUID = re.compile(r"^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$")


def build(root: pathlib.Path, commit: str) -> dict:
    if not re.fullmatch(r"[a-f0-9]{40}", commit):
        raise ValueError("Expected a pinned 40-character commit SHA")
    registry = json.loads((root / "automation_200/registry.json").read_text(encoding="utf-8"))
    state = json.loads((root / "docs/PUBLIC_CONTINUITY_STATE.json").read_text(encoding="utf-8"))
    if registry.get("schema") != "CF200.1" or registry.get("target") != 200 or len(registry.get("tasks", [])) != 200:
        raise ValueError("Invalid public CF-200 registry")
    if sum(t.get("status") == "verified" for t in registry["tasks"]) != registry.get("completed"):
        raise ValueError("Registry count mismatch")
    if state.get("schema") != "cf0.public_continuity.v1":
        raise ValueError("Invalid public continuity state")
    result = {"commit": commit, "registry": registry, "state": state, "health": "not_published"}
    identifier = state.get("hp", {}).get("public_ping_request_id", "")
    if isinstance(identifier, str) and UUID.fullmatch(identifier):
        inbox = root / "command_queue/inbox" / (identifier + ".json")
        receipt = root / "command_queue/receipts" / (identifier + ".json")
        if inbox.is_file() and receipt.is_file():
            result["ping"] = {
                "request": json.loads(inbox.read_text(encoding="utf-8")),
                "receipt": json.loads(receipt.read_text(encoding="utf-8")),
            }
    return result


def main() -> None:
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    data = build(ROOT, commit)
    OUTPUT.write_text(json.dumps(data, separators=(",", ":"), ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"Bundled public CF-200 snapshot at {commit[:12]} ({data['registry']['completed']}/200)")


if __name__ == "__main__":
    main()
