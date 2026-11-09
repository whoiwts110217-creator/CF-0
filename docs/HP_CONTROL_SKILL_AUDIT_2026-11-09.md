# CF-0 HP Control Skill — adversarial continuation and public-state audit (2026-11-09)

**Continuity ID:** CF0-P0-HP-CONTROL-SKILL-001  
**Parent:** CF-0 P0 automation / existing owner-local HP relay  
**Related:** `relay/`, `bridge/`, Mission Control, AUTO-08, CF-200  
**Owner instruction:** Continue carefully and double-check public updates, following the earlier harsh critique.  
**Status:** **Public audit only; source-level candidate 1.2 reviewed locally. NOT deployed, NOT a live remote controller.**

## Exact baseline and evidence

- Original public operating skill: [`skills/cf0-hp-control/SKILL.md`](../skills/cf0-hp-control/SKILL.md), blob SHA `1ebb94efda38cce263299f1dad00b8fd2cd064a1` inspected on 2026-11-09. This file documents a local package but contains no live HP executor or universal account-control adapter.
- Current canonical operating sequence re-read in order (2026-11-09): `automation_200/MASTER_OPERATOR_PROMPT.md` blob `22ae58c3bc1a7513ef45e4c8267ea011a56bb357`, `automation_200/MASTER_CONTINUITY_PROMPT.md` blob `6d0cf4ac809172d0525de288d87a340d1f01537c`, `automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md` blob `150c6629ba1496c2b05d9f4afb31929ad142357e`.
- Relevant owner boundaries: [`OWNER_CAPABILITY_CONTRACT.json`](../automation_200/OWNER_CAPABILITY_CONTRACT.json), [`UCC-001`](UNIVERSAL_CONTINUITY_CONTRACT.md), [private operator gate](../bridge/PRIVATE_OPERATOR_GATE_CF100.md), [controller audit](MASTER_CONTROLLER_AUDIT_2026-11-09.md), and [existing public relay](../relay/cf_public_relay.py).
- Authoritative registry read from `main` during audit: `automation_200/registry.json` blob `81be05aa5a9a3306e7ca0f1005e4840373b4d365`, **87 of 200** tasks verified at that exact revision. This audit itself verifies **no additional CF-200 task**. The count may change later.
- Public health snapshot inspected during audit: `relay/health/latest.json` reported 32 local receipts and 10 ping receipts, at a self-reported collection time `2026-11-09T16:47:06+00:00`. This is a **public self-report**, not independent HP identity, Windows Scheduler provenance, or a command/receipt correlation for unattended execution.

## Adversarial local candidate results

The previous v1.1 candidate (delivered privately in the owner conversation, not installed or present as code on public `main`) was rerun independently: **14/14 Python mock tests passed**, syntax compilation passed. Two v1.0 defects were reproduced and corrected: false successful resume after unknown scheduler readback; false newly-paused result for an originally disabled task.

A separate **v1.2 review ZIP** was generated and integrity-checked in the current conversation; package SHA-256:

`b0193d84877b0a4cc1fecc6905bad449ce6731701f887e5f99d3960f2b070918`

A packaging self-check caught a stale audit-file hash in the first locally assembled ZIP manifest; the candidate was repacked in the owner conversation, every included file SHA-256 was independently checked against the embedded manifest (6/6 matched), and the ZIP passed CRC validation. Only the **verified replacement** ZIP hash above should be used. No executable or HP schedule was changed in this repack.

The v1.2 candidate adds a local SHA-256 fingerprint across Task Scheduler name, root path, principal, actions and triggers; requires owner-principal and Limited run-level readback; and blocks or marks uncertain changed/unknown task identity on pause/resume. **19/19 mock tests passed**, Python syntax compiled. Private executable details are not returned by the inventory. This ZIP is an owner-chat attachment, **not available from public GitHub**. No code, executable, Windows schedule, token, bridge or HP deployment is changed by this documentation commit.

