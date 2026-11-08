# CF-0 parallel coordination — integration gate (review only)

Status: **HOLD — DO NOT MERGE / DO NOT DEPLOY**. Draft PR [#17](https://github.com/whoiwts110217-creator/CF-0/pull/17).

## Evidence recorded 2026-11-07

- Main operator, continuity and Work prompts were read in required order before this decision.
- GitHub compare `main...experiment/parallel-coordination-v1`: 51 commits ahead, 167 behind, 21 changed files at inspection. This is a diverged branch, not a safe fast-forward.
- Pull request review query returned **zero submitted reviews**.
- Combined status query for regression commit `e4d27972edd977147165fb7c09af8f4c06cc5189` returned **zero individual statuses**. This is not evidence of CI success or failure.
- The isolated workflow `.github/workflows/parallel-coordination-tests.yml` exists and describes unittest discovery, but a completed passing workflow run for current branch tip has not been independently confirmed.
- The adapter checks public request/receipt consistency only; it does **not** prove physical HP execution, scheduled unattended operation, or task completion.
- The CF-200 registry remains **84/200**; no registry increment is authorized by this review gate.

## Required before integration

1. Obtain full test-suite results for exact branch tip, with commit SHA, runner, exit code, and a passing CI job or independently reproducible equivalent. Fix any failures before proceeding.
2. Reconcile the branch with current main and review all changed paths; no blind merge, no overwrite of newer main.
3. Confirm relay allowlist remains `ping`, `hp_status`, read-only `sidecar_verify`; no arbitrary shell/GUI execution, financial actions, or expanded permissions.
4. Independently verify Windows scheduled invocation and receipt provenance before claiming unattended HP operation.
5. Record review, owner-governed integration decision, and accepted task-specific evidence before changing the CF-200 registry.

No owner clipboard steps are required to maintain this review file. This file itself is advisory and does not grant permissions.
