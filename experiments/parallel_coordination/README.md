# Parallel coordination: isolated source experiment

This directory implements **advisory, side-effect-free preflight checks** for competing CF-0 operators. It does **not** create an atomic GitHub lock, claim a CF-200 work order, contact an HP, alter a scheduler, or write to the main mission board.

Run from this directory with Python 3.10+:

```sh
python -m unittest discover -v -p 'test_*.py'
```

## Source-level verification, November 7, 2026

- **29 of 29 local Python unit tests passed** in an independent local environment using byte-exact source files whose Git blob SHA-1 values match the GitHub experiment branch. This is **not** a GitHub Actions result or an HP test.
- Verified `parallel_guard.py` blob `0fc8c1925d53ff5aab2b940303d3ab5f838a4600`; verified `test_parallel_guard.py` blob `967bc412ef39c474507fe40b2dfa2078f193ebfd`.
- A **real GitHub Contents API stale-write probe** was performed **only on this experiment branch** using `cas_probe.md`:
  - [Created test fixture](https://github.com/whoiwts110217-creator/CF-0/commit/0716ac9abe846bb6a39d1205d4639c12e7c81599), original blob `3fbbd1bddf598b1e5d644b8762042d3aacb434bb`.
  - [First update accepted](https://github.com/whoiwts110217-creator/CF-0/commit/ebc2d2251b807b733cb0b9b0fca499564f5ff364), new blob `82f7d46430e85a21d1bc2c731bbbedc8d7eeeeac`.
  - An attempted second update with the original blob SHA returned **GitHub HTTP 409 Conflict** (no commit created). A read afterward verified the accepted blob and its content remained intact.
- Multi-path proposals now require expected and observed versions for **every** claimed path. Missing and stale path snapshots are rejected. See [guard patch](https://github.com/whoiwts110217-creator/CF-0/commit/1e8061b83ef60dd41fd0f2806a06dc06856c64c2) and [tests](https://github.com/whoiwts110217-creator/CF-0/commit/528f4420b2f16f8ee7ad4708059bbcb85abb3197).
- **Create-only claim experiment:** [claim envelope source](claim_envelope.py) (blob `63ef300fcdb4703c2f11e3887e2cf04f0d1e2d51`) and [11 tests](test_claim_envelope.py) (blob `c282ff1c1a09b3d16ea38eeaf5bf21002ed98b4a`) are isolated from the operational registry. The payload uses deterministic per-task paths and a bounded one-hour maximum lifetime, but expiry **never** means permission to reclaim or retry a remote side effect. A SHA matching the expected format still requires external source verification.
- **Real GitHub create-only file-exists probe:** [synthetic fixture created](https://github.com/whoiwts110217-creator/CF-0/commit/ab6be8cd31a627df444643e15f6efbb36d93b233) on this experiment branch. A second `create_file` call at the identical path, with changed worker ID, was rejected with **GitHub HTTP 422** (missing update SHA). Fetch afterward confirmed the original fixture remained intact. This verifies **sequential** create-if-absent rejection in the tested API—not simultaneous multi-worker exclusion under all failure modes.
- **Byte-exact full-suite source hashes:** `parallel_guard.py` `0fc8c1925d53ff5aab2b940303d3ab5f838a4600`; `test_parallel_guard.py` `967bc412ef39c474507fe40b2dfa2078f193ebfd`; `claim_envelope.py` `63ef300fcdb4703c2f11e3887e2cf04f0d1e2d51`; `test_claim_envelope.py` `c282ff1c1a09b3d16ea38eeaf5bf21002ed98b4a`.
- A dedicated GitHub Actions workflow exists on this branch, but **passing CI evidence has not yet been confirmed**. A GitHub source commit is not CI acceptance.

## Remaining limitations and next tasks

1. **CI:** Confirm a completed Actions job from this branch and troubleshoot any failure. Do not label it passed merely because the workflow file exists.
2. **Multi-file atomicity:** Per-file SHA checks do not provide transactional guarantees. The remote API must apply a version guard separately to each write, or an approved single-commit strategy must be designed and tested with rollback/reconciliation.
3. **Coordination integration:** The claim envelope is a *prototype payload generator*, not a deployed lease service. It does not create claims or verify that the underlying CF-200 task is eligible. Verify an actual branch-level concurrent-creation race, explicit claim ownership, expiry recovery and safe conflict reconciliation before suggesting integration. Never turn a public claim into authority for HP execution or verified CF-200 completion.

**Branch:** `experiment/parallel-coordination-v1` (not merged to `main`).  
**Related policy:** [Parallel Operator Coordination](../../docs/PARALLEL_OPERATOR_COORDINATION.md).  
**Preflight public source blobs:** operator `f8f0c94c28cd28cc0402daf4f21bd875e1417932`; continuity `cac63dead1e00592c1d12ea6562639b02893d81f`; [Work self-reference](../../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md) `5da1a390f31ee8f57e5829ef368062f9215c28ac`. The next operator must fetch all three again from current public `main`.  
**Authoritative registry observations:** original prior `72/200` at blob `38e68cca79e5aa8c3e01829cdd55eb6ab4393632`; latest checked this run `73/200` at main blob `38b6cf4b5f30e22a30246ed85cd345b06f352029`. Re-read main before any later count.  
**Main HP heartbeat and unattended schedule:** No new device evidence generated by this experiment.  
**Privacy and owner control:** No private archives, credentials, receipts, manuscripts, income records, HP relay commands, schedules, prompt changes, or central CF-200 evidence changed.

## November 7 continuation — live race and fail-closed partial-write recovery

**Concurrent duplicate-create probe (public synthetic fixture only):**
- Two `create_file` requests targeted the same `race_probe/CF-098-synthetic.json` at the same time on this branch with different synthetic worker IDs.
- One accepted commit: [`519fdd8`](https://github.com/whoiwts110217-creator/CF-0/commit/519fdd8ea77e27438d78a3edb42538bda68993e6). The other received GitHub HTTP 422 (no `sha` supplied for an existing file). Reading the file afterward showed the accepted worker's exact record.
- This demonstrates **one actual concurrent collision**, not a guarantee against all races or a production claim for CF-098. The fixture says `not_a_real_task_claim: true`.

**Partial multi-file write recovery diagnostics (new code, still not integrated):**
- [`reconcile_writes.py`](reconcile_writes.py) exact blob `8b5964942ec3e1aaeff48e5edd41c81204411ed0`: classifies `COMPLETE`, `NO_APPLIED_WRITES`, `PARTIAL`, `CONFLICT` and `UNKNOWN`. It distinguishes *observed missing* files from *not observed* files, records drifted paths, and always disables automatic retry.
- [`test_reconcile_writes.py`](test_reconcile_writes.py) exact blob `131f40401c03168236fca0dd565b527bd7c0bdc4`: **15/15 local tests passed** using byte-exact local copies whose Git blob SHA-1 values matched these public source blobs. This is a local Python unittest outcome, not confirmed Actions CI or physical HP execution.
- Combined test inventory on this branch is **44 tests** (29 previously locally verified + 15 newly verified). This continuation independently ran the 15 new tests; a fresh full-suite CI pass remains required.
- **Important:** `COMPLETE` describes agreement between reported file SHA observations and proposed targets. The function does not authenticate observations, establish atomic commits, or prove side effects were safe. Any non-complete outcome requires source re-check and reconciliation before further edits, with owner approval where the contract requires it.

**Current main snapshot inspected before this continuation:** CF-200 **75/200 verified** at Git registry blob `cecdcea4f9dcc00e1b046f39875433aaeb7e63d6` (other workers may advance it again). The experiment did not change the authoritative count, main mission board, public prompt bin, HP permission allowlist, scheduler, or any private continuity files.

**Next three executable gates:**
1. Obtain actual GitHub Actions success evidence for the entire experiment suite; fix failures without granting new capabilities.
2. Test recovery diagnostics against a further **synthetic** GitHub partial-write trace, carefully preserving existing file contents.
3. Review durable-claim ownership and safe expiration/recovery separately before any merge or real task reservation. Expired claims are not permission to repeat actions.

**Preflight read this continuation:** public main blobs operator `f8f0c94c28cd28cc0402daf4f21bd875e1417932`, continuity `cac63dead1e00592c1d12ea6562639b02893d81f`, and [Work self-reference](../../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md) `5da1a390f31ee8f57e5829ef368062f9215c28ac`. Read all three again on next run.

### Real GitHub partial-write readback test

A second source-level test was performed against **synthetic fixtures in this experiment branch only**, with no real work-order reservation or side effect:

1. Created `recovery_probe/a.md` (blob `5bda26221f290580c0c450eb8aa50da79bdc3527`) and `recovery_probe/b.md` (blob `8fb358ee8fd07a617c701c67b6ad2cb1334fe236`).
2. Committed **only A's planned update**: [`0d95c6d`](https://github.com/whoiwts110217-creator/CF-0/commit/0d95c6de0bab013076256d0956b3d6c8799a73b7), observed A blob `c0b8cd0a5a0268d6e2bfcc51de22b33baf93a5c2`. B's planned update was intentionally **not sent**.
3. Read both files again from GitHub: A remained updated and B remained at its original blob. The computed Git blob hash of B's hypothetical desired content was `e8407889cd708ec4ceb489443dbe272018a8877f`; B did not have that hash.
4. Passed those real GitHub readback hashes into the locally tested, byte-matched `reconcile_writes` implementation. It returned `PARTIAL`, exactly A in `applied`, exactly B in `untouched`, no drift/unknown files, and `automatic_retry_allowed=False`. A Python assertion for this outcome passed.

This verifies classification of **one controlled two-file interruption**, not the integrity of an independent multi-file transaction or recovery after an actual worker crash. No automatic rollback, repair, or claim release was attempted. An agent handling a genuine interrupted operation must re-read each remote file and reconcile safely with current owner authority.

## November 7 continuation — interrupted claim review is fail-closed

**Isolated change; not deployed to the CF-200 executor.** Added [`recovery_review.py`](recovery_review.py) (Git blob `233d6975e8c3856f86cf61c3cefb625fac0e2076`, [commit cb6785b](https://github.com/whoiwts110217-creator/CF-0/commit/cb6785ba00bc99e113413f7fe4b3df7a44fdb7f9)) and [`test_recovery_review.py`](test_recovery_review.py) (blob `7a5242ac2f97ba64fe4ecf19cf0eded01ee67041`, [commit 26ba091](https://github.com/whoiwts110217-creator/CF-0/commit/26ba091b93d8cc1a12d48862d9c0e4adaaa704ff)).

- **16 of 16 local tests passed** on exact local bytes. Both GitHub blob SHAs were fetched again and independently matched local Git-style blob SHA-1 calculations. These tests cover expiry, active claim, changed/missing claim, partial/unknown/conflicting file states, complete files not equaling task verification, verified/unknown registry, unknown receipts, absent HP proof, malformed status and naive time.
- The review output is a **diagnostic only**: `HOLD_CONFLICT`, `HOLD_EVIDENCE` or `REVIEW_REQUIRED`, plus specific blockers. Every output unconditionally sets `automatic_retry_allowed=False`, `automatic_release_allowed=False`, `task_verified=False`.
- **Expiry, even with all known file writes untouched, does not transfer execution authority.** An independently verified owner-authorized recovery protocol would be needed before reclaiming a real task.
- **Evidence boundary:** Caller must authenticate live GitHub blob/claim state and independently account for every receipt and uncertain attempt. Passing a Boolean claiming receipts were reconciled does not establish they were. The module must not be treated as proof of GitHub atomicity, physical HP operations, or real-world effects.
- Existing test inventory now includes **60 test methods** across the 4 modules, based on previous 44 + 16 new cases. Only these **16 new tests** were independently rerun during this continuation; no full-suite or passing GitHub Actions evidence is claimed.
- Main registry observed at **75/200** (blob `cecdcea4f9dcc00e1b046f39875433aaeb7e63d6`) before this source update. Verify fresh main before stating any later number. No registry/events, central mission board, public prompts, approval bin, schedule or HP allowlist changed.
- Mandatory public preflight was read in order: [Operator](../../automation_200/MASTER_OPERATOR_PROMPT.md) blob `f8f0c94c28cd28cc0402daf4f21bd875e1417932`, [Continuity](../../automation_200/MASTER_CONTINUITY_PROMPT.md) blob `cac63dead1e00592c1d12ea6562639b02893d81f`, [Work self-reference](../../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md) blob `5da1a390f31ee8f57e5829ef368062f9215c28ac`.

**Next executable gates:** (1) obtain independent completed CI evidence for the entire branch suite; (2) add an evidence-authenticated recovery packet that includes claim and receipt provenance, without expanding authority; (3) test a reviewed claim release/reclaim proposal in a sandbox before any live integration. No additional copy/paste is requested from the owner.

## November 7 continuation — integrity packet and actual GitHub CI acceptance

**Previously unresolved CI gate now has positive evidence.** [Actions run #27](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42413588078) on branch commit [1aef7b5](https://github.com/whoiwts110217-creator/CF-0/commit/1aef7b589a116c99a79bb67319f0d26d6c6b3300) completed **successfully**. The GitHub Actions job log directly reports **"Ran 80 tests ... OK"** and a successful \`guard-tests\` job. The source files on that run included the new [\`evidence_packet.py\`](evidence_packet.py) (Git blob \`c4f0a5cdce5129cdcad4e7c910ad44cc7f861792\`) and [20 packet tests](test_evidence_packet.py) (blob \`e45978103b5482a22773192ba56d6a07e568ec8d\`).

### What the read-only integrity packet actually checks

- Byte-exact local content matches the **claimed** Git blob SHA-1, plus claim task/operator/base SHA, authorized test file scope, status, bounded date window, and non-reclaim policy.
- Synthetic normalized receipt records match expected action IDs, expected paths, request SHA-256, and \`completed\` status; missing, duplicated, malformed, altered or uncertain records fail closed.
- The returned status is intentionally \`INTEGRITY_CHECKED_ONLY\` or \`HOLD_EVIDENCE\`. All results prohibit automatic action retry, claim release, or CF-200 task verification.
- A matching hash does **not** authenticate GitHub origin, signer, authorization, real HP execution, receipt provenance, Windows scheduler, or the external truth of any claimed result. The current public HP relay receipt schema is **not assumed** to be identical to the synthetic normalized receipt schema.

### Cross-module recovery gate

[Integration tests](test_recovery_integration.py) (Git blob \`bdeefc1ac0942eb07e9c297d43fec686aa14a91e\`, [commit 05fe30b](https://github.com/whoiwts110217-creator/CF-0/commit/05fe30b01b2f5e0c4cb2429beb935af552e8d123)) connect **claim envelope -> integrity packet -> partial-write reconciliation -> interrupted claim review**, with five no-network cases: matched evidence still requires review; tampering blocks; partially applied writes hold; missing HP schedule evidence blocks; uncertain receipt blocks. CI confirmation for this **newer** integration commit must be checked separately; run #27 cannot certify code committed after it.

**Main registry at latest inspection:** \`81/200\`, blob \`51a706bdec8f8f206e5ec7a4f4a4e6eeb1cc2593\`; this branch did not change it.

**Preflight versions read fully from current public main:** operator \`f8f0c94c28cd28cc0402daf4f21bd875e1417932\`, continuity \`cac63dead1e00592c1d12ea6562639b02893d81f\`, Work self-reference \`5da1a390f31ee8f57e5829ef368062f9215c28ac\`. Retrieve fresh for the next decision.

**Next three executable gates:** (1) verify the new integrated suite via a completed GitHub Actions job; (2) adapt provenance validation to the *actual* existing public-safe receipt schema only after fetching its authoritative source and tests, not by guessing; (3) review a conservative release/reclaim decision process with owner permission, no automatic retries. No new HP commands or production claim locks have been enabled.


## November 7 continuation — current relay v1/v2 receipt contract

**Development branch, read-only analysis.** Fetched the complete current public main operator, continuity, and Work prompts in order: operator \`f8f0c94c28cd28cc0402daf4f21bd875e1417932\`, continuity \`cac63dead1e00592c1d12ea6562639b02893d81f\`, Work \`5da1a390f31ee8f57e5829ef368062f9215c28ac\`. The current public main [relay validator](../../relay/cf_public_relay.py) blob was \`c2a3fe61448bf947174be2ac5038e32efc2087ec\`; the experiment branch relay blob is \`94c9a9a1574adb8e55d67227b6618a33e4d56832\`. Their \`validate_receipt\` and \`validate_public_result\` function bodies were explicitly compared and matched. Future integration **must** compare against fresh main again.

- Added [\`actual_relay_pair.py\`](actual_relay_pair.py) ([commit a48135a](https://github.com/whoiwts110217-creator/CF-0/commit/a48135ab81af72dadcf05d8a16f5c6c32b1bfa1f), blob \`7b37d3a197cfd65952fd9bd11084776339dcbe38\`) to **reuse** the already-existing relay's validation of v1 and v2 public request/receipt pairs, including canonical JSON hashing, UUID, allowlist, exact result shape, request SHA-256, and v2 response SHA-256. Historical request shape is checked against its recorded issue time, **not** asserted fresh or executable.
- Added [\`test_actual_relay_pair.py\`](test_actual_relay_pair.py) ([commit a36507d](https://github.com/whoiwts110217-creator/CF-0/commit/a36507d4cf1ae41a954f54434dc160137dc88f56), blob \`64f264254e92bb6a5e9dfee07336ceca995086e4\`), with **20 synthetic no-network test methods** for v1/v2, tampering, canonical hashing, wrong paths, mismatches, unsupported actions, public result shape, and missing requests/receipts. The source and tests were fetched back from the branch and their Git blob SHAs verified.
- An independently recorded successful [CI run #27](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42413588078) had **80/80 tests passing**, but it precedes these two new source commits. **No completed CI result for the additional 20 tests has yet been verified.** Do not call 100/100 passed based on an earlier run.
- The helper's strongest positive result is \`CONSISTENT_PUBLIC_PAIR_ONLY\`. It explicitly returns \`physical_hp_proven=False\`, \`unattended_schedule_proven=False\`, \`automatic_retry_allowed=False\`, and \`task_verified=False\`. V1 historical receipts are classified \`LEGACY_REVIEW_REQUIRED\`. A hash-matched public pair is not cryptographic authentication of HP execution or a Windows scheduled poll.
- This module makes **no network requests, writes, command dispatch, receipts, or registry updates**. Existing live HP allowlist remains unchanged. No private data was read or published.

**Fresh authoritative registry observation before this branch work:** \`84/200\`, blob \`304ed3c72df0fb82b6a0eacf6f4dc2e971262c74\`. Other sessions may advance it.

**Next executable gates:** (1) obtain a completed GitHub Actions run for the new actual-receipt tests and inspect its job log; (2) test a real public-safe request/receipt pair readback through an independent read-only consumer, making no HP-origin claim; (3) review whether to merge only the small validated read-only helper after a fresh main/owner-capability reconciliation. No production task claims or auto-recovery are authorized.


### Read-only spot-check against two existing PUBLIC legacy pairs

On current public \`main\`, two already-published ping inbox/receipt pairs were retrieved by matching UUID and independently checked using the exact \`json.dumps(..., sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)\` and SHA-256 conventions of the original relay code. Both request digests matched their respective public v1 receipts; both receipts contain \`status=completed\`, \`result.pong=true\`, and \`result.protocol=1\`. Exact original inbox and receipt Git blobs were observed for each pair.

This is **public content consistency**, not physical HP identity, scheduled-poll provenance, an authentic operator signature, or proof the tests ran on an HP. Neither historical receipt contains a v2 \`response_sha256\`; both must be classified as legacy-review evidence, not promoted into a production release decision. The normal programmatic adapter was not invoked directly on these retrieved bytes; the public spot-check and synthetic adapter tests are distinct verification activities.

**Latest CI boundary:** the last independently confirmed GitHub Actions job was run \`42413588078\` with 80 passing tests. A new workflow run covering the 20 actual-relay tests has **not** yet been independently confirmed from current tool output; pending, not passed.

No owner authorization was expanded, no automatic recovery enabled, and no real task reservation made.
