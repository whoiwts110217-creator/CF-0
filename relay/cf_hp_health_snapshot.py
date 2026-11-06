#!/usr/bin/env python3
"""Read-only, privacy-minimized local CF-0 HP health snapshot.

No network, no tokens, no shell execution, no writes. JSON on stdout only.
For future explicit integration with the existing scheduled relay.
"""
import json
import contextlib
import pathlib
import sqlite3
from datetime import datetime, timezone

def snapshot(home=None):
    home = pathlib.Path(home) if home is not None else pathlib.Path.home()
    db = home / ".caveman_focus_relay" / "relay.sqlite3"
    result = {
        "schema": "cf0.hp_health.v1",
        "collected_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "db_exists": db.is_file(),
        "receipt_count": None,
        "ping_receipt_count": None,
        "last_receipt_status": None,
        "error": None,
    }
    if not db.is_file():
        return result
    try:
        # SQLite read-only URI avoids accidentally creating a new database.
        with contextlib.closing(sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True, timeout=2)) as con:
            result["receipt_count"] = con.execute("SELECT COUNT(*) FROM receipts").fetchone()[0]
            rows = con.execute("SELECT receipt FROM receipts ORDER BY rowid DESC LIMIT 200").fetchall()
        result["ping_receipt_count"] = 0  # among the most recent 200 rows only
        for idx, (raw,) in enumerate(rows):
            try:
                receipt = json.loads(raw)
            except (TypeError, ValueError):
                result["error"] = "malformed_receipt"
                continue
            if not isinstance(receipt, dict):
                result["error"] = "malformed_receipt"
                continue
            if idx == 0:
                status = receipt.get("status")
                result["last_receipt_status"] = status if status in ("completed", "failed") else "other"
            if receipt.get("result") == {"pong": True, "protocol": 1}:
                result["ping_receipt_count"] += 1
    except (OSError, sqlite3.Error, ValueError, TypeError):
        result["error"] = "state_unavailable"
    return result

if __name__ == "__main__":
    print(json.dumps(snapshot(), sort_keys=True))
