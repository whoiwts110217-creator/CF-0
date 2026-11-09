# Brainrot → Brainpower v0.3 — scoring and validity gate (November 9, 2026)

**Identity:** `CF-EXP-GAME-LEARN-001`, related `CF-CORE`, `FIN-09`, `RES-04`; [UCC-001](../../docs/UNIVERSAL_CONTINUITY_CONTRACT.md) · [pilot protocol](../../docs/BRAINROT_LEARNING_PILOT_PROTOCOL_V0_1.md).

**State: DRAFT — NOT INDEPENDENTLY REVIEWED.** This is an **internal design audit**, not an external expert opinion, participant study, calibrated instrument or proof that playful presentation improves memory. No data collected. No change to the live Mission Control lab, AUTO-08, HP, financial state or CF-200 registry.

## What was fixed, and what remains unfixable without evidence

| Earlier v0.1/v0.2 problem | Concrete v0.3 change | Remaining scientific limit |
|---|---|---|
| 50% guessing on a TRUE/FALSE answer | Replaced selection with two short explanations: warranted conclusion **and** its evidence justification | A respondent can still guess or memorize public examples; open responses increase scorer subjectivity |
| Four dichotomous answers per wave (0–4) | Four two-facet tasks, max 8 points per complete wave | More score points **do not automatically increase reliability** or eliminate ceiling effects |
| Wording pattern clues and nearly repeated scenarios | New contexts with explicit evidence and mixed supported/unsupported claims | Content family stays the same by design; equal item difficulty and construct transfer are **not established** |
| Unspecified grading of subjective answers | Per-item target conclusion, evidence criteria, unacceptable categorical claims, and a two-facet 0/1/2 rubric | Requires independent content and bias review, training, double rating, agreement monitoring and adjudication |
| Public answer keys | Development key stays visibly labelled public, **never used as a secret study key** | Real study would need separately version-locked private materials and independent administration |
| Proposed 48-hour outcome | Explicit later, separately timed 36–60-hour phase | No actual participants, allocation, retention results, follow-up rates or attrition data |

## Two-facet development rubric (manual only)

For each item, assess the two components **independently**:
- **Conclusion (0 or 1):** one point if it states the warranted inference without overstating the available evidence.
- **Evidence (0 or 1):** one point if it identifies the concrete observation, missing verification, or counterexample that makes the inference warranted. Do not give this point for an empty restatement of the conclusion.

Sum yields **0, 1 or 2 per item**. A complete four-item wave yields **0–8**. A completely blank answer is missing, not a confirmed zero. A partially answered item remains incomplete for scoring policy purposes; if a future protocol uses partial scores, define the rule **before** data collection and report it separately.

### Synthetic rater calibration examples (not real responses)

| Illustrative item | Invented response | Expected developmental score | Why |
|---|---|---|---|
| `B3-EXEC` | “The laptop definitely ran the job. The server said queued.” | 0/2 | Unsupported local-execution conclusion; queue evidence doesn't prove execution |
| `B3-EXEC` | “The server acknowledged the request, but the laptop run is unverified.” | 1/2 | Warranted conclusion only; no specific missing local-run record identified |
| `B3-EXEC` | “The server acknowledged the request; unattended execution remains unverified because no laptop scheduler or wrapper result is linked to it.” | 2/2 | Both warranted conclusion and specific attribution gap |
| `D3-PROOF` | “The all-loads prediction fails: one permitted load caused structural failure.” | 2/2 | Valid universal-claim conclusion with an actual counterexample |
| `I3-FUND` | “The contract is signed and payment is pending; I can't call the cash received until bank settlement is confirmed.” | 2/2 | Proper evidence state and missing confirmation |

**Important:** These are judgment examples, not a verified automatic grader. Several responses are borderline (e.g. “A receipt isn't proof” may be only a conclusion or may imply a reason). Independent judges must decide whether the rubric can be applied consistently, revise explicit anchors and record each dispute **before** a trial. Don't use an LLM to grade participant answers automatically and call the scores objective.

## Planned rater-quality gate — must actually be completed

1. Have an **independent subject-matter reviewer** check all 12 situations for factual correctness, unnecessary context, cultural accessibility, whether both points are distinguishable, and whether accepting multiple correct explanations is reasonable.
2. Conduct cognitive interviews and readability/accessibility checks, with separately authorized consenting people. Record whether people understand the two requested response parts. No such interview has happened.
3. Prepare **private, version-locked forms and rubrics** not published with the answer key. Keep a public description of the method without leaking the keyed items.
4. Calibrate at least two independent human raters on **separately developed example responses**, then blind them to the teaching condition and, where possible, timepoint. Score independently; calculate exact agreement and a suitable chance-corrected or ordinal measure where data permit. Define adjudication and retraining rules before seeing results.
5. Compare item difficulty, discriminatory power and attrition across baseline, immediate and delayed forms. **Equal topic count or equal rubric point totals does not make forms interchangeable.** Revisit primary outcome definition, because v0.3 changes the response format and the scale; do not mix scores with v0.1/v0.2.
6. Obtain an explicit owner decision and informed consent/data-handling approval before recruitment, assignment, responses, delayed reminders, external contact or claims of efficacy. Follow applicable ethics requirements for a real study.

## Evidence and references

Design guidance: [ETS Best Practices for Constructed-Response Scoring](https://onlinelibrary.wiley.com/doi/full/10.1002/ets2.12358) emphasizes alignment between the task, scoring rubric, rater training and documented validity evidence, including independent review and fairness; [Buros testing program standards](https://buros.org/sites/unl.edu.cehs.educational-psychology.buros/files/media/file/Buros_Standards_for_Accreditation_of_Testing_Programs_revised2017.pdf) require comparability across forms to be evaluated rather than assumed. These sources motivate procedural safeguards; **they do not validate this specific CF-0 assessment**.

## Rollback and next action

Maintain untouched [v0.1](ASSESSMENT_WORKSHEET_DRAFT_V0_1.md) and [v0.2](ASSESSMENT_WORKSHEET_DRAFT_V0_2.md) originals, then this alternative [v0.3 worksheet](ASSESSMENT_WORKSHEET_DRAFT_V0_3.md) and [development rubric](ASSESSMENT_RUBRIC_DRAFT_V0_3.json). Revert v0.3 alone if the constructed-response burden is unacceptable, without changing the published mission UI or the existing research findings. **Next:** send the 12-item rubric for an independent critique, get adjudication/reliability evidence, and only then decide whether to seek permission to run a trial.
