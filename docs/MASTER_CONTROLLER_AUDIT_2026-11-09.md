# CF-0 Master Controller — critical audit and narrowed recovery scope (2026-11-09)

**Evidence class:** public source inspected + private ChatGPT automation inventory queried within the authorized account for the owner-facing audit. No Windows desktop inspection or signed-in chat sweep has been performed. A green repository CI result does **not** prove a real account or HP worker was controlled.

## Plain-language conclusion

Mission Control is currently a **read-only information dashboard with a local shutdown planner**, not a working universal automation controller. Displayed buttons for Start/Pause/Resume/Emergency Stop and the master switch have no authenticated execution adapters and are intentionally disabled. This avoids false success claims, but does not yet fulfill the owner's one-panel stop/start objective.

## Coverage reconciliation

| Surface | Source-verified known count | What the page can actually know | Unresolved gap |
|---|---:|---|---|
| ChatGPT scheduled automations | 10 last observed in owner's account | Ten placeholders or owner-loaded private names/status snapshot; no live task action | The static site cannot read current enabled state, latest run, or pause via account APIs |
| GitHub Actions workflows | **19 total**, of which **5 cron-scheduled** and 14 push/PR/manual-triggered | Public source names and trigger classes; the audit fix adds all 19 | Source presence is not a live workflow enablement check; workflow run status needs separate authenticated/run readback |
| Owner-local Windows CF-0 tasks | 3 documented by name: Fast Lane, Relay, optional HP Bridge | Documented existence/installer paths, not physical current status | No live Task Scheduler inventory, startup jobs or independent watch loops; the historically disabled Supervisor may need checking |
| AUTO-08 | 1 source runner | Keyboard-first, same-tab code is present | Signed-in browser driver, live completion receipts, stable stop/resume and account selection have not been demonstrated |

The known **33 displayed inventory entries** (10+19+3+1) are *not* a proof that only 33 automation mechanisms exist. CF-200 work orders (200 total) are work items rather than scheduled jobs. GitHub CI suites are workflows, not necessarily research agents.

## Harsh findings (priority first)

1. **CRITICAL — No master control.** The principal Start/Pause/Resume/Emergency Stop controls cannot perform operations. A one-panel inventory with disconnected buttons does not meet the feature acceptance.
2. **HIGH — Incomplete repository coverage (fixed in this branch).** The previous controller showed only five cron workflows despite 19 workflow files. Source parity tests must compare all filenames and trigger classes on every change. All 19 now appear, with the 14 event/manual entries folded by default for readability.
3. **HIGH — Cloud status can mislead through staleness.** ChatGPT state is a private, manually loaded snapshot, not a live read. The panel cannot prove a task actually paused or whether a scheduled run failed; every status must include provider, origin, timestamp and confidence.
4. **HIGH — Local Windows workers may still run outside any master switch.** Fast Lane can start a child PowerShell every 30 seconds, even when the static dashboard is open or closed. Local sign-in tasks, independently started processes, and health/supervisor jobs need a physical-device inventory, not guesses about a flashing CMD window.
5. **HIGH — Research shutdown staging is incomplete.** 'Stage known research tasks' marks source-classified GitHub entries and only imported ChatGPT entries with a research flag. Unimported private tasks and unknown external automations are not included. Never claim this button selected 'all research'. Preserve grant monitoring and core health systems unless explicitly selected for shutdown.
6. **MEDIUM — The hierarchy is cluttered.** Work orders, source data, optional evidence, AI Tracker, private imports and unavailable controls are all intermixed; the first screen should separate current status, control availability, active jobs, and evidence from deep detail.
7. **MEDIUM — Test green is narrower than user acceptance.** Node tests confirm DOM structure, safe state labels, inventory parity and a draft generator. They do not prove a signed-in account was changed, a live task resumed, a Windows worker stopped, or an entire AUTO-08 conversation sweep completed.
8. **LOW — A number in source is not discovery.** Ten ChatGPT placeholders and three Windows records are historic inventory, not a complete current provider-wide scan.

