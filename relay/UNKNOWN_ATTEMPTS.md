# CF-069 — Durable unknown in-progress recovery (source patch)

**Owner:** Kiara Lynn Rose Smith's Caveman Focus  
**Status:** Source- and CI-tested design; not automatically deployed on the owner's HP.

## Problem

The existing relay saved its result *after* running an allowlisted action. If the Python process disappeared between running an action and saving a local SQLite receipt, the next five-minute poll could try the same request again without knowing whether the first attempt took effect.

## Behavior after this change

- Before calling `execute()`, the worker commits a small SQLite `attempts` row keyed by the original request UUID and canonical request SHA-256, with status `in_progress`.
- A successful action atomically saves the original completed receipt and transitions its attempt to `completed`. Publication to GitHub may be retried from that saved receipt without repeating the action.
- A crash or execution error **after** the start marker but **before** the completed receipt leaves an `in_progress` marker. A later poll reports that request as `uncertain` and **does not repeat the action** or fabricate a successful public receipt, even if the original request TTL has expired.
- If a request with the same UUID but different digest appears, processing fails closed as `attempt_conflict`. Invalid or expired requests without existing attempts are rejected before inserting any start marker.
- `python relay/cf_public_relay.py status` prints an aggregate `uncertain` count in addition to the completed receipt count, without exposing local private data or request bodies.
- Database initialization adds a table using `CREATE TABLE IF NOT EXISTS`; legacy `receipts` and `meta` entries are retained.

## Tradeoff and authority

This favors **at-most-once attempts over guaranteed completion**. If the worker crashes immediately after persisting `in_progress` but before actually performing the action, the system still conservatively treats the request as uncertain. It cannot distinguish that case from a crash just after an action took effect. A future owner-reviewed reconciliation process could resolve uncertain entries after independently checking local results; **none is supplied or authorized by this patch**. Never delete an uncertain row just to force a retry.

The public relay remains restricted to `ping`, `hp_status` and configured read-only `sidecar_verify`. It does not gain remote shell/GUI control, install anything, or read private documents. A cloud CI success is **not** evidence of installation on the owner's physical HP.

## Reproducible test

```powershell
python -m unittest discover -s relay/tests -p test_unknown_in_progress.py -v
python -m unittest discover -s relay/tests -v
```

The first suite uses a child Python process intentionally terminated *during* the action, then confirms restart cannot rerun it or publish a success receipt. It also covers TTL expiry, request digest conflict, Windows-safe SQLite fixture cleanup, aggregate unknown count, normal completed receipt replay, and a preexisting SQLite database without the new table.
