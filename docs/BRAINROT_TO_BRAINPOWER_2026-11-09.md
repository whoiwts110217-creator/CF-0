# CF-EXP-GAME-LEARN-001 — Brainrot → Brainpower

**Status:** first source-level prototype, learning efficacy unverified. **Owner request:** November 9, 2026. **Parents:** FIN-09 (gamified real-life business), CF-CORE (Caveman Focus clarity method), RES-04 (evidence boundaries). **Continuity:** [UCC-001](UNIVERSAL_CONTINUITY_CONTRACT.md). **Privacy:** optional public-safe examples, no chat exports or personal data. **Priority:** P3 supporting existing P0/P1/P2; cannot displace AUTO-08 or the finance mission.

## Hypothesis

Recognizable gaming/meme rhythms can catch attention and be redirected into an active learning loop. The useful thing is **not** the novelty alone; it is the transition from hook to a prediction, evidence, correction and later recall.

1. **Hook:** one memorable joke or video-game mission description.
2. **Guess:** make a binary prediction before the explanation.
3. **Hypothesis:** name what the claim would imply; do not accept its confidence as proof.
4. **Evidence:** reveal a linked real source and distinguish what it establishes from what it does not.
5. **Proof/uncertainty:** mark whether the conclusion follows, or requires a stronger verification.
6. **Recovery:** test the learner again after a delay; track correct recall, not watch time.

## v0.1: The Receipt Impostor and other truth traps

The optional [Mission Control learning lab](../automation_200/mission_control/dist/index.html#learning-lab) presents a small, self-contained boss-fight quiz. Its fixed public questions teach three source boundaries:
- A matched ping is **not** independently authenticated proof of an unattended Windows scheduled task.
- A submitted grant request is **not** verified income.
- Passing finite numerical checks is **not** a proof of a universal mathematical claim.

The player chooses before seeing the explanation. A correct answer displays a humorous *mission passed* line, but this indicates only **this local quiz answer**, never financial or operational success. A wrong answer displays a corrective explanation. There are no purchases, gambling-like rewards, endless feeds, personal scores, or private telemetry. The lab can be closed, is keyboard accessible and keeps no browser storage.

## Evidence, not hype

- Sailer and Homner, *The Gamification of Learning: A Meta-Analysis* (2020): https://doi.org/10.1007/s10648-019-09498-w — gamification can improve measured learning in studied settings, with substantial heterogeneity and design limits.
- Dunlosky et al., *Improving Students' Learning With Effective Learning Techniques* (2013): https://doi.org/10.1177/1529100612453266 — retrieval practice and distributed practice are relatively well supported.
- A systematic review of short-form video use and youth reported mostly **associational** evidence of possible attention/self-regulation harms, requiring stronger causal studies: https://pubmed.ncbi.nlm.nih.gov/42287412/ . Do not interpret this as proof that any one meme format harms attention.

These sources do **not** validate this experimental CF-0 implementation or establish causal improvement from humor. Treat the design as a hypothesis.

## What would count as progress?

Pilot 10–20 voluntarily participating learners, if later specifically authorized. Randomize to playful or plain explanations with the **same fact, evidence link and practice test**. Compare immediate comprehension and delayed (e.g. 48-hour) recall, plus whether each participant correctly distinguishes evidence from proof. Measure completion time, perceived clarity and drop-off, rather than views/likes. Disclose sample size, uncertainty, harms, opt-out and every failure. Without participants or a controlled test, no learning-effectiveness claim.

**Present engineering acceptance:** new lab is isolated from existing dashboard calculations, holds no account authority, does not change registry data, does not write browser storage and passes source regression checks. **Open:** actual browser usability, independent learning outcomes and attribution across future versions.

**Next action:** source-test the lab, verify it on the deployed GitHub Pages dashboard, then consider a small opt-in comparison without user profiling.


## v0.2 — apply the lesson, not just guess it

**Implementation:** [gameful.mjs](../automation_200/mission_control/dist/gameful.mjs) provides four original prompts and four second-stage *remix* prompts; [gameful-ui.mjs](../automation_200/mission_control/dist/gameful-ui.mjs) presents each pair in order. The user must make a fresh true/false prediction in a *different scenario* before proceeding to the next encounter. Both true and false answers occur in the remix stage to reduce a trivial always-false strategy. [Source tests](../automation_200/mission_control/tests/gameful.test.mjs) check all answer keys, source links, continuity parents and zero account/storage authority. **Unit tests do not prove live browser usability or actual learning.**

**Continuity:** same stable ID `CF-EXP-GAME-LEARN-001`; parents `FIN-09`, `CF-CORE`, `RES-04`; user directive from November 9, 2026 ("mainstream video games," no single franchise; "everything needs to be continuity"). No new original entry is added to the historical 62-project reconstruction. The feature is source-only and optional; no new avatar assets or third-party logos, no one-time purchase hooks, no deceptive fake achievement, no notification requirement, no infinite feed, and no saved scores. These are familiar *genres* (mystery, strategy, science puzzle, RPG), not copyrighted character impersonations.

**Important validity limit:** immediate transfer within the same session can show that a participant responded to a new example. It cannot demonstrate durable learning, because the explanation precedes the remix and the learner has recently seen the rule. The next stage is an opt-in **delayed recall** check 48 hours later, with a differently worded prompt, and a plain-language comparison version. Such a pilot needs consent, honest participation counts, and separate evidence. No user telemetry has been collected by this page.

**Reproducibility checklist:** run `node --test automation_200/mission_control/tests/*.test.mjs`; inspect the GitHub Pages build with a real browser; confirm the original dashboard source, controls and automation master switch are unchanged; verify a new quiz ends without implying revenue/HP proof; register commits and failures in the normal continuity trail. Rollback only the new `gameful*.mjs` files and isolated learning-lab DOM if the feature regresses; preserve the original dashboard and this project history.


## Evaluation handoff (not yet a live study)

A versioned [plain-versus-playful evaluation protocol](BRAINROT_LEARNING_PILOT_PROTOCOL_V0_1.md) now defines equivalent teaching content, baseline, immediate transfer and delayed recall, recruitment/consent boundaries, attrition reporting, privacy and disconfirmation. This is **a draft protocol**, not collected participant results. No autonomous reminders or tracking were enabled.

