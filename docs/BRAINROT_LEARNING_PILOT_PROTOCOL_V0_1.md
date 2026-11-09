# Brainrot → Brainpower — optional learning evaluation protocol v0.1

**Stable project:** `CF-EXP-GAME-LEARN-001`; this is an evaluation artifact of the **existing** pilot, not an additional recovered project. **Continuity:** [UCC-001](UNIVERSAL_CONTINUITY_CONTRACT.md) · [Pilot source/status](BRAINROT_TO_BRAINPOWER_2026-11-09.md) · [GitHub Pages learning lab](https://whoiwts110217-creator.github.io/CF-0/mission-control/#learning-lab).

**Status:** preregistration *draft*, not an active study. **Owner request:** Nov 9, 2026: make broadly mainstream video-game humor useful through Caveman Focus and preserve continuity for every project. **Parents:** `FIN-09`, `CF-CORE`, `RES-04`. **Permission:** public-safe source design only; no unsanctioned recruitment, posting, payment, reminders, telemetry, or collection of private participant data.

## The testable claim

Game-style attention hooks improve **recall and transfer of verified evidence boundaries** compared with a plain, non-game explanation presenting the *same content*. Research on gamification and practice testing motivates this hypothesis but does not establish it for this implementation.

- **Condition A, playful:** short game mission headline, prediction, source explanation, remix (new-scenario application).
- **Condition B, plain:** neutral headline with the **same claims, correct answers, evidence, time allotment and remix question**. No added content or extra practice in either arm.
- **Primary outcome:** proportion correct on four **newly worded** transfer questions on an optional delayed retest (roughly 48 hours after the lesson).
- **Secondary outcomes:** immediate novel-scenario transfer accuracy, quiz completion, voluntary helpfulness rating and dropout; do not optimize for watch time, likes, repeated scrolling or emotional pressure.

## Small pilot — only if separately authorized

1. Enroll approximately 10–20 consenting adults (18+) who are comfortable with a short online learning experiment; state explicitly that the format is experimental and optional.
2. Assign conditions A/B in advance by simple randomized order, preserve allocation procedure and prevent switching after viewing the questions. This requires an actual plain version, **which is not yet implemented**.
3. Give identical short baseline questions before showing either lesson. Use new equivalent prompts for the immediate and delayed transfer; do not copy the original in-lesson answers as the outcome measure.
4. Keep the 4 teaching subjects fixed: public HP receipt attribution, grant/payment distinctions, mathematical finite versus universal proof, and event/continuity provenance.
5. For delayed recall, permit voluntary return through a dedicated neutral page after about 48 hours; no push notifications or tracking cookies by default. A participant's choice not to return is attrition, not a wrong answer.
6. Keep trial responses private, minimal and consent-based; publish only aggregate counts and uncertainty, never raw respondent identifying information or chat histories. No collection is occurring in the existing Mission Control page.
7. Report sample sizes by arm, completion and attrition, exact test wording and answer keys, confidence intervals where appropriate, and all departures from the plan.

## Decision thresholds and disconfirming evidence

With a sample this small, even a favorable score is a **pilot signal**, not a causal proof or broad population result. Advance only if the gameful format is usable, does not degrade factual accuracy, and the delayed-transfer estimate is at least plausibly better than the neutral version. If retention is unchanged, engagement rises but recall falls, or attrition is greater, document that result rather than inventing success.

**Stop:** if the feature becomes a manipulative infinite feed, encourages spending, obscures evidence labels, needs private account permissions, or attempts to treat quiz success as real work-order / money verification.

## Acceptance and next step

**Source-stage acceptance:** paired remixes exist, true/false keys vary, all prompts source-link through UCC-001, feature is opt-in and no telemetry or autonomous control exists. [Source tests](../automation_200/mission_control/tests/gameful.test.mjs) at [CI run 42663949373](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42663949373) passed; [GitHub Pages deploy 42663949334](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42663949334) succeeded. This verifies source/build, not browser interaction or efficacy.

**Next executable project task:** add a privacy-safe *plain vs playful* selection in the same dashboard, keeping exact educational content/answer keys fixed, and separately test the browser interaction. **Rollback:** revert only the future optional comparison UI; retain the existing gameful quiz and source history.

## References

- Sailer & Homner (2020), [The Gamification of Learning: a Meta-analysis](https://doi.org/10.1007/s10648-019-09498-w) — evidence for gamification in studied educational contexts; does not validate this pilot.
- Dunlosky et al. (2013), [Improving Students' Learning With Effective Learning Techniques](https://doi.org/10.1177/1529100612453266) — supports practice testing and distributed practice.
- Ebster et al. (2026), [Taming the endless scroll? A systematic literature review](https://pubmed.ncbi.nlm.nih.gov/42287412/) — mainly observational associations about intensive short-form media exposure in youth, not proof that short-form humor is itself harmful or beneficial.


## Dated implementation addendum — November 9, 2026 (v0.3)

The earlier planning statement "plain version not yet implemented" described the state when this protocol was written. An **owner-selectable neutral/Playful demo implementation now exists** in [Mission Control](https://whoiwts110217-creator.github.io/CF-0/mission-control/#learning-lab); both modes use the same factual questions, explanation, answer keys and sources. [Pure presentation data](../automation_200/mission_control/dist/gameful-modes.mjs) · [mode UI](../automation_200/mission_control/dist/gameful-ui.mjs).

**Critically, selection is self-chosen, not randomized.** It cannot estimate an effect of humor on learning. The public page does not recruit people, allocate study conditions, collect quiz results, or verify an actual 48-hour return. Future authorized research must implement independent random allocation and consent outside this self-selected public demonstration. This change does not amend the outcome measures in the protocol or retroactively claim study enrollment.


## Dated assessment-instrument draft — November 9, 2026 (v0.1)

**Research instruments prepared, no participants:** [three-wave participant-facing worksheet](../research/gameful_learning/ASSESSMENT_WORKSHEET_DRAFT_V0_1.md) and [separate development answer key with per-item explanations/source links](../research/gameful_learning/ASSESSMENT_KEY_DRAFT_V0_1.json). Both belong to existing `CF-EXP-GAME-LEARN-001` and its `CF-CORE`, `FIN-09`, `RES-04` links, not to a new recovered project. They cover four baseline, four immediate transfer and four delayed novel scenarios, one from each of the four teaching subjects, with two TRUE and two FALSE answer keys per wave.

**Proposed timing:** baseline before lesson, immediate assessment after the identical lesson, and a genuinely separate delayed test 36–60 hours later (roughly 48 hours). An item re-read or script execution on the same day is **not** a delayed retest. Score each wave 0–4; the protocol's primary comparison remains delayed-wave performance between independently randomized, consenting Playful and Plain arms, with recruitment denominators, attrition and uncertainty. Do not silently convert missing follow-ups into wrong answers.

**Validity limits:** short binary judgments can be guessed and may have ceiling effects; questions need blinded expert review for construct alignment and difficulty. The answer key is in a **public development repository**, so these materials are **not a blinded study packet** and could be contaminated if participants consult it. Before any real trial, separate keys, assign conditions independently, preregister intended exclusions, review privacy/consent and response handling, and ensure each participant has equal content exposure and no feedback leakage. The existing public demo lets users choose the mode and therefore cannot estimate a causal effect.

**Engineering evidence:** [assessment-draft integrity tests](../automation_200/mission_control/tests/assessment-draft.test.mjs) check 12 unique items, one per topic per wave, balanced answers, exact worksheet/key text and canonical source linkage. The first CI run [42682928501](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42682928501) failed on an over-specific *test wording* check; [commit `0a5af7d`](https://github.com/whoiwts110217-creator/CF-0/commit/0a5af7df9c2b0c68b06a15212fbd1ac575581cf5) corrected it. [Rerun 42683004670](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42683004670) passed; [website workflow 42683004678](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42683004678) also succeeded. This is source verification only and **not evidence of learning or delayed retention**.

**No operational changes:** neither the assessment files nor the test modify the public quiz, HP relay, signed-in ChatGPT, P0 AUTO-08, funding, scheduled tasks, registration, data collection or the CF-200 registry. Roll back the worksheet, key and test as a matched draft set if an expert identifies invalid or unanswerable items; preserve all source history and failed results. The next research decision is independent content validity review before a separately authorized, consent-based comparison.


## Dated internal critique and candidate instrument v0.2 — November 9, 2026

An **internal adversarial item review** identified serious limitations of the original public 12-item instrument; it is **not external independent validation**. [Review findings and evidence table](../research/gameful_learning/ASSESSMENT_ITEM_REVIEW_2026-11-09.md) flag mixed yes/no question stems paired with TRUE/FALSE response instructions, similar baseline/delayed questions, easily spotted qualifying cues, identical baseline and delayed answer patterns in v0.1, a four-binary-item guessing ceiling, non-equated wave difficulty and public answer-key leakage.

**Preserved v0.1; new revision is only a candidate:** [v0.2 assessment worksheet](../research/gameful_learning/ASSESSMENT_WORKSHEET_DRAFT_V0_2.md) · [v0.2 development key](../research/gameful_learning/ASSESSMENT_KEY_DRAFT_V0_2.json). The 12 v0.2 items use declarative statements, rotate topic/context order, preserve one evidence-boundary topic per wave and use a different balanced key order per phase. Their appearance and word choices were checked; **parallel form equivalence, item difficulty, accessibility with real participants, causal efficacy, and validity are not established**. Both versions and public development keys remain available in Git history; **neither is a secure blinded instrument**.

[Version-locked source integrity tests](../automation_200/mission_control/tests/assessment-v02.test.mjs) compare the candidate worksheet/key, item IDs, correct topic-source links, declarative response format, key distribution, repeated wording and explicit no-collection status. [GitHub Actions CI 42686167379](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42686167379) **passed** at source commit `ca476bf0f2263796e5ee2e495bbbcd71c8a87831` (50 regular Node source tests plus three standalone checks and successful responsive browser test); [website workflow 42686167089](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42686167089) also succeeded. An initial run [42685921786](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42685921786) failed because the draft review omitted a literal “50%” expected by a new integrity assertion; the [review correction `b806af0`](https://github.com/whoiwts110217-creator/CF-0/commit/b806af0cd679daf968532ea4189cc9587b7e0b91) made the guessing limitation explicit and the passing rerun retains this failure history.

**Study status unchanged:** no randomized allocation, recruited/consenting participants, live quiz collection, response uploads, actual 48-hour return, independent item review, privacy approval or claims of better learning. To progress, obtain *independent* item review/cognitive interviews and evaluate form difficulty, then separately approve study consent, allocation, private key handling, privacy retention and delayed measurement. Preserve the original pilot outcome definitions or explicitly preregister any intended changes **before** data collection. The public Mission Control quiz, CF-200 ledger, HP and AUTO-08 controls and financial state were not modified.


## Constructed-response alternative v0.3 — November 9, 2026

**Change in instrument design, not a study outcome.** The original v0.1 and v0.2 TRUE/FALSE worksheets were retained unchanged. A separate [v0.3 constructed-response worksheet](../research/gameful_learning/ASSESSMENT_WORKSHEET_DRAFT_V0_3.md), [public development rubric](../research/gameful_learning/ASSESSMENT_RUBRIC_DRAFT_V0_3.json), and [scoring/validity gate](../research/gameful_learning/ASSESSMENT_SCORING_REVIEW_V0_3.md) now ask for **(1) the evidence-supported conclusion and (2) the precise reason or missing verification** in each scenario.

The proposed per-item scale is **0–2 points** (one point per correctly demonstrated facet), and the full four-scenario wave spans **0–8**, rather than the earlier 0–4 binary measure. This is a **new alternative outcome specification**, not a retroactive change to any enrolled study: **no study has started**. Before any enrollment, the research owner must select and preregister which outcome and scale will be primary. No raw participant scores, delayed visits, recruitment or collection were created.

**Why this is an improvement:** it demands articulated reasoning rather than a single binary guess and offers concrete scoring anchors. **What remains:** subjective human grading, untested inter-rater agreement, calibration workload, public answer/rubric leakage, possible unequal form difficulty, limited topic coverage, reading/language accessibility and real delayed follow-up. The scale has more points but **is not thereby validated or necessarily more reliable**. Future human raters should be independently trained and blinded to the teaching condition wherever practical; document agreement and adjudication before drawing conclusions. Independent item review and bias/accessibility checking are required.

The [new source-only integrity test](../automation_200/mission_control/tests/assessment-v03.test.mjs) checks the three-wave scenario/rubric/worksheet consistency, without trying to grade natural-language answers or collect data. Existing Mission Control Plain/Playful behavior, account/HP/AUTO-08 permissions, financial state, CF-200 registry and user data remain untouched. **Rollback:** remove only the v0.3 candidate with a recorded decision; keep v0.1/v0.2 and failed-test history. The key remains **PUBLIC DEVELOPMENT MATERIAL**, not a private blind key.


## Ready-for-review packet — November 9, 2026 (no external validation yet)

The [independent-review packet](../research/gameful_learning/INDEPENDENT_REVIEW_PACKET_V0_3.md) now gives a 12-item, item-by-item review sheet for factual correctness, construct validity, two-facet scoring separability, alternative acceptable answers, fairness/readability and cross-wave comparability. This packet is **prepared, not submitted or reviewed**. It links the unchanged public [v0.3 worksheet](../research/gameful_learning/ASSESSMENT_WORKSHEET_DRAFT_V0_3.md), [rubric](../research/gameful_learning/ASSESSMENT_RUBRIC_DRAFT_V0_3.json), historical versions and [scoring limitations](../research/gameful_learning/ASSESSMENT_SCORING_REVIEW_V0_3.md).

An [offline, pure arithmetic helper](../research/gameful_learning/rater_agreement.mjs) accepts two raters' independently chosen *binary conclusion/evidence facet labels*, not raw text. It reports raw facet and total-score exact agreement, facet-level Cohen's kappa when defined, and disagreement identifiers. Missing or malformed ratings are rejected instead of silently scored zero; constant-category kappa is explicitly undefined. The helper **does not read or automatically grade writing, retain participant data, contact a person, collect study results or estimate learning effects**. [Synthetic-source tests](../automation_200/mission_control/tests/assessment-agreement.test.mjs) and [packet coverage tests](../automation_200/mission_control/tests/assessment-review-packet.test.mjs) are part of the existing CI workflow.

[Mission Control test run 42689599459](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42689599459) **passed** on source commit `d761edbf0da6a4cd5342b577fa50f12658ca6189`: 61 regular Node tests, 3 standalone tests and the existing browser/accessibility checks. This verifies arithmetic and document consistency, **not human scoring reliability or external approval**.

External reviewer invitation, paid engagement, unsolicited outreach or sharing personal response data was **not** performed or approved. For a future authorized study, obtain independent signed review decisions and cross-form calibration before locking the primary outcome, consent plan, key custody and genuinely delayed data-collection method. The user need not manually copy prompts for this development work; no owner change to AUTO-08, HP, finances, project identities or the authoritative CF-200 register was made.


## Public reviewer route research — November 9, 2026 (no external contacts)

A bounded [independent-review contact plan](../research/gameful_learning/REVIEWER_OUTREACH_PLAN_DRAFT_V0_1.md) and [machine-readable, source-linked shortlist](../research/gameful_learning/INDEPENDENT_REVIEW_CONTACT_CANDIDATES_V0_1.json) were prepared as a continuation of the still-pending [12-item reviewer packet](../research/gameful_learning/INDEPENDENT_REVIEW_PACKET_V0_3.md). **No actual contact or independent review has been initiated or completed.** Three contact routes were checked using official public service pages, with explicit eligibility/price uncertainty: Ohio State CETE assessment consultations, Buros psychometric **consulting** (not Buros's standard Mental Measurements Yearbook review), and the Center for Assessment / NCIEA. An [NCME educational-measurement programs directory](https://ncme.org/students/graduate-programs/) is included only as an expertise-discovery resource, not a promised reviewing service. University teaching centers with affiliation requirements were not presented as available to an independent owner.

The unsent inquiry asks whether a limited pre-study 12-item/rubric critique is within scope, whether any no-cost initial guidance/referral is offered, and what fees, conflicts or minimum deliverables apply. **Nothing is free or available until verified.** The official contact form that requests identifying information was not submitted. [PCA-003](../automation_200/PROMPT_CHANGE_BIN.md) remains the gate for new outbound messages; expenses require their own explicit owner-approved budget. No participant data, personal chats, private credentials or commercial commitments were distributed.

[Source-only candidate/permission tests](../automation_200/mission_control/tests/reviewer-candidates.test.mjs) and [GitHub Actions run 42691780975](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42691780975) passed: 63 Node source tests / 0 failures, four standalone checks, and retained Chromium/accessibility tests. This establishes only artifact integrity, not reviewers' acceptance or research quality. The next real action—**one individually authorized scope inquiry**—requires an explicit owner decision identifying recipient/limits, then actual response evidence before the state can advance from `outreach_not_sent`.

