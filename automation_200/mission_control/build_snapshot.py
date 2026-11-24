"""Build a public-only, commit-pinned fallback for CF-0 Mission Control.

No network, credentials, private data or HP control. Reads fixed public
repository sources and writes only the dashboard baseline.
"""
import json
import pathlib
import re
import subprocess
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "automation_200/mission_control/dist/snapshot.json"
MAX_HEALTH_REPORT_BYTES = 1024
UUID = re.compile(r"^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$")
UTC_STAMP = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?(?:Z|[+-]00:00)$")


def public_collection_time(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, str) and len(value) <= 48 and UTC_STAMP.fullmatch(value):
        try:
            stamp = datetime.fromisoformat(value)
            if stamp.utcoffset() == timezone.utc.utcoffset(stamp):
                return value
        except ValueError:
            pass
    # Invalid sentinel: never preserve malformed strings or unexpected objects.
    return ""


def health_snapshot(path: pathlib.Path) -> dict:
    try:
        with path.open("rb") as source:
            raw = source.read(MAX_HEALTH_REPORT_BYTES + 1)
    except FileNotFoundError:
        return {"health": "not_published"}
    except OSError:
        return {"health": "unavailable"}
    if len(raw) > MAX_HEALTH_REPORT_BYTES:
        return {"health": "invalid"}
    try:
        report = json.loads(raw.decode("utf-8"))
    except ValueError:
        return {"health": "invalid"}
    if isinstance(report, dict) and report.get("schema") == "cf0.hp_health.v1":
        result = {"health": "available"}
        if "collected_utc" in report:
            # Keep only bounded collection time, never arbitrary report fields.
            # The browser reclassifies age at read time, not at bundle creation.
            result["healthCollectedUtc"] = public_collection_time(report["collected_utc"])
        return result
    return {"health": "invalid"}


def health_availability(path: pathlib.Path) -> str:
    return health_snapshot(path)["health"]


def public_tool_inventory(path: pathlib.Path) -> dict | None:
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(contract, dict) or contract.get("schema") != "cf0.owner_capability_contract.v1":
        return None
    capabilities = contract.get("capabilities")
    if not isinstance(capabilities, list) or not all(
        isinstance(capability, dict)
        and isinstance(capability.get("id"), str)
        and isinstance(capability.get("status"), str)
        for capability in capabilities
    ):
        return None
    return {
        "schema": contract["schema"],
        "capabilities": [
            {"id": capability["id"], "status": capability["status"]}
            for capability in capabilities
        ],
    }


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
    result = {
        "commit": commit,
        "registry": registry,
        "state": state,
        **health_snapshot(root / "relay/health/latest.json"),
    }
    contract = public_tool_inventory(root / "automation_200/OWNER_CAPABILITY_CONTRACT.json")
    if contract is not None:
        result["contract"] = contract
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
