# Independent review packet — Brainrot → Brainpower v0.3 (PRE-REVIEW)

**Continuity:** `CF-EXP-GAME-LEARN-001` under [UCC-001](../../docs/UNIVERSAL_CONTINUITY_CONTRACT.md). Related/parent projects: `CF-CORE`, `FIN-09`, `RES-04`.

**Status:** PACKET PREPARED, **NO INDEPENDENT REVIEW COMPLETED OR SOLICITED**. No recruitment, contact, invitation, endorsement, human rating, payment, personal data, or randomized experiment has occurred. The material is public and keyed, **not a secure blinded participant instrument**.

## Purpose and exact materials

This packet lets an independent subject-matter or educational-measurement reviewer critique the **content validity and scoreability** of a draft 12-item assessment. It must *not* be used to claim the Gameful/Plain teaching conditions have an effect; that requires a separately authorized participant study.

- [Participant-style development worksheet (v0.3)](ASSESSMENT_WORKSHEET_DRAFT_V0_3.md): four baseline, four immediate, four delayed scenarios. Respond with a warranted conclusion and a supporting evidence boundary.
- [Public answer and scoring anchors](ASSESSMENT_RUBRIC_DRAFT_V0_3.json): correct inference, acceptable reasons and unacceptable overclaims for every item. This source was read at Git blob `3dc53ef13a49a1df472f49ac035d865d31b7f112`.
- [Internal scoring and validity concerns](ASSESSMENT_SCORING_REVIEW_V0_3.md): synthetic examples and explicitly unresolved construct/bias/difficulty issues.
- [Original v0.1 and v0.2 review](ASSESSMENT_ITEM_REVIEW_2026-11-09.md): prior source failures are preserved, not erased.
- [Technical rater-agreement calculator](rater_agreement.mjs): pure arithmetic on two already human-decided, binary facet scores. **No answer text ingestion, no automated scoring and no external transmission.**

## Review task A — independent item-quality check

Read each item and its scoring reference. For every item, evaluate the following **separately**:

1. **Factual correctness:** Is the proposed conclusion a defensible inference from the described evidence, with no missing assumption or unsupported claim?
2. **Construct fidelity:** Does it measure a transferable evidence-boundary distinction (execution / settled funding / universal mathematical claims / preservation of failed tests) rather than memorized vocabulary?
3. **Two-facet separability:** Can a respondent give a correct conclusion without a valid reason, or a valid reason without a fully stated conclusion? If not, the 0–2 scoring rule may double-count.
4. **Acceptable alternatives:** Would a competent response using different wording or a different legitimate argument be unfairly marked wrong by the current anchors?
5. **Clarity/fairness:** Are reading level, technical jargon, culturally specific references, and English-language load unnecessarily affecting the intended reasoning task?
6. **Form comparability:** Do baseline, immediate, and delayed versions differ in difficulty, hints, or required background knowledge? **A text review can flag but not empirically equate form difficulty.**

**Mark one decision per item:** Retain / Revise / Reject / Unable to judge. For every Revise, Reject, or Unable to judge, record the exact problematic phrase, reason, severity (critical/material/minor), and suggested edit. Any critical ambiguity or unjustified key is a stop for using that item in a trial; this is a proposed editorial rule, not evidence of validation.

| Item ID | Wave | Topic | Reviewer disposition | Issue, severity, proposed revision |
|---|---|---|---|---|
| `B3-EXEC` | baseline | receipt | ☐ Retain ☐ Revise ☐ Reject ☐ Unable to judge | — |
| `B3-FUND` | baseline | funding | ☐ Retain ☐ Revise ☐ Reject ☐ Unable to judge | — |
| `B3-PROOF` | baseline | hypothesis | ☐ Retain ☐ Revise ☐ Reject ☐ Unable to judge | — |
| `B3-CONT` | baseline | continuity | ☐ Retain ☐ Revise ☐ Reject ☐ Unable to judge | — |
| `I3-FUND` | immediate | funding | ☐ Retain ☐ Revise ☐ Reject ☐ Unable to judge | — |
| `I3-EXEC` | immediate | receipt | ☐ Retain ☐ Revise ☐ Reject ☐ Unable to judge | — |
| `I3-CONT` | immediate | continuity | ☐ Retain ☐ Revise ☐ Reject ☐ Unable to judge | — |
| `I3-PROOF` | immediate | hypothesis | ☐ Retain ☐ Revise ☐ Reject ☐ Unable to judge | — |
| `D3-PROOF` | delayed | hypothesis | ☐ Retain ☐ Revise ☐ Reject ☐ Unable to judge | — |
| `D3-EXEC` | delayed | receipt | ☐ Retain ☐ Revise ☐ Reject ☐ Unable to judge | — |
| `D3-CONT` | delayed | continuity | ☐ Retain ☐ Revise ☐ Reject ☐ Unable to judge | — |
| `D3-FUND` | delayed | funding | ☐ Retain ☐ Revise ☐ Reject ☐ Unable to judge | — |