**Limitations remain high priority:** Windows Task Scheduler has not been exercised; source tests do not establish real task identity, child-process shutdown, concurrency/lock safety, interrupted-operation reconciliation, or live HP access. Existing v1.1 pause records lack an identity digest; **there is no automatic migration** and any real previously paused record must be reconciled by the owner before replacement. Never tell the owner to overwrite a functioning installation with the review candidate.

## Security, acceptance and authority

1. Current PUBLIC queue is limited to `ping`, `hp_status` and configured read-only `sidecar_verify`. Do not add generic shell, file, browser, payment or GUI controls to that public queue.
2. Richer HP control remains a proposal under **PCA-004**, requiring a separately authenticated private channel, exact reviewed action manifests, explicit owner approval and an independent HP-local opt-in. No new permission was inferred from this audit.
3. Verify a single owner-local **read-only** task inventory first; compare actual task paths/principals/actions privately without exposing machine paths or personal details in public logs.
4. Before any pause/resume test, add cross-process operation locking, a precise transaction ledger, recovery for unknown outcomes and a rollback plan that preserves original Windows tasks, the SQLite receipt ledger and old source.
5. Authenticate one private request with a correlated receipt, reject duplicate/expired/altered jobs, and correlate its actual HP execution to Windows event/Task Scheduler evidence before calling unattended operation proven.
6. Wire one supported adapter to the existing Mission Control only after a genuine live readback. AUTO-08 remains an independent single-tab, keyboard-only, serial-completion flow; no implied account/browser control.
7. Test in Windows CI and then on the explicitly authorized HP. A passed cloud test means **source-level acceptance only**.

## Public update checks and next three

- The original skill still exists on public `main` with its previous SHA; no silent v1.2 promotion.
- Existing publicly documented relay allowlist and owner capability regression are preserved. This audit does not pause a task, enable Notepad in the public relay, alter grants/finance or read a private chat.
- **Next 1:** Add/verify cross-process locks and migration/reconciliation for existing local pause records in an uninstalled candidate.
- **Next 2:** Validate exact Windows task identity/readback and rollback in a disposable/safe Windows environment; compare against actual owner HP only after a separate local opt-in.
- **Next 3:** Implement a signed, scoped *private* request and receipt validator using existing bridge transport without changing its current accepted actions.

**Rollback:** Removing this new documentation file restores the prior public documentation state. The earlier skill, relay, Mission Control, task registry and schedules are unchanged. Future Work runs must re-fetch all three operating prompts from `main`; this page cannot authorize local operations.

## v1.3 crash-safe candidate — November 9, 2026 (source-level, no deployment)

**Continuity:** `CF0-P0-HP-CONTROL-SKILL-001`. Owner's instruction was to continue careful P0 work, preserve the existing HP relay and verify public updates. This is a separately packaged owner-local **REVIEW** candidate, not a live source cutover or a granted remote permission. v1.2 and the original v1.0 source remain intact.

- Added an owner-local cross-process OS file lock around `pause`, `resume`, read-only pause-record review and owner-confirmed recovery reconciliation. Lock acquisition fails with `OTHER_HP_CONTROL_INSTANCE_BUSY`; the stable lock file is never deleted during normal release. No new background service or schedule.
- A unique UUID operation ID and `attempting_pause` / `attempting_resume` record are saved **before** any Windows scheduler mutation. A crash or timeout remains an uncertain owner-local record; unknown outcomes are never blindly replayed.
- Re-checks fixed task path, same-user principal, limited-runlevel identity digest and task state **after** typed owner confirmation, before changing the schedule. A second readback follows the attempt.
- `review` only classifies records. `reconcile --task <fixed alias>` uses owner-local typed confirmation and repeated matching identity/state readback to settle evidence of an action that appears already completed. The reconciliation path does **not** enable/disable/start/stop Windows tasks. Legacy v1.1 records missing a fingerprint remain held for separate manual review.
- **30/30 offline tests passed** on a Linux sandbox, including a real competing-process lock test and simulated Task Scheduler responses. Python syntax compilation passed; CLI correctly reported no Windows connection in this sandbox. **This does not establish Windows lock or Scheduler behavior on the HP.**
- Candidate ZIP in owner conversation: `CF0_HP_Control_Skill_v1_3_Crash_Safe_REVIEW.zip`. SHA-256: `8a3b18a38b6f4822f2f082ec6fc8cc525ad050fe4d29126b9a609c91920032e2`. ZIP CRC passed and all **6 source files** matched the included manifest digests. The binary is **not** uploaded to public GitHub and is **not** installed on the owner's HP.

