# CF-0 — Tasks & Issues
**Public owner dashboard · Last source review: November 7, 2026 (Eastern)**

> **This is the short version.** See [the official 200-task registry](../automation_200/registry.json) for each work order, the [master mission board](../automation_200/MASTER_MISSION_BOARD.md) for technical history, and [GitHub Issues](https://github.com/whoiwts110217-creator/CF-0/issues) for discussion. This is a dated report, **not** a continuously live HP status display.

## Status at a glance

| Measure | Verified source-backed state |
|---|---|
| CF-200 work orders | **75 verified / 200 total**; 125 planned |
| Current verified progress | 37.5% of defined work orders; **not** 37.5% of the finished product |
| Open GitHub issues | **3** returned in the last issue search |
| Public task/issue refresh | **Working once** through existing enabled hourly CF-200 executor; ongoing reliability still being observed |
| Unattended HP computer | **Unverified** — local Windows scheduling and matching receipt not independently correlated |
| Donations/revenue | No new owner-confirmed receipts established by this dashboard |

**Evidence:** [registry.json](../automation_200/registry.json), source blob `cecdcea4f9dcc00e1b046f39875433aaeb7e63d6`; [public continuity](PUBLIC_CONTINUITY_STATE.json); [first executor-produced dashboard refresh commit](https://github.com/whoiwts110217-creator/CF-0/commit/479c93ae8689279cb422771a504cd3be494763aa). A successful dashboard refresh is **not** proof of unattended HP operation.

## What is being worked on next?

Owner's order remains **P0 Automation → P1 Priority/continuity → P2 Finances → P3 Other branches concurrently**. These five are *source-work candidates* with dependencies passed at the last limited public check, **not commitments, completed work, or authorizations to touch the HP**. The [decision engine](../automation_200/decision_engine.py) makes fuller proposals.

| Category | Task | Plain-language purpose | Status |
|---|---|---|---|
| **P0 — Automation** | **CF-100** | Design the second-phase private operator authorization gate | Planned; source-only candidate |
| **P1 — Priorities** | **CF-110** | Confirm blocked high-priority jobs cannot suppress useful eligible work | Planned; source-only candidate |
| **P1 — Continuity** | **CF-141** | Publish a source-backed, categorized master project index | Planned; source-only candidate |
| **P2 — Finances** | **CF-122** | Publish a *verified* financial checkpoint, only if actual evidence exists | Planned; evidence-dependent |
| **P3 — Research** | **CF-161** | Preserve the guess → hypothesis → evidence → proof rule | Planned; source-only candidate |

**Other planned tasks:** 120 are held outside this limited candidate list, typically due to dependency or local/HP evidence constraints. See [registry](../automation_200/registry.json) for their individual status. Existing work can proceed concurrently in separate branches; do not turn proposals into completions.

## Problems we know about

| Issue / category | Why it matters | Next verification step |
|---|---|---|
| **HP automatic operation · P0** | A matched public command receipt alone does not prove a Windows scheduled run | Correlate public-safe receipt with real HP Task Scheduler time/exit evidence |
| **Notepad regression · P0** | Historical owner-observed launches are not supported by the current public relay | Owner-approved local restoration; preserve relay allowlist |
| **Project archive gap · P1** | Original ~37-project inventory still unrecovered; newer reconstructed lists are not the original | Private source audit with hashes and documented uncertainties |
| **Donation website audit · P2** | Rendered layout, accessibility and actual payment link behavior not verified from available environment | Run authorized browser-level read-only audit |
| **AI challenge distribution · P2/P3** | [Public challenge](../finance/donation_growth/AI_ATTENTION_CHALLENGE_2026-11-07.md) exists, but independent agent engagement is unverified | One specifically approved, permission-compliant third-party placement and response check |

The list distinguishes **operational blockers** from actual GitHub Issues; one need not have a GitHub issue number to be important.

## Open GitHub Issues (last checked: November 7)

- [**#1 — HP bridge acceptance:** private mailbox → real Windows round trip](https://github.com/whoiwts110217-creator/CF-0/issues/1)
- [**#3 — Engineering feedback:** critique the autonomous relay and intervention design](https://github.com/whoiwts110217-creator/CF-0/issues/3)
- [**#16 — Agent collaboration:** prove one real automation improvement](https://github.com/whoiwts110217-creator/CF-0/issues/16)

[See current GitHub Issues directly](https://github.com/whoiwts110217-creator/CF-0/issues). If the Issues service cannot be read, the board must say **unknown**, never zero.

## What requires your decision?

**Nothing on this page requires immediate manual work merely to keep status reporting running.** Five optional consequential changes remain **not approved** in the [owner approval bin](../automation_200/PROMPT_CHANGE_BIN.md):

- **PCA-001 — Governance:** change master priorities/ownership/capability contract.
- **PCA-002 — Financial:** fund a cash micro-bounty (currently unfunded).
- **PCA-003 — Distribution:** authorize specific third-party agent posts or messages.
- **PCA-004 — HP access:** change the restricted computer-command allowlist.
- **PCA-005 — Cutover:** replace or retire a working scheduled operator.

No approval is implied by publication of this list. Creator/developer: **David Smith**; designated owner and intended beneficiary: **Kiara Lynn Rose Smith**. No legal transfer is claimed.

## How regular updates work

The **existing enabled hourly CF-200 Four-Task Executor** (automation ID `6aeca952e1608191a102030939b4205b`) includes an owner-requested instruction to refresh this page after ordinary work when it is **six hours old** or when verified tasks, open issues or owner approval state materially changes. It preserves the original schedule; no extra automation was created.

**First actual result:** the task service recorded a completed executor run and a public [dashboard update commit](https://github.com/whoiwts110217-creator/CF-0/commit/479c93ae8689279cb422771a504cd3be494763aa) on November 7. This verifies one successful automatic updater **run**, not future reliability.

Every later update should revise the summary **in place** and preserve prior history in [Git commits](https://github.com/whoiwts110217-creator/CF-0/commits/main/docs/TASKS_AND_ISSUES.md), rather than stacking contradictory older status notes at the bottom. Re-read the current registry, issue list, approval bin and public continuity before a SHA-guarded write. If a check or write fails, keep the previous dashboard and clearly report stale/unknown state. Never fabricate progress or account activity.

**Other links:** [Project index](PROJECTS.md) · [Start Here](START_HERE.md) · [Operator prompt](../automation_200/MASTER_OPERATOR_PROMPT.md) · [Work prompt](../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md).
