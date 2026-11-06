# CF-0 — One-click HP health reporting (optional)

Owner: **Kiara Lynn Rose Smith's Caveman Focus**. This is a source-reviewed convenience control, not proof of an installed, unattended agent.

## Why this exists

The existing Windows relay already has a public-safe health snapshot module and a publisher behind an **owner-local opt-in flag**. Repeatedly asking the owner to run and paste PowerShell diagnostics is not the automation goal. This provides one-click **enable**, **status**, and **rollback** controls without a new service, new scheduled task, remote commands, credential exposure, or repeated clipboard steps.

## First-time use on the HP

Use a *current* CF-0 checkout already installed on the HP, whose `CavemanFocusCF0Relay` scheduled task runs **that same checkout** of `relay/cf_public_relay_rw.ps1`. Downloading or merging GitHub source alone does not update the owner HP. These batch files must physically exist on the machine before use.

- Double-click `ENABLE_CF0_HEALTH_REPORT.bat` once. It performs a read-only collector preflight, checks that the existing task points at this checkout, checks that the existing encrypted writeback token file is present, then writes **only** `allow_health_report.flag` in the owner's CF0Relay local state folder.
- Double-click `STATUS_CF0_HEALTH_REPORT.bat` to see whether local prerequisites and the flag are present. **Presence is not proof of a successful report or a valid token.**
- Double-click `DISABLE_CF0_HEALTH_REPORT.bat` at any time to remove the flag. This does not stop the existing relay, remove the token, change its schedule, or delete the local SQLite ledger.

The existing five-minute scheduled **read/write** wrapper sees the flag on its next successful execution and *attempts* to publish exactly the sanitized `cf0.hp_health.v1` fields at `relay/health/latest.json` on the public repository. Unchanged metrics are normally not republished more often than every 30 minutes; meaningful changes trigger a new report. No report is guaranteed to appear just because the flag was enabled.

## Public privacy and evidence

The report contains a UTC timestamp, database-present boolean, aggregate receipt counts, the last receipt's coarse status, and a restricted error category. It contains **no private command output, usernames, local paths, device identifiers, credentials, personal records, or raw receipts.** Treat a report as a self-reported operational heartbeat, not cryptographic HP attestation.

Verify a **freshly created** public `relay/health/latest.json` before claiming automatic HP reporting works. To link a particular task to a scheduled run, correlate the task request and receipt with independent scheduler evidence; a GitHub CI success or an opt-in flag alone is insufficient. Seven-day autonomy remains a separate long-duration acceptance target.

## Important failure conditions

Activation refuses to proceed if the current checkout is not the same wrapper targeted by the existing task, writeback has not been configured, the Python collector or publisher is missing, or the collector preflight fails. It does not request or inspect the actual token. A stale, invalid, or revoked token can still prevent publication. Read the brief error shown by the launcher; the rollback is independent.

**No one should place a GitHub token or HP-private details into this public repository or a chat.** The optional fine-grained token used by the existing wrapper grants write access to the whole CF-0 repository, not only the health file.
