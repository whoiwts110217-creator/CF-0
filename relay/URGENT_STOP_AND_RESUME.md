# CF-099 — Owner-local urgent stop and safe resumption

**Status:** documented procedure; no button was pressed, no HP process was terminated, and no schedule was changed by creating this page.  
**Scope:** existing public `CavemanFocusCF0Relay` task and the separately configured `CavemanFocusHPBridge`.  
**Operating boundary:** only the signed-in owner or an authorized local administrator can operate the HP. A public GitHub issue, ChatGPT message or remote queue entry cannot order a shutdown.

## Emergency stop on the physical HP

If the existing CF-0 relay needs to **stop processing work now**:

1. On the HP, open **Windows Task Scheduler**, locate `CavemanFocusCF0Relay`, choose **Disable** to prevent new scheduled starts. If the task currently says **Running**, choose **End** to request termination of that running instance. This is a local action, not something the cloud executor can claim to have performed.
2. If a separately started `python relay/cf_public_relay.py watch` command is running in a terminal, stop that terminal process with **Ctrl+C**. Disabling Task Scheduler does not terminate an independently launched watch loop.
3. If an immediate stop is more important than preserving an in-flight result, understand that ending a process mid-action can leave an `in_progress`/uncertain request. **Do not clear the local SQLite ledger to force a retry.** The source relay conservatively treats uncertain attempts as non-retryable.
4. Use `STOP_CF0_RELAY.bat` only if you also intend to **unregister** the existing relay schedule. It calls `relay/install_task.ps1 remove`, which removes future task registration. **It is not an immediate kill switch for already-running processes.** Recreating the schedule later requires a deliberate owner-local installation.

If the separate private HP Bridge has also been enabled, its `CavemanFocusHPBridge` task is distinct. Manage its running instance and triggers separately in Task Scheduler. `STOP_HP_BRIDGE_WINDOWS.bat` unregisters that bridge task but does not operate the public CF-0 relay.

## Related controls are not substitutes for stopping the relay

| Existing file | What it actually does | What it does **not** do |
|---|---|---|
| `DISABLE_CF0_HEALTH_REPORT.bat` | Removes the local opt-in flag for publishing public-safe health data | Does not stop relay polls or remove stored receipts |
| `DISABLE_CF0_WRITEBACK.bat` | Reverts an existing scheduled task action to tokenless read-only polling and removes its local writeback token file | Does not stop polling; do not confuse with an urgent stop |
| `STOP_CF0_RELAY.bat` | Unregisters the future public relay task | Does not prove a running process ended and does not delete the SQLite ledger |
| `STOP_HP_BRIDGE_WINDOWS.bat` | Unregisters the separate HP Bridge task | Does not stop the public relay |

Revoking the previously created GitHub fine-grained token **through GitHub's account controls** can block future authorized writeback if credentials are compromised, but it does not stop tokenless public reads or running local commands. Never send that token in ChatGPT, an issue, or the public repository. No token revocation or account changes were performed as part of this documentation.

## Preservation and restart

**Preserve evidence:** keep the local `relay.sqlite3` receipts and attempts database, unresolved `in_progress` entries, pending public jobs, original scripts, existing private files, and Git history. Stopping is not a reason to wipe records. The public inbox may still contain **unexpired requests**; do not blindly resume against the queue.

**Resume only after explicit local decision:** inspect the Task Scheduler entry and pending queue; if you merely disabled `CavemanFocusCF0Relay`, enable it locally after verifying the action and intended rights. If you unregistered it, the existing `INSTALL_CF0_RELAY.bat` reinstalls the **current-user limited-rights** schedule after its offline preflight, but registration may reset the original task action and must not silently be treated as restoring writeback. If writeback or health opt-in is still desired, review the existing `ENABLE_CF0_READ_WRITE.bat` and `relay/HEALTH_ONE_CLICK.md` as separate, owner-local decisions. Do not assume the current HP checkout matches the latest cloud branch.

**Verify after resumption:** require a new, correctly correlated public-safe receipt and independent Windows scheduled-task evidence before calling a restarted task healthy. An earlier cloud CI pass or a matching public receipt alone does not prove HP scheduler origin or seven-day unattended operation.

## What the cloud operator may do

The cloud operator may inspect public `relay/health/latest.json` and existing public receipts, cite stale/unavailable/unknown statuses, preserve the task queue and continue safe source-level work. It **may not remotely disable or kill HP processes**, claim a local stop occurred, broaden the relay command allowlist, delete local databases, revoke a token, or silently reinstall tasks. Emergency stop is **owner-local and reversible** at the schedule level, with explicit caveats about in-flight commands.

**Source references:** [public relay installer](install_task.ps1) · [read/write wrapper](cf_public_relay_rw.ps1) · [recovery semantics](UNKNOWN_ATTEMPTS.md) · [health opt-in](HEALTH_ONE_CLICK.md) · [owner capability contract](../automation_200/OWNER_CAPABILITY_CONTRACT.json).