# CF-0 — Parallel Operator Coordination Protocol (v0.1)

**Status:** Public operational proposal, source-level only. **Owner direction:** multiple prompts and chats may run concurrently; proceed without corrupting each other's work. **Project:** Kiara Lynn Rose Smith's Caveman Focus.

## Problem and new guess

Multiple ChatGPT conversations and scheduled executors can read the same public `main` state, make different assumptions, and attempt overlapping edits. A shared prompt is not a lock; a mission board is not an atomic task claim.

**Working guess:** treat each operator as an independent, potentially stale worker. Coordination should depend on durable GitHub evidence, explicit work ownership, idempotent operations, and safe conflict handling—not an assumption that operators can see each other's current chat.

## Operating rules, effective as guidance for this lane

1. **Fresh preflight:** Before any consequential CF-0 decision, read the full current public operator, continuity, and Work prompts in their prescribed order. Inspect registry, mission board, capability contract, and applicable source. Record actual blob SHAs.
2. **No implicit chat synchronization:** A separate chat's intention, in-progress work, or verbal status is not a durable claim. Public commits, issue state, task evidence, and validated receipts are observable; private conversations may be inaccessible.
3. **Partition work by file and acceptance condition:** Prefer an independent artifact that cannot overwrite another operator's work. Do not edit the central `registry.json`, `events.jsonl`, `MASTER_MISSION_BOARD.md`, master prompts, or HP relay deployment in a side lane without rechecking the active primary executor and reconciling live state.
4. **Optimistic concurrency:** For an existing file, fetch its current blob SHA immediately before an update; pass that SHA to the GitHub update API. On conflict, re-fetch and reconcile, never force-overwrite. A SHA guard prevents some lost updates but does not provide a multi-file transaction.
5. **Unique changes:** Give every independently published artifact a distinct stable path and link to its source. Reuse existing work-order IDs only when they actually apply; do not create a second authoritative task registry.
6. **Evidence before promotion:** A document, idea, or source-level test is not a verified CF-200 acceptance, real HP deployment, unattended operation, or income. Only the responsible evidence-gated ledger update can promote status.
7. **No duplicate side effects:** Never issue duplicate external messages, payments, device commands, scheduled tasks, or public promotions because another chat might have done them. Check existing receipts and idempotency keys first; require applicable authority.
8. **Collision handling:** If another operator has modified a target, stop that write, preserve both contributions, compare original intent and evidence, and choose a non-overlapping next task. Do not auto-merge conflicting owner instructions.
9. **Safe alternate:** When P0 implementation overlaps or requires inaccessible HP evidence, work on independent P0 tests, reproducible diagnoses, documentation, or a bounded P1/P2 artifact without claiming that P0 is complete.
10. **Handoff:** Report sources read, work lane, exact changed paths/commit, test scope, remaining uncertainties, and next independent task. The next operator must re-read current `main`, not blindly reuse this snapshot.

## Suggested durable work-claim design (NOT implemented)

For future development, use a small claim record with `task_id`, `operator_id` (nonpersonal random identifier), `base_commit`, `claimed_paths`, `acceptance_target`, `lease_expires_at`, `state`, and `evidence`. A lease expiration is only a hint to re-evaluate; it must never authorize overwriting a changed file or duplicating an external action. GitHub branch protections or a single serialized merger would be needed for stronger coordination. A collection of separate JSON claim files is **not** a guaranteed atomic lock.

## Current lane for this conversation

**Lane:** Third-Option Hypothesis / cross-operator coordination, source-safe documentation and future isolated tests.

**Primary CF-200 executor:** Existing scheduled/other-chat executor remains responsible for verified registry changes, central mission-board progress, and owner-approved HP execution.

**Initial source observation:** `automation_200/registry.json` reports 69/200 verified, blob `8114ecc161c4ffd8773913625b5b48b52f6ef5a7`. This is a point-in-time observation; check again before citing a later count.

**Previously published related proposal:** [Third-Option Hypothesis](THIRD_OPTION_HYPOTHESIS.md), conceptual only.

**No claims:** This document does not install a lock, create an automation, change permissions, verify a CF-200 work order, or confirm that another chat is idle.

## Minimal collision test plan for future code

- Two workers read the same file SHA; first writes; second update with stale SHA must fail without erasing first.
- Two workers select the same task; only one authoritative evidence promotion is accepted.
- Expired work claim plus changed source must trigger reconciliation, not automatic overwrite.
- Replayed external action with the same idempotency key must not repeat side effects.
- Missing peer status must lead to a non-overlapping task, not an invented confirmation.

**Next action:** Implement isolated synthetic tests against the actual existing update/registry workflow when its code and acceptance criteria have been inspected. Preserve all current owner priorities and source permissions.
