# Brainrot → Brainpower — three-wave assessment worksheet (DRAFT v0.1)

**Continuity:** `CF-EXP-GAME-LEARN-001` · related/parents `CF-CORE`, `FIN-09`, `RES-04` · [UCC-001](../../docs/UNIVERSAL_CONTINUITY_CONTRACT.md) · [pilot preregistration draft](../../docs/BRAINROT_LEARNING_PILOT_PROTOCOL_V0_1.md).

**Status:** publicly inspectable research **instrument draft**, **NOT an active study or an invitation to participate**. No response collection, account requirement, tracking, cookie, timer, randomization, reminders or research recruitment is implemented here. The answer key is public in a separate development file, so this worksheet **is not blinded and is not suitable for use as a genuine study without separately controlled materials and consent**.

**Instruction for eventual authorized evaluation:** Respond **TRUE** or **FALSE** for each independent scenario. Do not supply names, contact information, medical details, social accounts, money details or other private information. In a real consented evaluation, the baseline is given before any lesson; the immediate set after the identical Plain/Playful lesson; the delayed set in a separate session about 48 hours later (preregister a 36–60-hour window). No answer feedback or practice between immediate and delayed assessments. Maintain a neutral experience with the same instructions and exposure in both study arms.

## Wave B — baseline (before teaching)

The baseline checks preexisting judgment, not improvement. A study may assess these privately under consent; this public packet does not do so.

| Item | Scenario | TRUE / FALSE |
|---|---|---|
| `B-EXEC` | A cloud dashboard says “request processed” at noon. By itself, does that prove an unattended scheduled task ran on a particular laptop? | ☐ TRUE  ☐ FALSE |
| `B-FUND` | A nonprofit receives a grant award letter but no transfer. Is it correct to record the award and cash received as separate states? | ☐ TRUE  ☐ FALSE |
| `B-PROOF` | A program is claimed to work for every allowed input. One genuine allowed input causes an error. Does that refute the universal claim? | ☐ TRUE  ☐ FALSE |
| `B-LOG` | A team deletes the failed test report as soon as the fix passes. Does deleting it make the change history more reproducible? | ☐ TRUE  ☐ FALSE |

## Wave I — immediate transfer (after teaching)

Use new situations after teaching; do not grade these in front of the participant during the experiment.

| Item | Scenario | TRUE / FALSE |
|---|---|---|
| `I-EXEC` | A verified scheduler entry from a named workstation, its execution-wrapper result and a matching server receipt provide stronger attribution than the server receipt alone. | ☐ TRUE  ☐ FALSE |
| `I-FUND` | A customer presses Pay, but the processor shows the charge as pending. Is that already verified settled cash? | ☐ TRUE  ☐ FALSE |
| `I-PROOF` | An algorithm passes checks on 50,000 inputs. Does this alone prove it works for an unbounded set of possible inputs? | ☐ TRUE  ☐ FALSE |
| `I-LOG` | Linking the old failing test, changed source revision and successful rerun makes it easier for another reviewer to reconstruct a bug fix. | ☐ TRUE  ☐ FALSE |

## Wave D — delayed transfer (36–60 hours after teaching)

This wave must occur in a genuinely later session. Merely opening this document again or running code does not constitute a delayed recall observation.

| Item | Scenario | TRUE / FALSE |
|---|---|---|
| `D-EXEC` | Two chatbots display the same job ID and say “done.” Without a machine-specific run record, is this enough to prove one named computer performed the task unattended? | ☐ TRUE  ☐ FALSE |
| `D-FUND` | A grant is publicly announced, but settlement has not been verified. Should project records distinguish the award from money actually received? | ☐ TRUE  ☐ FALSE |
| `D-PROOF` | A simulation passed thousands of runs, then one valid scenario violates an “always safe” claim. Does that counterexample still refute the universal claim? | ☐ TRUE  ☐ FALSE |
| `D-LOG` | An operator keeps the passing build and removes earlier failures because the problem is fixed. Does this preserve the complete auditable trail? | ☐ TRUE  ☐ FALSE |

## Instrument handling and scoring specification (for a future authorized study)

The companion [development key](ASSESSMENT_KEY_DRAFT_V0_1.json) includes source links, correct answers and rationales. **Never give that key as part of a purportedly blinded administration.** The current public packet makes item leakage possible and must be revised, privately separated and version-locked before any genuine causal study.

Each wave has four items, one per topic, with two correct TRUE and two correct FALSE responses. Score one point per correct answer, zero otherwise; each wave ranges 0–4. Score unknown/blank responses as *missing*, not automatically as wrong; report incompletion and attrition separately. Prespecify how many completed responses are required before an arm score is considered evaluable, rather than changing this after looking at results.

In an eventual authorized randomized evaluation, the **primary descriptive comparison** is mean delayed-wave score for Playful minus Plain, with delayed completion numbers, eligibility denominators, participant attrition, and uncertainty intervals. Separately show baseline and immediate results. Avoid overclaiming a small-sample experiment; a four-binary-item instrument is vulnerable to ceiling effects, guessing, and known-key contamination, and requires expert review/pilot testing before use. **Do not call hypothetical numbers observed results.**

**Next research acceptance:** expert review item validity, difficulty/construct alignment, alternative wording and leaks; then obtain separate authorization for informed consent, independent allocation, privacy-safe response handling, outcome lock, and delayed-session logistics. The existing public Mission Control quiz is a self-selected demo, never randomized and not collecting research responses.

**Version/rollback:** `ASSESSMENT_WORKSHEET_DRAFT_V0_1.md` paired to `ASSESSMENT_KEY_DRAFT_V0_1.json`. Keep both in Git history, including failed tests and corrections; no change to the main game UI or the CF-200 verified-task registry.
