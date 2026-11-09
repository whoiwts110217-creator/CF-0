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