**Public update limits:** No changes to `skills/cf0-hp-control/SKILL.md` (still v1.0), `relay/cf_public_relay.py` (public allowlist unchanged), `bridge/`, Windows scheduled tasks, Mission Control, private accounts, registry `automation_200/registry.json`, or append-only CF-200 verified evidence. This documentation entry is **not** a CF-200 completion or proof of an authenticated HP connection. Private archives were not opened or published.

**Next acceptance gates, in order:** (1) isolate task identity, lock semantics, rollback and uncertain-state behavior in disposable *Windows CI* and a locally authorized HP pilot; (2) make child-process outcomes separately observable from schedule-disabled state; (3) design/test a precise owner-approved private command+receipt validator under PCA-004 without broadening the existing public relay or claiming a wired Mission Control switch. Preserve owner powers, exact AUTO-08 one-tab keyboard-only semantics and P0→P1→P2→P3 order.

**Rollback:** revert only this new audit-doc update if the evidence is wrong; no executable or schedule rollback is needed because none was changed. Subsequent agents must re-fetch all three public operating prompts from current `main`, this audited candidate's evidence and the latest registry/CI before making a new claim.

## v1.5 owner configuration pin — local review candidate, November 9, 2026

**Continuity ID:** `CF0-P0-HP-CONTROL-SKILL-001`. **P0 automation.** Owner instruction: continue carefully and verify public updates. This is an additional public-safe audit entry, **not a controller deployment or new authority**.

The v1.4 local candidate had an important trust gap: matching name, own Windows SID, Limited run level and a stable configuration hash does **not** prove that the executable/arguments/triggers were intentionally approved. A same-name unexpected command could otherwise be modified. The new **owner-local v1.5 configuration-pin REVIEW candidate** addresses that at source level:

