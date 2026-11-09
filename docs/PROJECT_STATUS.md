# Caveman Focus — Current public status

**Source-verified snapshot · November 9, 2026 (Eastern).** This is a dated source/document check, **not** a live HP heartbeat. For stable handoffs, use the [public continuity record](CONTINUITY.md) and [machine-readable status](PUBLIC_CONTINUITY_STATE.json).

**Verified CF-200 work orders: 85/200.** The [authoritative registry](../automation_200/registry.json) records 85 verified source/operation work orders. CF-091 now verifies that transport errors are reduced to sanitized reason codes without printing test credentials in chained tracebacks ([source](../relay/cf_public_relay.py), [Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42384041000)). This is source-level verification, not HP installation. CF-109 now verifies deterministic owner-priority task selection across source order changes without bypassing blocked/HP dependencies ([priority tests](../automation_200/tests/test_priority_selector.py), [passing Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42384405219)). It is a read-only source capability, not unattended execution. CF-093 verified that existing public action results, receipts, CLI status and the health summary exclude synthetic Windows user and device identifiers, and reject injected identity fields before publication ([tests](../relay/tests/test_identity_privacy_cf093.py), [passing Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42386254592)). Scope is source-level public surfaces, not physical-device attestation. CF-092 now guards new public receipt schemas against private paths, free-form strings, and unknown fields before storage or publication ([tests](../relay/tests/test_receipt_privacy_cf092.py), [Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42385663462)). Historical v1 receipts remain readable. This check covers the receipt schema. The current HP evidence appears below. CF-094 now prevents arbitrary repository/API/HTTP-path overrides in the owner-scoped GitHub relay; [Windows CI 42398244953](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42398244953) passed, including offline localhost transport and path-injection tests. Source-level security evidence only, not an HP-local deployment. CF-095 verified that HTTP responses are read with a 1,000,001-byte cap and rejected when they exceed one million bytes, including oversized JSON with synthetic sensitive data ([tests](../relay/tests/test_http_response_limit_cf095.py), [Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42398570265)). This is a source-level network safety check, not HP operations. CF-096 verifies finite 20-second HTTP socket timeout and non-retrying timeout error handling ([source](../relay/cf_public_relay.py), [Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42398859873)); it does not establish a whole-poll duration or physical HP operation. CF-097 verifies the existing four-actions/eighty-scans per-poll limits, cursor continuation and uncertain-attempt nonretry via [CI 42403779158](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42403779158). Source-only, not HP execution. CF-098 source checks verify current-user limited-rights Windows task installation and prevent elevated-user changes in associated scripts ([guard](../relay/local_user_rights_guard.py), [CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42406941458)). No claim of actual HP task rights inspection. CF-099 now documents the owner-local emergency-stop procedure, accurate script effects and evidence-preserving restart ([guide](../relay/URGENT_STOP_AND_RESUME.md), [passing CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42407315346)). No actual HP action performed. The latest numbered checkpoint is [084](../automation_200/checkpoints/checkpoint_084.json), with the next numbered checkpoint due at 088. The [CF-070 Windows regression](../relay/tests/test_queue_capacity_200.py) validated 200 offline queue requests. [CF-071 Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42324453763) verified the serialized public-safe status receipt and its replay. [CF-072 Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42329233663) verified response digest validation and legacy receipt compatibility. The [CF-073 watchdog](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42330589381) checks archive capacity before reading queue contents. [CF-074](../relay/README.md#queue-pruning-review-cf-074) generates a read-only manifest for an owner to review before any queue relocation.

[CF-088 Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42357079051) verified that writeback setup checks the canonical GitHub name, repository ID, and default branch before it can upload a test receipt.

CF-089 verified the connected issuer's GitHub write permission. CF-183 verified the Python transport on Windows with GitHub CLI unavailable, including a live read-only poll and synthetic receipt replay. [Issuer permission check](../relay/README.md#command-issuer-permission-check-cf-089) · [Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42360605852/job/128368708384)

CF-090 verified the exact command expiry and clock-skew boundaries, the one-day lifetime limit, and timestamp validation for all three public actions. [Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42361732710/job/128371362462)

CF-108 verified that Git checkpoint commits contain only the registry, event log, and numbered snapshot. A repeat leaves the saved commit in place. [Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42362253930/job/128372899805)

**Current Notepad behavior:** historical owner-observed launches and matching receipts are documented in the [November 5 milestone](CF0_FAST_LANE_MILESTONE_2026-11-05.md), but the **current public relay source does not support** `open_notepad`. It only allows `ping`, `hp_status`, and `sidecar_verify`. The earlier installer is now a **read-only refusal**, not an installation success; Notepad restoration remains a documented open regression. Do not claim the old Windows installation has been overwritten or verified.

**HP relay.** The [public health report](../relay/health/latest.json) is publishing. Windows logged a scheduled run from **1:06:53 to 1:08:58 p.m.** on November 8. The matched public pong was committed at **1:07:21 p.m.** Direct ping-to-run attribution is open. [HP evidence](CONTINUITY.md#november-8-hp-relay-evidence)

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

## In development at the November 6 checkpoint

- **Highest priority:** remove manual PowerShell copy/paste by collecting and publishing a sanitized HP health snapshot automatically.
- [Read-only snapshot source](../relay/cf_hp_health_snapshot.py) is committed, but **not verified deployed, scheduled or publishing**.
- Priority selection, autonomous work execution, recovery and public reporting remain under development.

## Open at the November 6 checkpoint

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
- [Public project index](PROJECTS.md) — current workstreams and filed concepts.
- [Public development snapshot](PUBLIC_DEVELOPMENT_SNAPSHOT_2026-11-06.md) — historical publication snapshot.

**Integrity rule:** historical files retain their original dates and scope. Update this status when new evidence is actually checked; never convert a proposed feature or a passing CI test into a claimed physical HP deployment.

## November 7 — publicly filed game concept

[**Dreamkiller / BreachDungeon**](../concepts/dreamkiller/MASTER_CONCEPT_AND_CONTINUITY_PROMPT.md) (CF-CONCEPT-DREAMKILLER-001) is now a **public design artifact**, created by **David Smith** with **Kiara Lynn Rose Smith** designated owner/intended beneficiary. It extends but does not overwrite the historical Breach Dungeon APK CR-10. No game installation, real Game Boy ROM, tested glitch, revenue or CF-200 task verification is claimed by this addition. [Cross-archive reconciliation](CONTINUITY_RECONCILIATION_2026-11-07_DREAMKILLER.md).


**CF-114 verified (November 7):** [Read-only owner policy diff](../automation_200/policy_diff.py) and [negative tests](../automation_200/tests/test_policy_diff_cf114.py) compare priorities, stream tiers, and capability status without granting approval or modifying policy. [Windows CI 42413436610](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42413436610) passed. Source-level evidence, not owner consent or HP operation.


**CF-115 verified (November 7):** [Owner-instruction conflict detector](../automation_200/owner_instruction_conflicts.py) refuses contradictory structured block/prioritize proposals without owner resolution; unverified instructions are rejected, not treated as authorization. [Full Windows CI 42413696329](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42413696329) passed. Source-only, not a real-world authentication claim.


**CF-116 source verification (November 7):** [Task context expiry](../automation_200/task_context_expiry.py) holds tasks whose optional reviewed metadata is expired or future-issued; [CI 42414009722](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42414009722) passed. No current HP deployment or owner authorization was inferred.


**CF-117 verified (November 7):** [Read-only next-unblocking task selection](../automation_200/next_unblocking_task.py) identifies a dependency-safe source task or explicitly reports that only blocked/HP-local steps remain. [Full Windows CI 42414383595](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42414383595) passed after fixing a concurrent continuity test handle issue. Not a live HP execution claim.


**CF-118 verified (November 9):** Existing local retry-evidence journal is now connected to read-only task proposals via [adapter](../automation_200/attempt_history_cf118.py). Source https://github.com/whoiwts110217-creator/CF-0/commit/d207d68b4eb70dc2c719d2b960cd71e4a4fe2ca1; [integration tests](https://github.com/whoiwts110217-creator/CF-0/commit/a50d7f76e01fedc25858f3177ea9da38f20209bd); [full Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42576948195) passed with three new adapter tests. A third recorded failure holds the proposal even after cooldown; malformed, tampered and future-dated records are rejected. **This is source verification only:** no autonomous machine retry, authenticated HP execution, or financial result. Registry now **85/200**, checkpoint 084 unchanged; next checkpoint 088.
