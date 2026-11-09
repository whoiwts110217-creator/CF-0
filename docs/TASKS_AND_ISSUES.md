# CF-0 — Tasks & Issues
**Public owner dashboard · Source review November 9, 2026 (Eastern)**

This dated report summarizes work orders, blockers, and GitHub issues. [Mission Control](https://whoiwts110217-creator.github.io/CF-0/mission-control/) shows the GitHub commit it read or the commit of its bundled fallback. Use the [official registry](../automation_200/registry.json) for task records and the [mission board](../automation_200/MASTER_MISSION_BOARD.md) for technical history.

## Status at a glance

| Measure | Verified source-backed state |
|---|---|
| CF-200 work orders | **85 verified / 200 total**; 115 planned |
| Current verified progress | 42.5% of defined work orders; **not** 42.5% of the finished product |
| Open GitHub issues | **4** confirmed in the November 9 issue search ([#1](https://github.com/whoiwts110217-creator/CF-0/issues/1), [#3](https://github.com/whoiwts110217-creator/CF-0/issues/3), [#16](https://github.com/whoiwts110217-creator/CF-0/issues/16), [#21](https://github.com/whoiwts110217-creator/CF-0/issues/21)) |
| Public task/issue refresh | Existing CF-200 executor ran on demand November 9; [mission-board record](../automation_200/MASTER_MISSION_BOARD.md) and this dated refresh. |
| Public HP health | [Latest public health report](../relay/health/latest.json) publishes its own collection time and receipt counts. Direct Windows scheduler attribution is tracked separately. |
| Windows scheduled relay | **Observed.** Windows logged a scheduled run from **1:06:53 to 1:08:58 p.m.** on November 8. The matched public pong was committed at **1:07:21 p.m.** Direct ping-to-run attribution is open. [HP evidence](CONTINUITY.md#november-8-hp-relay-evidence) |
| Seven-day unattended operation | Verification remains open. |
| Donations/revenue | No new owner-confirmed receipts established by this dashboard |

**Evidence:** [registry.json](../automation_200/registry.json), source blob `3124e881d709de58e1150e9f612b15731b7169c6`; [public continuity](PUBLIC_CONTINUITY_STATE.json); [first executor-produced dashboard refresh commit](https://github.com/whoiwts110217-creator/CF-0/commit/479c93ae8689279cb422771a504cd3be494763aa). A successful dashboard refresh is **not** proof of unattended HP operation.

**CF-118 source integration passed.** The existing executor ran on demand on November 9 and added a [read-only adapter](../automation_200/attempt_history_cf118.py) from the existing retry journal to the decision engine. [Linux](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42564024841/job/128986476285) and [Windows](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42564024841/job/128986476096) passed the offline journal and retry-boundary tests. The [Windows integration job](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42576948195/job/129026687680) passed on the journal-adapter revision. The registry credits CF-118 at source level. Scheduled acceptance still requires a real run that carries attempt history forward and enforces the retry ceiling.

## What is being worked on next?

Owner's order remains **P0 Automation → P1 Priority/continuity → P2 Finances → P3 Other branches concurrently**. These are publicly dependency-gated *candidates*, not commitments, completed work, or HP authorization. Additional owner holds are enforced by the [decision engine](../automation_200/decision_engine.py).

| Category | Task | Plain-language purpose | Status |
|---|---|---|---|
| **P1 — Priorities** | **CF-119** | Add source-level HP authority proof gate; retain owner-local device restriction | Planned; CF-118 source prerequisite verified; no HP execution authorization |
| **P1 — Priorities** | **CF-141** | Publish the source-backed master project index | Planned; source-only candidate |
| **P2 — Finances** | **CF-122** | Publish a verified financial checkpoint only if evidence exists | Planned; evidence-dependent |
| **P3 — Research** | **CF-161** | Preserve guess → hypothesis → evidence → proof | Planned; source-only candidate |

**P0 evidence gate:** [draft PR #17](https://github.com/whoiwts110217-creator/CF-0/pull/17) remains subject to its [no-merge integration gate](https://github.com/whoiwts110217-creator/CF-0/blob/experiment/parallel-coordination-v1/experiments/parallel_coordination/INTEGRATION_GATE.md). The [HP continuity record](CONTINUITY.md#november-8-hp-relay-evidence) separately records the matched ping and overlapping scheduler window.

**Other planned tasks:** **111** other work orders remain planned; many need dependencies or HP-local evidence. See the [registry](../automation_200/registry.json) for each acceptance condition. CF-100 and CF-110 are already verified and must not appear as planned candidates.

## Problems we know about

| Issue / category | Why it matters | Next verification step |
|---|---|---|
| **Relay evidence adapter CI · P0** | [Draft PR #17](https://github.com/whoiwts110217-creator/CF-0/pull/17) contains isolated relay evidence tests, a deeply nested JSON regression, and an explicit no-merge integration gate, but the full branch test suite and cloud CI remain unconfirmed; do not merge or call these passing | Obtain a real full-suite test result and review against current main |
| **HP receipt attribution · P0** | [A scheduled relay run overlaps a matched public receipt](CONTINUITY.md#november-8-hp-relay-evidence) | Correlate the request ID and outcome with the specific Windows invocation |
| **Notepad regression · P0** | Historical owner-observed launches are not supported by the current public relay | Owner-approved local restoration; preserve relay allowlist |
| **Project archive gap · P1** | Original ~37-project inventory still unrecovered; newer reconstructed lists are not the original | Private source audit with hashes and documented uncertainties |
| **Donation website audit · P2** | Rendered layout, accessibility and actual payment link behavior not verified from available environment | Run authorized browser-level read-only audit |
| **AI challenge distribution · P2/P3** | [Public challenge](../finance/donation_growth/AI_ATTENTION_CHALLENGE_2026-11-07.md) exists, but independent agent engagement is unverified | One specifically approved, permission-compliant third-party placement and response check |

The list distinguishes **operational blockers** from actual GitHub Issues; one need not have a GitHub issue number to be important.

## Open GitHub Issues (checked November 9, Eastern)

- [**#1 — HP bridge acceptance:** private mailbox → real Windows round trip](https://github.com/whoiwts110217-creator/CF-0/issues/1)
- [**#3 — Engineering feedback:** critique the autonomous relay and intervention design](https://github.com/whoiwts110217-creator/CF-0/issues/3)
- [**#16 — Agent collaboration:** prove one real automation improvement](https://github.com/whoiwts110217-creator/CF-0/issues/16)
- [**#21 — Clarity exercise and public feedback**](https://github.com/whoiwts110217-creator/CF-0/issues/21)

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
- **Read-only CI:** [dashboard-guard.yml](../.github/workflows/dashboard-guard.yml) runs [the offline dashboard tests](../automation_200/tests/test_dashboard_guard.py) and compares the dashboard with its registry snapshot when related sources change. [The November 9 Linux job](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42564024841/job/128986476285) passed both checks.
- **Repair rule:** when a registry edit creates drift, refresh the dashboard from authoritative source with a GitHub SHA guard; do not change task statuses merely to make the checker pass. If issues cannot be retrieved, show **unknown**, not zero.

## How regular updates work

The **existing enabled hourly CF-200 Four-Task Executor** (automation ID `6aeca952e1608191a102030939b4205b`) includes an owner-requested instruction to refresh this page after ordinary work when it is **six hours old** or when verified tasks, open issues or owner approval state materially changes. It preserves the original schedule; no extra automation was created.

**First actual result:** the task service recorded a completed executor run and a public [dashboard update commit](https://github.com/whoiwts110217-creator/CF-0/commit/479c93ae8689279cb422771a504cd3be494763aa) on November 7. This verifies one successful automatic updater **run**, not future reliability.

Every later update should revise the summary **in place** and preserve prior history in [Git commits](https://github.com/whoiwts110217-creator/CF-0/commits/main/docs/TASKS_AND_ISSUES.md), rather than stacking contradictory older status notes at the bottom. Re-read the current registry, issue list, approval bin and public continuity before a SHA-guarded write. If a check or write fails, keep the previous dashboard and clearly report stale/unknown state. Never fabricate progress or account activity.

**Other links:** [Project index](PROJECTS.md) · [Start Here](START_HERE.md) · [Operator prompt](../automation_200/MASTER_OPERATOR_PROMPT.md) · [Work prompt](../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md).


## November 9 source acceptance follow-up (current authoritative state)

CF-118 is **source verified**, not hardware deployed. The [current registry](../automation_200/registry.json) is **85/200**, 115 planned, source blob `3124e881d709de58e1150e9f612b15731b7169c6`. [Integration Windows run 42576948195](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42576948195) passed; the three new retry-journal adapter tests ran and passed in the job log. Checkpoint 084 remains last; next 088. Earlier failures and planned states remain in the [dashboard history](https://github.com/whoiwts110217-creator/CF-0/commits/main/docs/TASKS_AND_ISSUES.md). HP scheduled-run provenance, private archive recovery and revenue verification remain open. The next eligible source task is CF-119 (HP authority proof gate), which cannot grant real HP access from public metadata.
