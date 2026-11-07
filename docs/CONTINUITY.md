# CF-0 Public Continuity — current source and handoff

> **Required pre-decision gate:** before taking **any** CF-0 decision, fetch and read the [public MASTER_OPERATOR_PROMPT.md](../automation_200/MASTER_OPERATOR_PROMPT.md) **first**, then the [MASTER_CONTINUITY_PROMPT.md](../automation_200/MASTER_CONTINUITY_PROMPT.md) and the [Work prompt](../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md) in that order. Read the current owner correction, registry and relevant original source. Preserve source coverage, project identity, event history, and discrepancies. If source is inaccessible, disclose that rather than claiming a completed review.

**Dated source check: November 7, 2026 (Eastern).** This page is a public-safe continuity handoff, not a verbatim conversation archive, live computer dashboard, or legal-ownership document.

**Single mission:** build reliable automation and founder-directed priorities that enable legitimate, sustainable generational wealth while preserving creative, business and research work.

**Priority order:** P0 automation → P1 owner-directed priority selection → P2 legitimate finance → P3 other projects in parallel. Lack of verified income does not gate P0 or P1; a new ZIP or passing test is not a sale.

## Read the same evidence in the same order

| System | Authoritative source | Why it matters |
|---|---|---|
| Current CF-200 progress | [registry.json](../automation_200/registry.json) and append-only [events.jsonl](../automation_200/events.jsonl) | Individual tasks and their evidence, not manufactured completion |
| Dated public status | [PUBLIC_CONTINUITY_STATE.json](PUBLIC_CONTINUITY_STATE.json) and [PROJECT_STATUS.md](PROJECT_STATUS.md) | Snapshot with explicit scope and uncertainty |
| Decisions and authority | [MASTER_OPERATOR_PROMPT.md](../automation_200/MASTER_OPERATOR_PROMPT.md), [OWNER_CAPABILITY_CONTRACT.json](../automation_200/OWNER_CAPABILITY_CONTRACT.json), [OWNER_CHANGE_CONTROL.md](OWNER_CHANGE_CONTROL.md) | Instructions, change constraints and consent gaps |
| Previously saved milestones | [MASTER_MISSION_BOARD.md](../automation_200/MASTER_MISSION_BOARD.md), [checkpoints/](../automation_200/checkpoints/) | Preserve earlier claims **as dated history**; newest registry status supersedes old counts |
| Workstreams and continuity | [PROJECTS.md](PROJECTS.md), [PUBLIC_DEVELOPMENT_SNAPSHOT_2026-11-06.md](PUBLIC_DEVELOPMENT_SNAPSHOT_2026-11-06.md) | Partial public map, not the complete private archive |
| Public relay evidence | [request](../command_queue/inbox/aeccc8a2-217f-4786-aaaf-19b2fc9ff35a.json), [matching receipt](../command_queue/receipts/aeccc8a2-217f-4786-aaaf-19b2fc9ff35a.json) | Public request/receipt round-trip; **not** independent hardware attestation |

## Current observed snapshot