- `pin --task relay|fastlane|bridge` displays full executable/arguments, principal and triggers **only in the owner's private Windows console**, computes a matching fingerprint via two readbacks, and requires typed local approval to create `%LOCALAPPDATA%/CavemanFocus/HPControlSkill/approved_task_pins.json`.
- `pause`, `resume` and interrupted-operation reconciliation refuse to act without a matching approved pin. Pin changes and legacy/mismatched pause-records fail closed; pins are never silently overwritten. Pinning itself does not change any Windows task.
- Owner-private command arguments, local paths and pin files must **never** be uploaded to public CF-0.
- **42/42 offline mock/source tests passed**, Python syntax compiled; Windows is not available inside the local test container. Full controller Windows/on-HP behavior remains unverified.
- Versioned owner-chat artifact: `CF0_HP_Control_Skill_v1_5_Config_Pin_REVIEW.zip`, **SHA-256 `3c678e698eec60c770d8902be6a0ab45a1b5fa32b11ce2202b8294c84dde21db`**. All 6 listed file hashes matched the embedded manifest, and ZIP CRC passed. This ZIP is **not public repo source, not an installer and not deployed**.
- [Merged Windows primitive test PR #38](https://github.com/whoiwts110217-creator/CF-0/pull/38) passed ephemeral-runner scheduler + process-lock checks on head `95d3b2f7b64165a9d98c67e117aaa4d890c8448f` ([HP probe](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42669754568), [full Windows regression](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42669754525)). **That run did not execute the v1.5 controller.**
- [Draft PR #46](https://github.com/whoiwts110217-creator/CF-0/pull/46) adds a disposable Windows task-command drift probe. First workflows [42674339040](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42674339040) and [42674339079](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42674339079) returned `conclusion=failure` with **zero jobs** from the GitHub Actions jobs API. No Windows script execution or test-level failure is demonstrated; reason remains unknown. **Leave PR #46 draft/unmerged; never call v1.5 Windows-tested from this evidence.**
- This pin file is local trust metadata, **not a digital signature**, and it is not a defense against someone with write access to the same local Windows user account. It does not authenticate ChatGPT, iPhone, Mission Control or a physical HP.
- The existing public relay remains `ping`, `hp_status`, configured read-only `sidecar_verify`. No changes to owner/supervisor schedules, private bridge powers, ChatGPT accounts, public registry task count or original creative/financial sources.

**Next acceptance sequence:** (1) diagnose why PR #46 checks completed without jobs and obtain a real Windows drift-probe result; (2) run the **actual** v1.5 controller's read-only inventory/config-pin preflight on a disposable Windows task with explicit owner-local opt-in, including legacy pause recovery; (3) review the separate authenticated private request+receipt adapter under owner approval PCA-004. Do not deploy a full remote controller, assume child-process termination, or publish private machine arguments.

**Rollback:** revert this audit-doc change alone if wrong; old source/permissions and the v1.4 ZIP remain intact. Re-fetch the current operator, continuity and Work master prompts from `main` on the next run.

## Windows configuration-drift CI milestone — post-review closure (2026-11-09)

**Continuity:** `CF0-P0-HP-CONTROL-SKILL-001`; parent P0 automation; related `skills/cf0-hp-control`, public relay, Mission Control and AUTO-08. **Evidence level: source-level Windows disposable tests passed; not real-HP deployment.**

- [PR #46](https://github.com/whoiwts110217-creator/CF-0/pull/46) was merged as [`233ff82240a17baf2be601664668886fbbb79f98`](https://github.com/whoiwts110217-creator/CF-0/commit/233ff82240a17baf2be601664668886fbbb79f98), after a revised task fingerprint test fixed a flawed self-comparison. The precise change was only two public files: `skills/cf0-hp-control/tests/windows_identity_drift_probe.ps1` (new disposable Windows test) and `.github/workflows/cf0-hp-control-windows-probe.yml` (extend the existing test workflow).
- [Windows disposable drift + byte-lock run 42677391416](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42677391416) **passed** at PR head `3e6d99b9ffc8bbd32610f11372a4d058efce5a2c`. It registered an inert future-triggered test task, confirmed a different command invalidated its digest, restored its original command and fingerprint, and cleaned up. **This does not run the v1.5 controller itself.**
- [Full Windows relay regression 42677391398](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42677391398) **passed** at the same PR head, including existing public relay, owner capability guard, continuity and scheduled task source protections. A new post-merge workflow run has not been independently required or verified to claim these PR-head results.
- The initial two [42674339040](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42674339040) / [42674339079](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42674339079) `failure` reports had **zero jobs**, so they provide no evidence that the test script failed. They are historical and still lack an independently verified root cause. The subsequent real Windows jobs passed.
- The **local v1.5 review package** still has **42/42 offline mock tests** and independent ZIP/manifest verification, but it remains **uninstalled, not committed as executable source to this public repo, and unverified on owner HP**. Its owner-local config-pin review is a proposed safeguard, not an authenticated device control channel. Public relay command allowlist and owner task schedule remain unchanged.
- Source readback after merge confirmed `automation_200/registry.json` blob `81be05aa5a9a3306e7ca0f1005e4840373b4d365`: **87/200 verified**, unchanged by the test milestone. No private data, ChatGPT account identity, local executable arguments, tokens or credentials were published.

**Next three:** (1) test actual v1.5 controller's *read-only* Windows inventory/config-pin preflight using a reviewed disposable task and a private source delivery boundary; (2) cover lock recovery after forced interruption and child-process vs schedule semantics on a disposable Windows setup; (3) prepare a narrow private signed request/receipt validator subject to PCA-004 owner-local approval, without expanding the public relay or enabling Mission Control buttons prematurely.

**Rollback:** revert merge commit `233ff82240a17baf2be601664668886fbbb79f98` after reviewing later dependent test edits. This removes only the new drift probe and workflow reference; no installed HP program or owner schedule was changed. The operator on the next run must re-fetch all three canonical prompts from public `main`.
