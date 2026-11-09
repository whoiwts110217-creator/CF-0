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