## Specific recommendations, in order

**R1 — One authoritative registry, not a second automation engine.** Model each automation using `provider, stable_private_id, title, trigger, owner_scope, target_account, state, observed_at, evidence_ref, last_result, local_or_cloud, can_start, can_pause, can_stop, risk, provenance`. Keep personal IDs and credentials private; public views display only consented summaries. Enumerate all 19 GitHub workflows plus any future additions automatically by traversing repository source.

**R2 — Split one-page UX into three understandable areas:** (a) **Now running / attention / disconnected**, (b) **Controls** by ChatGPT, GitHub, Windows, AUTO-08, and (c) **History & evidence**. Put the global Stop beside the current active job only when it is truly wired. Do not suggest a global stop controls other providers unless they have a verified adapter.

**R3 — Connect one provider at a time.** Start with current ChatGPT scheduled tasks through an authorized provider-side action; then public GitHub runs/status; then an explicit owner-local Windows bridge, retaining the narrow relay allowlist. Each authenticated adapter must publish a confirmation receipt for every command and a safe rollback. Do not fabricate a local PC capability from a GitHub repository edit.

**R4 — Make shutdown staged, reversible and verified.** Require a generated target list, exclusions (especially grant watch), a deliberate human approval, a stop/pause command on each provider, a follow-up state read and a failure summary. The current stage/copy feature is only preparation, not a shutdown.

**R5 — AUTO-08 stays keyboard-only and one-tab.** One explicitly selected signed-in account, one worker tab navigating the current page in place, keyboard focus/type/Enter, exact `continue`, wait until the reply completes, durable checkpoint, bounded pass, stop on ambiguity. No mouse coordinates or tab proliferation. Validate a single authorized conversation live before claiming readiness.

**R6 — Govern by evidence, not visual green lights.** Add a test that the UI never labels source-present as running. Display last updated and whether status was authenticated, owner-reported, self-reported, or unavailable. Test source inventory parity and adapter-level pause/resume end-to-end before enabling switch controls.

## Narrow acceptance path

1. **Inventory gate:** all GitHub workflow files represented with correct schedule/event classification; private ChatGPT list checked without publishing details; Windows known/unknown distinction; AUTO-08 listed.
2. **UI gate:** status/limitations legible on phone and desktop; no false active buttons; no silent disappearance of an existing automation; scope of 'research' explicit.
3. **Execution gate:** one real provider action with authority and receipt + confirmed reread + rollback, before enabling the associated button.
4. **AUTO-08 gate:** a successful 1-chat keyboard-only, same-tab test with receipt and correct account; only then expand the batch.
5. **Global switch gate:** master switch becomes enabled **only after** each intended provider has a verified stop/pause adapter and 'partial coverage' is shown; never promise a global shutdown while an unmanaged worker can continue.

**Boundaries:** No task has been paused or resumed from writing this audit; no HP scripts, personal records, public relay allowlist, automation schedules, CF-200 counts, ownership rules or finance permissions are changed.

Source references: [Master operating prompt](../automation_200/MASTER_OPERATOR_PROMPT.md) · [continuity](../automation_200/MASTER_CONTINUITY_PROMPT.md) · [Work prompt](../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md) · [Controller source](../automation_200/mission_control/dist/controls.mjs) · [UI source](../automation_200/mission_control/dist/controls-ui.mjs) · [inventory regression test](../automation_200/mission_control/tests/controls.test.mjs) · [AUTO-08 source](../automation_200/continuation_keyboard/).


## November 9, 2026 — current-account/source reconciliation (20:50 Eastern)

**Status:** provider-confirmed inventory counts and source-verified workflow parity. The earlier **10 ChatGPT / 19 GitHub / 33 total** table above is preserved as a dated historical snapshot; it is **not** the latest observed inventory. This update is part of **P0 Mission Control**, under **CF-CORE / UCC-001 / CF-MESH-001**; P1 decision rules, FIN-09 funding and AUTO-08 remain separate linked projects.