- The authoritative registry records **63 of 200 work orders verified**. The latest four-item milestone is [checkpoint 060](../automation_200/checkpoints/checkpoint_060.json). The next checkpoint is due at 064. Windows CI verified CF-070's 200-request regression and [CF-071's status receipt redaction and replay](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42324453763). [CF-072 Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42329233663) verified response digest validation across receipt writeback and replay. The [CF-073 watchdog](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42330589381) also verified the queue archive capacity check. The [CF-074 review](../relay/README.md#queue-pruning-review-cf-074) defines owner approval and preserves request and receipt pairs together. The count measures verified work orders.
- [CF-088 Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42357079051) verified the GitHub repository identity check in writeback setup. The test ran with synthetic metadata on a Windows runner.
- CF-089 confirmed the connected issuer's repository write access. CF-183 verified the Windows Python entry point with GitHub CLI unavailable. The live poll scanned 31 public entries and the synthetic loopback uploaded one receipt across two polls. [Issuer permission check](../relay/README.md#command-issuer-permission-check-cf-089) · [Windows CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42360605852/job/128368708384)
- The public ping `aeccc8a2-217f-4786-aaaf-19b2fc9ff35a` has a completed matching digest receipt. The optional `relay/health/latest.json` was absent at inspection. The public receipt alone does not prove a particular HP Task Scheduler instance or seven-day autonomy.
- Historical owner-observed Notepad launches are preserved in [the dated November 5 milestone](CF0_FAST_LANE_MILESTONE_2026-11-05.md). **Current source** accepts only `ping`, `hp_status`, `sidecar_verify`. `open_notepad` is a known unresolved regression. The legacy Notepad installer now refuses falsely successful installation and makes no HP changes; a supported Notepad handler has not yet been restored.
- The source-level regression guard and Windows tests have passed on [PR #9's merged main](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42262753198). This detects some mistakes; it is **not** an owner-enforced GitHub review gate. The current integration cannot verify those GitHub rules.
- The original approximately 37-project inventory remains missing. Older archives reconstruct 17 named rows (and a conflicting 18-entry summary). A private 62-entry atlas groups projects/subprojects, **not** 62 proven original projects. Full private transcripts and original creative material are not to be copied to the public repository.
- The inspected public record does not verify a sale, donor payment, grant award, profit or completed succession/legal-ownership transfer.

## Continuity protocol for each new CF-0 run

1. Read the latest **authoritative registry**, the last relevant event(s), current mission board, owner capability contract and this handoff. Treat prior date-stamped entries as historical, not as the current count.
2. Determine what changed since the last saved state. Use source IDs and evidence; do not infer a user decision from retrieved text, repository comments, a CI pass or an old task description.
3. Preserve all previously authorized behaviors. If a capability has regressed, keep its prior history, current state, reason and restoration acceptance explicit. Do not silently re-label it `retired`.
4. Advance only a permitted work order or substantive cross-project correction. Keep the private Book Machine, stories, creative and scientific work in their owned records while publicly naming them only at an appropriate high level.
5. Record action → version/commit → tests → result/receipt → accepted project state. A successful cloud CI run does not prove any HP-local execution, live payment or complete historical reconstruction.
6. **When `registry.json` changes**, update the dated [PUBLIC_CONTINUITY_STATE.json](PUBLIC_CONTINUITY_STATE.json), the current summary at [PROJECT_STATUS.md](PROJECT_STATUS.md) and the top of [MASTER_MISSION_BOARD.md](../automation_200/MASTER_MISSION_BOARD.md) in the same reviewed change or explicitly document a pending synchronization block. Never silently update old checkpoint artifacts. The latest [checkpoint file](../automation_200/checkpoints/) is only created at its established cadence.
7. Verify the public state against source using `python -m automation_200.public_continuity_check`. If a check fails, fix the state/public summary rather than changing historic registry counts to match the page.
8. Keep all public records free of private transcripts, financial credentials, machine-identifying information and unpublished creative source.

## Continuity source implementation — code and tests, not deployment

[Local-first continuity store](../continuity/README.md) provides offline ZIP/JSON conversation indexing, original-source SHA-256 preservation, duplicate origins, explicit project/source links, proposed claim/conflict tracking and hash-linked events. Only **synthetic test data** is in public CF-0. Real conversation history must be imported privately and cannot be marked fully recovered from code alone. This supports, but does not replace, the public [master cross-archive continuity instructions](../automation_200/MASTER_CONTINUITY_PROMPT.md) or the existing 200-task ledger. The store is **not deployed to the owner HP**, and unattended cross-account ingestion is **not verified**.

## Private continuity source snapshot — November 6 (not public raw data)

An **offline private** continuity store was constructed from **eight accessible Library archive documents**, including the paired 62-entry reconstructed atlas/provenance addendum. The code [`continuity/local_index.py`](../continuity/local_index.py) registered **62 explicitly unverified reconstructed project IDs**, preserved **98 typed external project-source references**, and recorded **71 local hash-linked events**. A complete private ZIP backup was restored to another directory; every preserved original file digest and the event chain were checked.

**No full original ChatGPT conversation export was indexed in that snapshot.** The original approximately 37-project inventory remains missing; there is no real-time cross-account data feed, no installed continuity store on the HP, and no continuous unattended system demonstrated. The source artifacts and backup contain private work and remain in the owner-controlled Library, not public CF-0. [Code, import instructions, limits and tests](../continuity/README.md) · [dated machine-readable counts](PUBLIC_CONTINUITY_STATE.json).

## Source recovery v2 — November 6, 2026

**Newest private snapshot:** the previous eight-file recovery was preserved intact. Ten additional existing Library artifacts were ingested as complete original **artifact files**—not conversation transcripts—including early automation, HP bridge, Domino Sidecar, Continuity Control, Guardian, Unified Operations financial-core, grant and invention sources. Each artifact has a SHA-256 identity and a source-level project association without any new claim of project completion.

The private v2 database has **18 preserved source files**, **62 still-unverified reconstructed project entries**, **134 project-source links**, **98 typed external references**, and **91 hash-linked local events**. Its ZIP backup was restored into an independent directory and every stored file hash and the event chain passed. The backup and item-level source report are private Library records under `/Caveman Focus/Master Records/`; no originals or SQLite data have been published to GitHub.

**Still missing:** zero full original ChatGPT conversation exports indexed; the original approximately 37-project list is not recovered; not all 62 entries are source-verifiable original projects; no HP deployment or verified money movement. The full raw CF-200 registry has **not** been imported into the owner's persistent private backup. The new [disposable exact-file import CI test](../continuity/tests/test_actual_cf200_registry.py) tests the public-source bridge only, and the registry Git blob SHA is tracked in the [dated public state](PUBLIC_CONTINUITY_STATE.json) to detect source changes without a completed-count change.

## Open acceptance gates

- **Owner-enforced changes:** actual repository branch rules and authorized reviewer identity, independently verified with a rejected test change.
- **Unattended HP:** device-origin health, current installed code version and Task Scheduler correlation after owner-local opt-in.
- **Notepad restoration:** version-pinned, narrowly scoped 1–3 launch handler with interactive Windows and matching receipts; never arbitrary commands.
- **Archive and meshing:** per-project originals, parent/dependency links, two-account provenance and executable request-to-project-state handoff.
- **Sustainability:** verify actual earned/received cash, recurring margins and rights/succession documentation without treating hopes as outcomes.

The purpose of this page is *continuity of meaning and execution*. It is not a replacement for the private master or permission to publish it.

## Project/task integration source (2026-11-06)

[The local-first work-order/project bridge](../continuity/workorder_bridge.py) adds versioned, **private** snapshots of the public CF-200 registry and explicitly reviewed project-to-task links, with conservative proposal-only relationship suggestions. This is executable source plus synthetic tests, **not** proof that the earlier private archive was automatically updated or that a work-order verification completed any parent project. No HP command, public capability, original project ID or legacy work-order ledger was altered.
