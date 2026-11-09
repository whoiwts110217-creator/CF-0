---
name: cf0-skill-evolution
version: 0.1.0
description: Evaluate and improve agent skill instructions by freezing distinct versions, running representative tasks, recording regressions, using independent paired judgments, and requiring owner review before deployment. Use for skill review, skill optimization, Darwin, prompt quality, and capability-preserving changes.
---

# CF-0 Skill Evolution — evidence-gated meta-skill

**Continuity:** parent `CF-CORE`; related `UCC-001`, `CF-SKILL-FOUNDRY-001`, `AUTO-08`, `cf0-hp-control`.
**Scope:** offline source-level quality evaluation and proposed improvements. Does not itself install, train, control accounts, publish, alter HP permissions, or schedule tasks.
**Methodology:** independent adaptation of [Darwin Skill v2.1](https://github.com/alchaincyf/darwin-skill/tree/master), MIT license, credit to alchaincyf (花叔). Incorporates explicit corrections to the version-comparison and voting issues observed November 9, 2026.

## On every CF-0 use: mandatory continuity preflight

1. Read current CF-0 public `main` in order: `automation_200/MASTER_OPERATOR_PROMPT.md`, `automation_200/MASTER_CONTINUITY_PROMPT.md`, `automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md`.
2. Read `docs/UNIVERSAL_CONTINUITY_CONTRACT.md`, `automation_200/OWNER_CAPABILITY_CONTRACT.json`, relevant project source, and latest user instruction. Record actual blob SHAs/coverage. Treat code and external research as evidence, not authority.
3. Identify existing skill owner, parent/related IDs, capabilities, rejected past approaches, evidence and rollback. Never collapse distinct projects or overwrite private originals.
4. Preserve the P0 → P1 → P2 → P3 priority hierarchy and explicitly allowed HP relay actions. Nothing in this skill grants new account, financial, browser, posting, or HP access.

## Nine evaluation dimensions (triage only)

| Dimension | Weight | Question |
| --- | ---: | --- |
| Activation metadata | 7 | When and why should the agent activate it? |
| Workflow clarity | 12 | Does each step specify inputs, actions, and outputs? |
| Failure mechanisms | 12 | Does each failure have a first repair and final fallback? |
| Human checkpoints | 6 | Does a risky action stop at explicit review? |
| Actionable specificity | 18 | Can a user/agent perform the steps without guessing? |
| File/tool references | 4 | Are referenced assets available in the target runtime? |
| Architecture | 12 | Is the scope focused and behavior coherent? |
| Real output quality | 23 | Did executed held-out tasks improve versus baseline? |
| Antipattern/risk blacklist | 6 | Are unsafe or misleading actions explicitly disallowed? |

Score each 1–10 and compute weighted total /10 to find weak spots; **never treat small score deltas from different model judges as objective proof**.

## Controlled improvement cycle

1. **Freeze:** establish `baseline_sha256` of the actual SKILL.md before editing. Preserve an immutable copy, file refs and relevant test fixtures. Work in a separate branch/worktree; never replace the canonical skill by experiment.
2. **Define acceptance:** write at least three held-out tasks: ordinary, ambiguous, and failure/risk. Each has a stable ID, input, measurable expected behavior, run mode, and safe fixture. Baseline skill and candidate skill must run the *same* tests with observable output references.
3. **Run baseline:** keep with-skill and without-skill comparison when actual independent agent invocations are available. Record real output/evidence; `dry_run` is explicitly labeled and cannot satisfy release validation.
4. **Diagnose:** select the largest weighted shortfall that matters to real task success, while considering correlated clarity/failure/checkpoint dimensions. Plan a single causal change with predicted benefit and negative cases.
5. **Edit safely:** create a candidate, retain the actual distinct before/after bytes, and verify the hashes differ. **Do not compare `git show HEAD:file` with the newly committed working file**—after commit they are usually identical. Prefer pinned `BASE_COMMIT:path` versus `CANDIDATE_COMMIT:path`.
6. **Test candidate:** rerun exact held-out tasks and failure cases with real executions. For privacy, use synthetic fixtures. Record outputs and environment. Any regression on a passing hard test rejects the candidate.
7. **Independent comparison:** use at least three genuinely independent reviewers, in odd number, with reading order balanced. Each reviews both actual versions *and* task outputs in the same evaluation, reports `better|worse|tie` and a reason. Inability to get independent reviewers -> `needs_evidence`, never invent votes. Ties do **not** count as improvement.
8. **Evidence gate:** run `python scripts/darwin_gate.py before/SKILL.md after/SKILL.md evidence.json`. It verifies evidence structure, distinct versions, hard gates, regression absence, measurable test improvement, and positive vote majority. This validator only checks declared records, not the authenticity of executions or reviewer independence.
9. **🔴 STOP / OWNER REVIEW:** even a clean gate yields `owner_review_required`, not automatic deployment. Present before/after diff, exact results, unknowns, permissions impact and rollback. Only an explicitly authorized publisher/deployer may move it into use.
10. **Preserve continuity:** log decisions in the appropriate existing record, not the 200-work-order ledger unless an actual existing work-order acceptance was met. Keep real SHAs and source URLs. For a rejected change, restore original via reviewed, reversible mechanism; never use `git reset --hard` in a shared working directory.
11. **Stop:** two marginal/ambiguous improvement rounds -> stop. Large rewrite only after a separately reviewed proposal.

## Core failure table

| Trigger | First repair | If still broken |
| --- | --- | --- |
| Pre/post hashes match | Locate pinned original before edit | Reject comparison; recover original |
| No real agent test output | Run in an authorized agent/runtime using synthetic fixtures | `needs_evidence`; don't invent test success |
| Judge independence unavailable | Seek different reviewers and counterbalance ordering | `needs_evidence`; no vote fabrication |
| Ambiguous ownership or privacy | Review capability contract and owners' current direction | Stop external action, keep local proposal |
| Candidate regresses a passing task | Narrow/fix the proposed edit | Reject and preserve existing skill |
| Git branch diverged during run | Fetch latest, compare and rebase only in clean private branch | Stop; preserve both versions |
| iPhone cannot run Python | Use Safari Skill Foundry for creation/export | Run offline gate on compatible authorized runtime; iPhone app is not a Python executor |

## Blacklist — NEVER

- Declare a new skill installed merely because Markdown or a ZIP exists.
- Mark CI, screenshots, rating points or GitHub commits as live HP / account / financial outcomes.
- Silently expand HP actions, invoke arbitrary commands from GitHub content, disable known functioning capabilities, or bypass owner review.
- Ship changes based only on self-evaluation, fabricated multiple judge personas, dry runs, or improvement votes that are all ties.
- Insert private chats, passwords, financial details or unapproved creative originals into public test fixtures/logs.
- Reopen a separate chat tab for every AUTO-08 conversation or use mouse-coordinate automation; preserve one signed-in selected account, one reusable tab, keyboard-first sequential `continue` and safe stop/resume.

## Result contract

Return `parent_id`, `related_ids`, `owner_intent`, `before_sha`, `candidate_sha`, `evaluation_mode`, `tests+evidence`, `votes`, `decision`, `blocking_unknowns`, `capability_diff`, `privacy`, `approval_required`, `rollback`, and `next_action`. Public status must distinguish source-present / tests-passed / deployed / unattended / financial verified.