| Surface | Read-only current evidence | Remaining uncertainty |
|---|---|---|
| ChatGPT automations | **11** tasks in authorized account-native listing: **5 enabled, 4 paused, 2 completed** (observed November 9, 20:50 ET). Identifiers, titles, prompt bodies and recipient details are **not** public. | Source UI cannot call account-native task actions. Its boolean-only private file import cannot distinguish which not-enabled row is completed versus paused, so its safe status is **"Last reported not enabled (pause/completion not distinguished)"**. This wording already appears in current [controller source](../automation_200/mission_control/dist/controls.mjs). |
| GitHub Actions | **25** `.yml` workflow files enumerated from the public `.github/workflows/` directory; **25** distinct corresponding public controller rows, **5** marked scheduled and **20** event/manual. No missing/extra identifiers in this bounded source cross-check. | Filename parity and trigger labels are source-level; they do not prove every workflow is enabled or that recent scheduled jobs ran. |
| Owner-local HP tasks | **3** documented CF-0 local tasks, not a live Windows Task Scheduler inventory. The public [health report](../relay/health/latest.json) contains **32** total receipts and **10** ping receipts, collected **2026-11-10 01:22:08 UTC**; it was under the source health classifier's 45-minute fresh window at this inspection. | This is a public self-report and **not** HP identity, unattended scheduling, command correlation or machine control. |
| AUTO-08 | **1** owner-selected, one-tab Chrome runner source; synthetic browser tests documented. | No signed-in one-chat opt-in acceptance receipt; iPhone browser does not host the Chrome extension. |

**Known inventory entries at this checkpoint:** **40** (11 private account tasks + 25 public workflow definitions + 3 documented Windows tasks + 1 AUTO-08 runner), **not** 40 simultaneously running automations. Public [CF-200 registry](../automation_200/registry.json) remains **87/200** verified work orders; it is a task registry, not an additional automation count.

**Actions and regression boundaries:** The owner-account state was read, not changed. The source already contains the safer not-enabled status and 11-slot historical count; avoid reintroducing the incorrect “paused” label or merging a redundant conflicting branch. A private owner-importable snapshot is prepared outside the public repository for one optional **in-memory** import to [Mission Control](https://whoiwts110217-creator.github.io/CF-0/mission-control/); the public controller never receives its private task names or IDs. The static master switch remains disabled, and no HP, ChatGPT, GitHub Actions or financial schedules were paused/restarted.

**Continuity evidence:** The current-public three-prompt preflight read Operator blob `6bbee198be687c1d31fef2f08678cf15c4fc76e2`, Continuity blob `d6f1484bb5fb3cacdde438a3a05074d13bcdff72`, and Work blob `a61c513e2ffb6ed02b12dacf0afb460fe47b4600`, then [public three-chat mesh](PUBLIC_THREE_CHAT_CONTINUITY_MESH.md) and UCC-001. Current source checked: controller blob `7ca6de12fdcaceb8e333a4d6779d0821002d5e88`. A recent [Mission Control source test run](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42737518351) passed on its own main-branch head; this does not certify a later moving head.

**Next three P0 tasks, ordered:** (1) Independently confirm the current source parity and deployed controller labels after concurrent repository merges; (2) implement and authenticate **one** provider-specific control with provider read-back and rollback before enabling its UI action; (3) verify one owner-selected signed-in AUTO-08 conversation receipt and the separate HP scheduled-origin correlation when authorized evidence becomes available. **FIN-09** outreach, customer replies and existing grant watch continue independently without replacing these priorities. **Owner action: none for source inventory; signed-in device acceptance remains an explicit opt-in gate.** Rollback: revert only this dated audit addition; historical audit and code remain unchanged.
