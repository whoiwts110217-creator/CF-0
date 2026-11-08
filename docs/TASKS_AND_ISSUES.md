# CF-0 — Tasks & Issues
**Public owner dashboard · Last source review: November 8, 2026, 8:58 a.m. Eastern**

> **This is the short version.** See [the official 200-task registry](../automation_200/registry.json) for each work order, the [master mission board](../automation_200/MASTER_MISSION_BOARD.md) for technical history, and [GitHub Issues](https://github.com/whoiwts110217-creator/CF-0/issues) for discussion. This is a dated report, **not** a continuously live HP status display.

## Status at a glance

| Measure | Verified source-backed state |
|---|---|
| CF-200 work orders | **84 verified / 200 total**; 116 planned |
| Current verified progress | 42% of defined work orders; **not** 42% of the finished product |
| Open GitHub issues | **3** returned in the November 8, 8:58 a.m. Eastern issue search |
| Public task/issue refresh | **Working once** through existing enabled hourly CF-200 executor; ongoing reliability still being observed |
| Unattended HP computer | **Unverified** — local Windows scheduling and matching receipt not independently correlated |
| Donations/revenue | No new owner-confirmed receipts established by this dashboard |

**Evidence:** [registry.json](../automation_200/registry.json), source blob `304ed3c72df0fb82b6a0eacf6f4dc2e971262c74`; [public continuity](PUBLIC_CONTINUITY_STATE.json); [first executor-produced dashboard refresh commit](https://github.com/whoiwts110217-creator/CF-0/commit/479c93ae8689279cb422771a504cd3be494763aa). A successful dashboard refresh is **not** proof of unattended HP operation.

## What is being worked on next?

Owner's order remains **P0 Automation → P1 Priority/continuity → P2 Finances → P3 Other branches concurrently**. These are publicly dependency-gated *candidates*, not commitments, completed work, or HP authorization. Additional owner holds are enforced by the [decision engine](../automation_200/decision_engine.py).

| Category | Task | Plain-language purpose | Status |
|---|---|---|---|
| **P1 — Priorities** | **CF-118** | Add failure retries with a ceiling (per authoritative registry); validate existing retry/cooldown logic before acceptance | Planned; source-only candidate; CF-117 dependency verified |
| **P1 — Priorities** | **CF-141** | Publish the source-backed master project index | Planned; source-only candidate |
| **P2 — Finances** | **CF-122** | Publish a verified financial checkpoint only if evidence exists | Planned; evidence-dependent |
| **P3 — Research** | **CF-161** | Preserve guess → hypothesis → evidence → proof | Planned; source-only candidate |

**Latest P0 review:** [draft PR #17](https://github.com/whoiwts110217-creator/CF-0/pull/17) is **DO NOT MERGE / DO NOT DEPLOY**. Its [integration evidence gate](https://github.com/whoiwts110217-creator/CF-0/blob/experiment/parallel-coordination-v1/experiments/parallel_coordination/INTEGRATION_GATE.md) requires branch-tip tests, current-main reconciliation, owner-governed review and independent HP provenance. A review query returned zero submitted reviews; commit-status query returned zero statuses (neither proves CI success nor failure). Latest compare reported 52 commits ahead / 169 behind. The public [HP health snapshot](https://github.com/whoiwts110217-creator/CF-0/blob/main/relay/health/latest.json) returned **404**, meaning unavailable, not proof that the HP is offline.

**November 8, 8:58 a.m. source review:** CF-118 remains planned at 84/200. Latest source includes retry boundary tests at `automation_200/tests/test_retry_boundary_cf118.py` (blob `eb1913011c613c16d734d633942f9232257ec90a`), but no passing execution evidence was established in this review. GitHub issue #16 still has two comments, the latest from the repository owner; no new contributor reply. The public HP health snapshot remains unavailable (404), and independently correlated Windows scheduled-run evidence is still missing. No relay commands were sent. Five owner approval proposals remain pending.

**Latest P0 source:** [canonical JSON test commit](https://github.com/whoiwts110217-creator/CF-0/commit/82c6baf88c31ad55eb087fd09a5dec5e64126809); no new verified work order, HP execution proof or CI pass claimed. The fixed [Work self-reference](../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md) was re-read from public main at blob `5da1a390f31ee8f57e5829ef368062f9215c28ac`.

**Other planned tasks:** **112** other work orders remain planned; many need dependencies or HP-local evidence. See the [registry](../automation_200/registry.json) for each acceptance condition. CF-100 and CF-110 are already verified and must not appear as planned candidates.

## Problems we know about

| Issue / category | Why it matters | Next verification step |
|---|---|---|
| **Relay evidence adapter CI · P0** | [Draft PR #17](https://github.com/whoiwts110217-creator/CF-0/pull/17) contains isolated relay evidence tests, a deeply nested JSON regression, and an explicit no-merge integration gate, but the full branch test suite and cloud CI remain unconfirmed; do not merge or call these passing | Obtain a real full-suite test result and review against current main |
| **HP automatic operation · P0** | A matched public command receipt alone does not prove a Windows scheduled run | Correlate public-safe receipt with real HP Task Scheduler time/exit evidence |
| **Notepad regression · P0** | Historical owner-observed launches are not supported by the current public relay | Owner-approved local restoration; preserve relay allowlist |
| **Project archive gap · P1** | Original ~37-project inventory still unrecovered; newer reconstructed lists are not the original | Private source audit with hashes and documented uncertainties |
| **Donation website audit · P2** | Rendered layout, accessibility and actual payment link behavior not verified from available environment | Run authorized browser-level read-only audit |
| **AI challenge distribution · P2/P3** | [Public challenge](../finance/donation_growth/AI_ATTENTION_CHALLENGE_2026-11-07.md) exists, but independent agent engagement is unverified | One specifically approved, permission-compliant third-party placement and response check |

The list distinguishes **operational blockers** from actual GitHub Issues; one need not have a GitHub issue number to be important.

## Open GitHub Issues (last checked: November 8, 8:58 a.m. Eastern)

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

## Automatic consistency safeguards

- **Read-only source check:** [dashboard_guard.py](../automation_200/dashboard_guard.py) compares the displayed work-order counts and task candidates against the exact local [registry](../automation_200/registry.json) and its Git content identity; it also checks that the displayed issue count matches distinct linked issue numbers. It **cannot** independently confirm which GitHub issues remain open, HP status or revenue.
- **Eight focused unit tests in source:** [test_dashboard_guard.py](../automation_200/tests/test_dashboard_guard.py) now includes the original six tests (previously reported **6/6 passed locally**) plus two new regressions against incorrect or missing P0–P3 category labels. **A new cloud CI pass for all eight is not yet confirmed.** The guard uses [the canonical priority-tier mapping](../automation_200/priority_selector.py) rather than an independently invented ordering.
- **Read-only CI:** [dashboard-guard.yml](../.github/workflows/dashboard-guard.yml) runs the offline tests and verifies the dashboard against its registry snapshot when the dashboard, checker, registry, or workflow itself changes (push/PR; no added scheduler or write permission). [Run #1 failed](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42409749216) when the dashboard was stale; [run #2 passed](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42409867689) after correction. The newer registry-change/workflow-self-check triggers are committed but their own cloud run is not yet independently verified. **A registry-only change may produce a transient red dashboard check until the existing hourly publisher updates the owner page**; do not treat that as failure of the CF-200 work order itself.
- **Repair rule:** when a registry edit creates drift, refresh the dashboard from authoritative source with a GitHub SHA guard; do not change task statuses merely to make the checker pass. If issues cannot be retrieved, show **unknown**, not zero.

## How regular updates work

The **existing enabled hourly CF-200 Four-Task Executor** (automation ID `6aeca952e1608191a102030939b4205b`) includes an owner-requested instruction to refresh this page after ordinary work when it is **six hours old** or when verified tasks, open issues or owner approval state materially changes. It preserves the original schedule; no extra automation was created.

**First actual result:** the task service recorded a completed executor run and a public [dashboard update commit](https://github.com/whoiwts110217-creator/CF-0/commit/479c93ae8689279cb422771a504cd3be494763aa) on November 7. This verifies one successful automatic updater **run**, not future reliability.

Every later update should revise the summary **in place** and preserve prior history in [Git commits](https://github.com/whoiwts110217-creator/CF-0/commits/main/docs/TASKS_AND_ISSUES.md), rather than stacking contradictory older status notes at the bottom. Re-read the current registry, issue list, approval bin and public continuity before a SHA-guarded write. If a check or write fails, keep the previous dashboard and clearly report stale/unknown state. Never fabricate progress or account activity.

**Other links:** [Project index](PROJECTS.md) · [Start Here](START_HERE.md) · [Operator prompt](../automation_200/MASTER_OPERATOR_PROMPT.md) · [Work prompt](../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md).
