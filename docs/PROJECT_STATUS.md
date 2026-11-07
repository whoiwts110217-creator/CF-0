# Caveman Focus — Current public status

**Source-verified snapshot: November 6, 2026 (Eastern).** This is a dated source/document check, **not** a live HP heartbeat. For stable handoffs, use the [public continuity record](CONTINUITY.md) and [machine-readable status](PUBLIC_CONTINUITY_STATE.json).

**Verified CF-200 work orders: 55/200.** The [authoritative registry](../automation_200/registry.json) records 55 verified source/operation work orders. The latest numbered checkpoint remains [052](../automation_200/checkpoints/checkpoint_052.json), with the next numbered checkpoint due at 056. The [CF-070 Windows regression](../relay/tests/test_queue_capacity_200.py) validated 200 offline queue requests. [CF-071 Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42324453763) verified the serialized public-safe status receipt and its replay; these counts are not a product-readiness percentage, HP uptime or customer income.

**Current Notepad behavior:** historical owner-observed launches and matching receipts are documented in the [November 5 milestone](CF0_FAST_LANE_MILESTONE_2026-11-05.md), but the **current public relay source does not support** `open_notepad`. It only allows `ping`, `hp_status`, and `sidecar_verify`. The earlier installer is now a **read-only refusal**, not an installation success; Notepad restoration remains a documented open regression. Do not claim the old Windows installation has been overwritten or verified.

**Verified public ping:** request `aeccc8a2-217f-4786-aaaf-19b2fc9ff35a` has a matching [public receipt](../command_queue/receipts/aeccc8a2-217f-4786-aaaf-19b2fc9ff35a.json) and digest. This does **not** independently attest which physical HP process produced the receipt or prove its scheduled behavior. The optional health report was not published at the last check.

**Source regression prevention:** [PR #9](https://github.com/whoiwts110217-creator/CF-0/pull/9) passed [merged-main Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42262753198); it detects several silent capability changes. **Mandatory owner review and GitHub rules are still unverified**; a CI pass is not owner consent. See [change controls](OWNER_CHANGE_CONTROL.md).

**Caveman Focus continuity:** P0 automation → P1 owner-directed priority intelligence → P2 legitimate income → P3 other projects in parallel, toward sustainable generational wealth. Original ~37-project list remains unrecovered. The private 62-entry reconstructed atlas is a mixed workstream index and is not the lost original list. No live payment, seven-day unattended HP operation or general-purpose remote control is verified by this snapshot.

## Earlier checkpoint — retained as historical observations, not the current status

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
