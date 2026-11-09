"""Validate an independently supplied executor decision against one watchdog readback.

Source-only contract: does not consume packets, execute work, or attest HP identity.
"""
import re

DECISIONS = frozenset({"accepted_source_only", "rejected", "deferred"})


def verify_consumer_ack(readback: dict, acknowledgement: dict) -> dict:
    """Fail closed unless a separate executor decision binds to one exact packet."""
    if not isinstance(readback, dict) or readback.get("schema") != "cf0.work_handoff_readback.v1":
        raise ValueError("invalid producer readback")
    if readback.get("execution_authorized") is not False:
        raise ValueError("producer packet cannot authorize execution")
    expected = {"schema", "watchdog_run_id", "watchdog_run_attempt", "packet_sha256",
                "executor_run_id", "decision", "execution_authorized"}
    if (not isinstance(acknowledgement, dict) or set(acknowledgement) != expected
            or acknowledgement["schema"] != "cf0.executor_packet_decision.v1"):
        raise ValueError("invalid executor acknowledgement schema")
    for key in ("watchdog_run_id", "watchdog_run_attempt"):
        value = readback.get(key)
        if (type(value) is not int or value <= 0
                or type(acknowledgement[key]) is not int or acknowledgement[key] != value):
            raise ValueError("watchdog run identity mismatch")
    digest = readback.get("packet_sha256")
    if (not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest)
            or acknowledgement["packet_sha256"] != digest):
        raise ValueError("packet digest mismatch")
    executor = acknowledgement["executor_run_id"]
    if not isinstance(executor, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", executor):
        raise ValueError("invalid executor run identity")
    if (type(acknowledgement["decision"]) is not str
            or acknowledgement["decision"] not in DECISIONS
            or acknowledgement["execution_authorized"] is not False):
        raise ValueError("invalid or unauthorized executor decision")
    # Matching untrusted JSON proves equality only, not independent executor origin.\n    return {"schema": "cf0.executor_packet_correlation.v1", "correlated": True,\n            "acknowledgement_origin_verified": False,
            "watchdog_run_id": readback["watchdog_run_id"],
            "watchdog_run_attempt": readback["watchdog_run_attempt"],
            "packet_sha256": digest, "executor_run_id": executor,
            "decision": acknowledgement["decision"], "execution_authorized": False,
            "hp_identity_attested": False}