**Additional independent cross-wave finding:** Which two items appear easiest/hardest, and *why*? Does one wave disproportionately demand technical knowledge or longer reading? An ordinal reviewer impression is not an empirical item-difficulty estimate.

## Review task B — blind-to-condition scoring feasibility

The rubric proposes one point for a supported **conclusion** and one for a concrete **reason/evidence**. Ask two independently trained human scorers (not this assistant, not an automated grader) to apply the same locked scoring guide to a separately authored **synthetic calibration sample** with varied correct, partial, contradictory and unconventional-but-valid answers.

- Evaluate each facet as `0` or `1`, not a single global impression; record missing/incomplete responses separately.
- Keep teaching mode and participant identity inaccessible to scorers.
- Compare each rater's facet decisions and total 0–2 scores. Record *all* disagreements; do not quietly change the rubric mid-rating.
- After the independently scored sample, review discrepancies and either clarify anchors or reject the two-facet scoring model. A calibration sample alone does not estimate a population reliability coefficient.
- If future authorized participant data exist, preregister a number of double-scored responses, agreement metrics and decisions on thresholds before inspecting the data. Both observed agreement and chance-corrected statistics should be reported with sample size and limitations.

For **synthetic-only arithmetic demonstration**, the pure `summarizeIndependentFacetRatings` utility accepts records like:

```js
import { summarizeIndependentFacetRatings } from "./rater_agreement.mjs";
const inventedRatings = [
  {id: "FICTION-1", a: {conclusion: 1, evidence: 1},
                   b: {conclusion: 1, evidence: 0}}
];
const report = summarizeIndependentFacetRatings(inventedRatings);
// Report is descriptive. It is NOT a score of the written answer,
// NOT a completed human review, and NOT a study result.
```

Any missing, non-binary, duplicated or ambiguous facet ratings are **rejected rather than silently treated as 0**. Kappa is `null` if the marginal distribution makes it undefined; report the separate observed agreement. The utility does not save files, contact users or parse response text.

## Review decision and evidence gate

The review is **not complete** until an actual qualified reviewer independently returns:

- a date, reviewer role/qualifications and conflicts-of-interest declaration (handle personal details privately, not in a public repo without consent);
- an item-by-item disposition with exact problems and alternative acceptable answers;
- at least one assessment of two-facet scoring ambiguity and possible construct-irrelevant reading/language load;
- a cross-wave comparability critique and recommendation about whether the three forms require more development.

A *second independent score rater* and empirical form/pilot calibration are separate gates. Even two reviewers unanimously agreeing that wording is good does not validate a test or establish that playful learning is better.

**Status to record until then:** `packet_prepared; review_pending; calibration_not_run; participants_0; learning_efficacy_unverified`.

## References and safeguards

The review structure reflects [ETS Best Practices for Constructed-Response Scoring](https://doi.org/10.1002/ets2.12358), which emphasizes task-aligned rubrics, training, rater consistency and fairness; and a [validity framework review](https://pmc.ncbi.nlm.nih.gov/articles/PMC5806296/) distinguishing content, response-process and internal-structure evidence. Neither source validates our instrument.

**Permissions:** No external invitation or outreach was sent. Future requests for expert feedback need explicit approval for specific people/channels. No automated study allocation, consent, data capture, cash commitment, account connector, GitHub master-switch change or HP/AUTO-08 permission is granted by this packet.

**Rollback:** preserve this packet and each linked original; if it becomes inaccurate, commit a corrected packet with a reason, not an erasure. Next authorized action: get a real independent review decision, then revise *only* the flawed item/rubric subset with its source SHA and another source test.
