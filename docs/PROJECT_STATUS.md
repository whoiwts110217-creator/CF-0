# Caveman Focus — Current public status

**Source-verified snapshot: November 7, 2026 (Eastern).** This is a dated source/document check, **not** a live HP heartbeat. For stable handoffs, use the [public continuity record](CONTINUITY.md) and [machine-readable status](PUBLIC_CONTINUITY_STATE.json).

**Verified CF-200 work orders: 71/200.** The [authoritative registry](../automation_200/registry.json) records 71 verified source/operation work orders. CF-091 now verifies that transport errors are reduced to sanitized reason codes without printing test credentials in chained tracebacks ([source](../relay/cf_public_relay.py), [Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42384041000)). This is source-level verification, not HP installation. CF-109 now verifies deterministic owner-priority task selection across source order changes without bypassing blocked/HP dependencies ([priority tests](../automation_200/tests/test_priority_selector.py), [passing Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42384405219)). It is a read-only source capability, not unattended execution. CF-093 verified that existing public action results, receipts, CLI status and the health summary exclude synthetic Windows user and device identifiers, and reject injected identity fields before publication ([tests](../relay/tests/test_identity_privacy_cf093.py), [passing Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42386254592)). Scope is source-level public surfaces, not physical-device attestation. CF-092 now guards new public receipt schemas against private paths, free-form strings, and unknown fields before storage or publication ([tests](../relay/tests/test_receipt_privacy_cf092.py), [Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42385663462)). Historical v1 receipts remain readable. This is source-only; the HP scheduled report is still unverified. CF-094 now prevents arbitrary repository/API/HTTP-path overrides in the owner-scoped GitHub relay; [Windows CI 42398244953](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42398244953) passed, including offline localhost transport and path-injection tests. Source-level security evidence only, not an HP-local deployment. CF-095 verified that HTTP responses are read with a 1,000,001-byte cap and rejected when they exceed one million bytes, including oversized JSON with synthetic sensitive data ([tests](../relay/tests/test_http_response_limit_cf095.py), [Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42398570265)). This is a source-level network safety check, not HP operations. The latest numbered checkpoint is [068](../automation_200/checkpoints/checkpoint_068.json), with the next numbered checkpoint due at 072. The [CF-070 Windows regression](../relay/tests/test_queue_capacity_200.py) validated 200 offline queue requests. [CF-071 Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42324453763) verified the serialized public-safe status receipt and its replay. [CF-072 Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42329233663) verified response digest validation and legacy receipt compatibility. The [CF-073 watchdog](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42330589381) checks archive capacity before reading queue contents. [CF-074](../relay/README.md#queue-pruning-review-cf-074) generates a read-only manifest for an owner to review before any queue relocation.

[CF-088 Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42357079051) verified that writeback setup checks the canonical GitHub name, repository ID, and default branch before it can upload a test receipt.

CF-089 verified the connected issuer's GitHub write permission. CF-183 verified the Python transport on Windows with GitHub CLI unavailable, including a live read-only poll and synthetic receipt replay. [Issuer permission check](../relay/README.md#command-issuer-permission-check-cf-089) · [Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42360605852/job/128368708384)

CF-090 verified the exact command expiry and clock-skew boundaries, the one-day lifetime limit, and timestamp validation for all three public actions. [Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42361732710/job/128371362462)

CF-108 verified that Git checkpoint commits contain only the registry, event log, and numbered snapshot. A repeat leaves the saved commit in place. [Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42362253930/job/128372899805)

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
