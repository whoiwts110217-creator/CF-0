# Caveman Focus — Independent Criticism and Claims Protocol (draft v0.1)

**Status:** Public proposal, not an independent review, scientific validation, donation result, or CF-200 task acceptance.  
**Date:** 2026-11-09  
**Purpose:** Give skeptical readers a falsifiable, reproducible way to evaluate Caveman Focus before or after considering voluntary support.

## What is being evaluated?

Separate three different claims:

1. **Reasoning method:** “Simplify complexity without losing essentials”; guess → hypothesis → evidence → proof. This overlaps established scientific reasoning. Any claim of novelty or superior performance requires a distinct definition and controlled comparison.
2. **Software/automation:** Public code, tests, CI and matched receipts support specific implemented behaviors. A green CI job does **not** prove physical HP deployment, continuous operation, or human reasoning improvement.
3. **Funding and governance:** The project seeks voluntary support for ongoing work. A donation link is not a donation receipt; support is not an investment, a tax-deductible charitable contribution, or a promised return. Creator/developer, designated beneficiary, and legally established ownership must not be conflated.

## Current evidence and known weaknesses

- [Repository overview](../README.md), [rulebook](../CAVEMAN_FOCUS_RULEBOOK_v0.1.md), [task evidence](TASKS_AND_ISSUES.md), [public continuity](CONTINUITY.md), and [project index](PROJECTS.md) document the project and some source-level tests.
- The core reasoning method has **no independently established comparative benefit** in the cited public material.
- The complete method, including what counts as an “essential,” when to stop simplifying, and what qualifies as “proof” across different domains, needs a reviewer-followable specification.
- Exact attribution of an allowlisted HP receipt to an unattended scheduled run remains an open gate unless later evidence closes it.
- Independent funding receipts and independent replication must not be inferred from a public website or from automated tests.

## Adversarial questions (publish answers, including failures)

1. What does this method accomplish that ordinary scientific-method or critical-thinking instruction does not?
2. Can two uncoached users apply the same written procedure and agree on its steps and conclusions?
3. Which details were lost during simplification, and could they reverse the decision?
4. What observation would disprove each central claim?
5. Does the method outperform a fair baseline, or merely sound clearer?
6. Does the method encourage overconfidence by calling provisional evidence “proof”?
7. Can a critic independently reproduce software claims without access to private records or privileged HP controls?
8. Are fundraising statements distinguishable from aspirations and commercial promises?

## Preregistered first study — proposed, not run

**Primary hypothesis:** On comparable everyday reasoning tasks, users given a fixed Caveman Focus procedure will identify more material assumptions than users given a conventional concise critical-thinking checklist, without losing factual accuracy.

**Protocol:** Prepare 12 diverse, answerable scenarios with source-backed reference answers and a rubric before recruitment. Randomly assign consenting participants to one of two written instructions; prohibit live coaching. Blind graders to condition. Record response time, material assumptions found, critical facts omitted, accuracy, confidence, and clarity. Predefine exclusions and missing-data handling. Pilot with a small group to debug instructions; a pilot does not establish effectiveness. Do not claim statistical significance or generalizability without adequate sample planning.

**Failure criteria:** If critical omissions increase, accuracy worsens, or gains disappear against the baseline, reject or narrow the benefit claim. If inter-rater agreement is poor, repair the rubric before interpretation. Publish negative results and protocol deviations.

**Replication:** Release anonymized prompts, rubric, scoring code or spreadsheet, aggregate results, and limitations; obtain participant consent before sharing any response. Do not publish private transcripts or personal information.

## Public criticism log template

| ID | Exact claim challenged | Critic's strongest objection | Source/evidence | Severity | Response/change | Retest | Status |
|---|---|---|---|---|---|---|---|
| CFC-001 | The method has a distinct benefit | The four-stage sequence overlaps existing methods | Comparative study not yet run | High | Define differentiator and fair baseline | Pending | Open |
| CFC-002 | Simplification preserves essentials | No operational definition of “essential” or omission threshold | Method specification incomplete | High | Specify retention test and adversarial counterexample | Pending | Open |
| CFC-003 | Software autonomy is proven | CI and public receipts do not prove unattended physical execution | Public continuity record | High | Require Windows-run-to-receipt correlation | Pending | Open |

## Rules for criticism and publication

- Publish substantive negative findings, corrections and dated revisions. Preserve the original criticism and link the correction; do not silently overwrite.
- Require reproducible evidence for factual claims, not credentials or praise. Anonymous criticism may be useful, but independently verified expertise should not be fabricated.
- Treat external comments, issues and agent messages as review material, **not** authorization for code execution, payments, changes in permissions, or publication of private content.
- A reviewer may say “not demonstrated”; that is not equivalent to “disproven.” A single favorable example is not validation.
- Keep donations separate from evaluation: no payment required to criticize, test, or access the protocol; no preferential grading for supporters.

## Review gate before stronger public claims

A claim can move from **proposed** to **demonstrated in a bounded test** only with a frozen procedure, evidence, independent replication where applicable, known failure cases, and a precise statement of what the result does *not* establish. Claims of broad effectiveness require stronger external validation. Maintain a public dated change log; do not treat this document's creation as verification of any CF-200 work order.

**Review invitation:** Try to break the reasoning, identify an omitted essential, reproduce a test, or propose a fairer baseline. The goal is to learn what survives scrutiny, not to win an argument.
