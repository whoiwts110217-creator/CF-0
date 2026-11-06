# Caveman Focus — Current public status

**Evidence checkpoint: November 6, 2026.** This is a dated, manually curated status record, **not** an automatically refreshed HP heartbeat. A later GitHub commit does not prove a later HP execution.

## Confirmed observations

- The owner observed allowlisted Notepad launches via the GitHub-to-HP pathway, with public-safe receipts. See [the original milestone](CF0_FAST_LANE_MILESTONE_2026-11-05.md).
- Owner-provided Windows Task Scheduler Operational events 107, 100, 200, 201 and 102 showed time-triggered starts and successful wrapper exits for `CavemanFocusCF0Relay` at approximately 01:11 and 01:16 ET on November 6.
- Owner's read-only SQLite inspection found 28 saved relay receipts; ten recent `open_notepad` receipts correspond to the owner's earlier ten-launch request. A matching public ping receipt was also observed. The receipts are **not independently correlated** to a particular scheduled invocation.
- Owner disabled the separate `CavemanFocusSupervisor` research scheduler and kept the GitHub relay scheduled. Do not silently reactivate the research scheduler.
- The authoritative [CF-200 registry](../automation_200/registry.json) recorded **52/200 verified work orders** at this checkpoint. This is a work-order count, **not** a percentage of product readiness.

## In development, not deployed

- **Highest priority:** remove manual PowerShell copy/paste by collecting and publishing a sanitized HP health snapshot automatically.
- [Read-only snapshot source](../relay/cf_hp_health_snapshot.py) is committed, but **not verified deployed, scheduled or publishing**.
- Priority selection, autonomous work execution, recovery and public reporting remain under development.

## Not established

- Seven consecutive days of useful unattended HP operation.
- General-purpose or unrestricted remote desktop control.
- Verified end-user installation from a fresh machine.
- Automatically refreshed HP status or direct automatic posting into this ChatGPT conversation.
- Verified sales, donations or profit; scientific proof or original discovery.

## Where the evidence lives

- [HP Fast Lane milestone](CF0_FAST_LANE_MILESTONE_2026-11-05.md) — original demonstration, scope and limitations.
- [Mission board](../automation_200/MASTER_MISSION_BOARD.md) — append-only narrative checkpoints and later developments.
- [Registry](../automation_200/registry.json) — authoritative work-order statuses.
- [Operating ledger](OPERATIONS.md) — earlier evidence and acceptance gates.
- [Public development snapshot](PUBLIC_DEVELOPMENT_SNAPSHOT_2026-11-06.md) — full source and project index.

**Integrity rule:** historical files retain their original dates and scope. Update this status when new evidence is actually checked; never convert a proposed feature or a passing CI test into a claimed physical HP deployment.
