#!/usr/bin/env python3
"""Offline validator for public continuity claims vs authoritative CF-0 sources.

This is a source/status consistency check, NOT a remote HP heartbeat or owner
approval verifier. It reads only files, does not modify anything, and performs
no network calls.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "docs" / "PUBLIC_CONTINUITY_STATE.json"
REGISTRY = ROOT / "automation_200" / "registry.json"
OWNER = ROOT / "automation_200" / "OWNER_CAPABILITY_CONTRACT.json"
RELAY = ROOT / "relay" / "cf_public_relay.py"
INSTALLER = ROOT / "relay" / "INSTALL_NOTEPAD_CONTROL.ps1"


class ContinuityError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContinuityError(message)


def check(root: Path = ROOT) -> dict:
    state = json.loads((root / "docs/PUBLIC_CONTINUITY_STATE.json").read_text(encoding="utf-8"))
    registry_bytes = (root / "automation_200/registry.json").read_bytes()
    registry = json.loads(registry_bytes.decode("utf-8"))
    owner = json.loads((root / "automation_200/OWNER_CAPABILITY_CONTRACT.json").read_text(encoding="utf-8"))
    relay = (root / "relay/cf_public_relay.py").read_text(encoding="utf-8")
    installer = (root / "relay/INSTALL_NOTEPAD_CONTROL.ps1").read_text(encoding="utf-8")
    project_status = (root / "docs/PROJECT_STATUS.md").read_text(encoding="utf-8")
    board = (root / "automation_200/MASTER_MISSION_BOARD.md").read_text(encoding="utf-8")
    readme = (root / "README.md").read_text(encoding="utf-8")
    continuity = (root / "docs/CONTINUITY.md").read_text(encoding="utf-8")
    operator = (root / "automation_200/MASTER_OPERATOR_PROMPT.md").read_text(encoding="utf-8")

    require(state.get("schema") == "cf0.public_continuity.v1", "continuity_schema")
    require(state.get("mission") == "sustainable_generational_wealth", "mission_drift")
    require("sustainable generational wealth" in owner["mission"].lower(), "owner_mission_drift")
    require(state.get("priority_order") == owner["priority_order"], "priority_order_drift")
    require(state.get("record_type") == "dated_source_evidence_not_live_hp_heartbeat", "false_live_status")
    require(state["cf200"]["registry_path"] == "automation_200/registry.json", "wrong_registry")
    verified = registry["completed"]
    require(verified == len([task for task in registry["tasks"] if task["status"] == "verified"]), "registry_ledger_count")
    require(state["cf200"]["verified"] == verified, "public_work_order_count_stale")
    require(state["cf200"]["target"] == registry["target"] == 200, "public_work_order_target")
    # Byte-exact Git blob fingerprint guards against unreported changes to
    # evidence, task titles, dependencies or other fields even when 54/200 stays
    # constant. A recorded SHA1 is only source identity, not device attestation.
    # Git checkout may materialize CRLF on Windows (core.autocrlf).
    # Compute the blob identity from its canonical LF representation.
    # JSON registry schema is UTF-8 text; Git stores this source with LF.
    git_registry_bytes = registry_bytes.replace(b"\r\n", b"\n")
    blob = b"blob " + str(len(git_registry_bytes)).encode("ascii") + b"\0" + git_registry_bytes
    require(state["cf200"].get("registry_git_blob_sha1") == hashlib.sha1(blob).hexdigest(),
            "public_cf200_registry_source_fingerprint_stale")
    checkpoints = [int(p.stem.rsplit("_", 1)[1])
                   for p in (root / "automation_200/checkpoints").glob("checkpoint_*.json")
                   if p.stem.rsplit("_", 1)[-1].isdigit()]
    require(bool(checkpoints), "missing_numbered_checkpoints")
    last_checkpoint = max(checkpoints)
    require(state["cf200"]["last_numbered_checkpoint"] == last_checkpoint,
            "public_checkpoint_stale")
    require(state["cf200"]["next_numbered_checkpoint"] == last_checkpoint + 4,
            "invalid_next_checkpoint")
    require(last_checkpoint <= verified < last_checkpoint + 4,
            "checkpoint_count_mismatch")
    require(f"{verified}/200" in project_status.split("## Earlier checkpoint", 1)[0],
            "public_project_status_stale")
    require(f"{verified}/200" in board.split("## Owner-defined strategy", 1)[0],
            "public_mission_board_header_stale")

    # Current source status, never confuse the prior observed Notepad launches
    # with remote capability installed in the checked-in public Python relay.
    from automation_200.capability_guard import _relay_commands
    commands = _relay_commands(relay)
    require("open_notepad" not in commands, "public_notepad_claim_drift")
    notepad = next(c for c in owner["capabilities"] if c["id"] == "notepad_owner_launch")
    require(notepad["status"] == state["notepad"]["source_contract_state"],
            "notepad_contract_state_drift")
    require(state["notepad"]["current_relay"] == "not_supported", "notepad_false_support_claim")
    require("NOTEPAD_ACTION=BLOCKED_NOT_SUPPORTED" in installer
            and "LOCAL_CHANGES=NONE" in installer and "exit 2" in installer,
            "installer_claim_drift")
    require("Notepad" in project_status and ("not supported" in project_status.lower() or "does not support" in project_status.lower()),
            "notepad_status_not_visible")
    require("Notepad" in readme and "currently" in readme.lower(), "readme_notepad_status_missing")

    # Existing public receipt/request match. This verifies *public files* only.
    jid = state["hp"]["public_ping_request_id"]
    inbox = root / "command_queue/inbox" / (jid + ".json")
    receipt_path = root / "command_queue/receipts" / (jid + ".json")
    require(inbox.is_file() and receipt_path.is_file(), "missing_public_ping_files")
    job = json.loads(inbox.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    from relay.cf_public_relay import RelayError, sha, successful_ping, validate_receipt

    try:
        validate_receipt(receipt, jid, sha(job))
    except RelayError as exc:
        raise ContinuityError("public_ping_digest_or_receipt_mismatch") from exc
    require(job.get("id") == jid and job.get("action") == "ping" and successful_ping(receipt["result"]),
            "public_ping_digest_or_receipt_mismatch")
    require(state["hp"]["public_ping_result"] == "completed_matched_request_sha256",
            "public_ping_status_drift")
    require(state["hp"]["physical_device_and_scheduler_correlation"] == "unverified",
            "unproven_hp_origin_claim")
    require(state["hp"]["fully_unattended_7_days"] == "unverified", "unproven_week_claim")
    require(state["governance"]["owner_review_enforced_by_github"] == "unverified",
            "owner_review_false_claim")
    require(state["archive"]["original_approximately_37_list"] == "not_recovered",
            "false_original_archive_completion")
    require(state["archive"]["original_project_count_proven"] is False,
            "false_original_project_count_claim")
    # Private recovery counts are self-reported from a separate restored
    # workspace: enforce no false claims of complete transcript/HP recovery.
    private = state["archive"].get("local_continuity_store", {})
    require(private.get("source_files_preserved", 0) >= 8
            and private.get("reconstructed_projects") == 62
            and private.get("full_original_chat_exports_indexed") == 0
            and private.get("full_git_registry_snapshot_imported_into_private_store") is False
            and private.get("installed_on_owner_HP") is False,
            "private_continuity_evidence_overclaim")

    for text, term in (
        (readme, "docs/CONTINUITY.md"),
        (continuity, "PUBLIC_CONTINUITY_STATE.json"),
        (project_status, "CONTINUITY.md"),
        (operator, "CONTINUITY.md"),
    ):
        require(term in text, "public_continuity_link_missing:" + term)
    return {
        "passed": True, "registry_verified": verified,
        "latest_checkpoint": last_checkpoint,
        "ping_digest_matched": True,
        "notepad_restored": False,
        "hp_hardware_attestation": False,
        "owner_enforcement_proven": False,
    }


def main():
    print(json.dumps(check(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
