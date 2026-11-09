# Resumable focus switching (owner-guided)

This is an **additive P1 improvement**, built on [the existing evidence-gated decision engine](DECISION_ENGINE.md). It does not alter the founder's default P0 automation → P1 priority governance → P2 legitimate finance → P3 other projects order. An explicit owner preference can temporarily elevate *eligible* work, and an interruption can return to the previous task. Hardware, dependency, retry, explicit block and owner-local gates still win over a preference. It does **not** execute tasks.

## Switching contract

- **Continue:** stay on the current eligible task when competing work is at the same priority tier and no owner preference moves another task forward. This reduces constant churn.
- **Switch:** when an eligible higher-tier or expressly owner-preferred task takes over, pause the unfinished task and keep its checkpoint pointer.
- **Resume:** when a previously paused task is selected again, restore its checkpoint pointer rather than re-starting from scratch.
- **Checkpoint required:** if unfinished work has no checkpoint reference, switching is **proposed, not committed**. Record a durable, private checkpoint first; the system does not invent one.
- **Done/blocked/HP:** verified tasks don't require a checkpoint; blocked and HP-only tasks cannot become cloud-executable through a preference or a public heartbeat.

## CLI (from repository root)

1. Review without saving: `python -m automation_200.resumable_focus`
2. Save a local, private initial focus state: `python -m automation_200.resumable_focus --state-file /private/path/focus.json --apply`
3. When a real checkpoint exists, switch to finance temporarily: `python -m automation_200.resumable_focus --state-file /private/path/focus.json --owner-preference CF-<ID> --checkpoint-ref private-checkpoint-ID --apply`
4. Re-run with the previous task as `--owner-preference` to resume, supplying a checkpoint for the task being paused.

Use an actual CF-200 ID from the registry, not the example placeholder. Windows users can use a suitable private local path in place of `/private/path/focus.json`. The checkpoint reference is an identifier pointing at a real saved private artifact, **not** the artifact itself; verify it before asserting successful recovery. The local state file should never be committed to public GitHub. No background process or scheduled handoff was installed.

`--apply` performs an explicit local-only atomic file replace; without it, the command is read-only. Saving a state transition is not evidence that the selected task was executed or completed. An existing owner-authorized Work schedule could separately load this state, but cloud/HP coupling and unattended continuity require independent integration and tests.

## Verification

Run: `python -m unittest automation_200.tests.test_resumable_focus -v`

Tests cover owner override, blocked-task skip, same-tier stickiness, resumable checkpoint preservation, verified task transition, HP and dependency fail-closed gates, invalid inputs, no mutation, and local atomic persistence. These tests establish source behavior only, not HP deployment, revenue, or live account background control.

## Source/provenance

Owner request: make priority changes and project transitions as seamless as possible while preserving P0/P1/P2/P3 mission boundaries. Existing `decision_engine.py`, `priority_selector.py`, registry and event ledger remain authoritative. The native C++ migration draft PR is independent and remains low priority.
