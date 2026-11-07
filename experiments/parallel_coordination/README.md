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
