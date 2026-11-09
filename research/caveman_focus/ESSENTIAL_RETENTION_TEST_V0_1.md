# Caveman Focus — Essential Retention Test (ERT) v0.1

**Status:** Public, falsifiable method proposal. Not an established theorem, validated psychological instrument, or verified CF-200 work order.  
**Date:** 2026-11-09  
**Related:** [Independent Criticism Protocol](../../docs/INDEPENDENT_CRITICISM_PROTOCOL.md)

## Central problem

“Simplify complexity without losing essentials” is a goal, not yet an operational guarantee. A simplification is **decision-safe relative to a specified task** only if it preserves the information needed to reach the same warranted decision under the relevant plausible alternatives. An essential may change when the task changes.

## Input and output contract

Before simplifying, record:

- **Question Q:** the exact decision or explanation being requested.
- **Source S:** the complete accessible evidence, with provenance and uncertainty.
- **Decision rule D:** what observations would change the answer, including safety constraints.
- **Context C:** audience, stakes, and reasonable alternatives.
- **Candidate summary M:** the proposed simplified explanation.
- **Loss ledger L:** omitted facts, assumptions, confidence, and possible consequences.

Output a decision with an uncertainty label, not merely a short slogan.

## Six-step Essential Retention Test

1. **Freeze the question.** Specify Q and D before choosing what to omit. If D is unknown, label the result exploratory.
2. **List candidate essentials.** Identify causal constraints, exceptions, counterexamples, boundary conditions, source limitations and quantities that could change D.
3. **Compress.** Produce M and explicitly list at least the highest-risk omissions in L.
4. **Adversarial reversal.** For each omitted fact f, ask: is there a plausible case consistent with M where knowing f changes the justified decision or its confidence? If yes, restore f or clearly flag the summary as unsafe for that decision.
5. **Independent reconstruction.** Give M alone to another reader; ask them to state the decision, assumptions and uncertainty. Compare with an assessor using S. Record disagreements, not only agreement.
6. **Revise or refuse compression.** Accept only for Q and C if critical reversals are absent under the tested cases. Otherwise add the missing essentials or say that the question cannot safely be simplified yet.

**Important:** No finite set of checks proves that all future counterexamples have been excluded. Passing is bounded to the question, cases, sources and reviewers tested.

## Worked examples — illustrative, not empirical results

### Example A: Weather and driving

**Question:** Should a person drive a route tonight?  
**Fuller context:** Rain is forecast; one route has a flood warning and a low-water crossing; an alternative route is available.  
**Unsafe simplification:** “It might rain, so drive carefully.”  
**Omitted essential:** The specific flood warning and crossing.  
**Reversal:** A reader could reasonably choose the hazardous route after seeing only the summary.  
**Repair:** “Avoid the flood-warning route and its low-water crossing; check current official conditions and use the alternative if safe.”  
**Result:** Illustrative failure of compression; not a real-time weather or route recommendation.

### Example B: Software CI

**Question:** Is an HP relay proven to run unattended?  
**Fuller context:** CI passes, a public receipt matches a command, and a Windows task start is observed, but exact receipt-to-scheduled-wrapper attribution is missing.  
**Unsafe simplification:** “Automation passed all tests; unattended operation is verified.”  
**Omitted essential:** The unproven attribution.  
**Repair:** “Source-level tests passed and manual/public round trips have evidence; unattended attribution remains open.”  
**Result:** Demonstrates how a missing qualification changes the claim.

### Example C: Donations

**Question:** Has a project earned money?  
**Fuller context:** A donation page is public, with no independently verified contribution.  
**Unsafe simplification:** “The fundraising campaign is working.”  
**Omitted essential:** No verified payment receipt or measured conversion.  
**Repair:** “The campaign is published; verified income has not been established.”  
**Result:** Distinguishes publication from financial outcomes.

## Scoring rubric for independent reviewers

Score each dimension 0, 1 or 2, using a frozen reference answer:

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Decision-critical facts | Material fact missing | Partial/ambiguous | All identified material facts retained |
| Counterexample handling | Ignores reversal | Flags but not resolves | Correctly restores or qualifies |
| Uncertainty calibration | Unsupported certainty | Partial limits | Limits and evidence clearly stated |
| Reconstruction | Reader reaches unsafe decision | Mixed | Reader reaches warranted bounded decision |
| Traceability | No source/loss ledger | Incomplete | Sources and high-risk omissions recorded |

**Total:** 0–10. A high score is not sufficient if a **critical reversal** is present. Predefine the assessor, reference answer, and which reversals count as critical before collecting results. Report inter-rater agreement, not just average score.

## Comparator and failure criteria

Compare ERT against (a) an ordinary concise summary and (b) a standard critical-thinking checklist. Use identical tasks and equivalent time budgets. Randomize instruction order or assignment, blind graders where practical, and preregister the primary outcome: **fraction of cases with a critical decision reversal**. Secondary outcomes: completion time, word count, factual accuracy, confidence calibration and reviewer agreement.

**Reject or narrow the claim** if ERT increases critical reversals, fails to reduce them against a fair comparator, or imposes disproportionate cost without measurable benefit. A zero-reversal pilot does not prove universal safety.

## Explicit limitations

- The definition of “plausible” and “decision-critical” depends on stakes, domain and evidence; experts may disagree.
- No algorithm can guarantee retention of every unknown essential from incomplete source data.
- More words do not automatically mean more accuracy, and shorter outputs are not inherently worse.
- The four-stage Caveman Focus sequence overlaps existing reasoning methods. ERT is a **proposed operational extension**, not a claim of mathematical or scientific originality.
- High-stakes medical, legal, safety and financial decisions require domain expertise and authoritative evidence; this protocol does not substitute for them.

## Reproducible review record

For each case publish a redacted record with: `case_id`, `Q`, `source_reference`, `D`, `M`, `loss_ledger`, `adversarial_reversal`, `reviewer_decision`, `reference_decision`, `scores`, `protocol_deviations`, and `date`. Do not include private participant information without consent.

**Next gate:** Freeze a diverse case set and reference decisions, then obtain independent blind scoring. Until then, the ERT is an auditable proposal, not an independently proven improvement.
