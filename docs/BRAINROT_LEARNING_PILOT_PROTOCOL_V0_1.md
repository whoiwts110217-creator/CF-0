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
