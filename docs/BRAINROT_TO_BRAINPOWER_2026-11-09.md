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


## v0.3 — Plain vs. Playful presentation (November 9)

The original learning lab now supports **two owner-selectable presentation modes**. `Playful` uses familiar game-mission and remix language. `Plain` uses neutral evidence-exercise headings, button labels and success messages. **Both read the same four original questions, four remix questions, answer keys, explanations, takeaways and evidence links** from the pre-existing `gameful.mjs` source.

**Implementation links:** [presentation functions](../automation_200/mission_control/dist/gameful-modes.mjs), [UI mode locking](../automation_200/mission_control/dist/gameful-ui.mjs), [source parity tests](../automation_200/mission_control/tests/gameful.test.mjs), [simulated browser-DOM interaction test](../automation_200/mission_control/tests/gameful-ui-dom.test.mjs), [Mission Control](https://whoiwts110217-creator.github.io/CF-0/mission-control/#learning-lab).

**Design rule:** the user selects a mode *before* opening the exercise. The choice is locked during that run and can be changed after closing/restarting. It is not written to browser storage, sent to a server, or linked to a user. The page does **not** randomize users, count participation or compare outcomes. This is a demonstration and engineering prerequisite for a later consent-based evaluation, **not an experiment demonstrating improvement**.

**Continuity:** still `CF-EXP-GAME-LEARN-001` with related parent records `FIN-09`, `CF-CORE`, `RES-04` under [UCC-001](UNIVERSAL_CONTINUITY_CONTRACT.md). The public `CF-200` verified work-order count and owner permissions are unchanged by this educational feature. New code was added to existing Mission Control without replacing its control center or HP/AUTO-08 functionality.

**Source acceptance, November 9:** [full Mission Control tests](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42666297305) and [GitHub Pages deployment](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42666297295) passed at commit `accfd0cc13ff43442fb31d33d609a7688d5f78a2` after fixing one new test expression. **Open acceptance:** real iPhone/desktop browser interaction, cross-browser accessibility, any durable learning effect, and a properly randomized opt-in evaluation. Revert the mode-specific selector and `gameful-modes.mjs` if it regresses without removing the original v0.2 educational content or the documented chronology.

## Mobile-width Chromium verification — dated November 9

A dedicated [source browser smoke](../automation_200/mission_control/tests/browser_smoke.mjs) now runs the actual learning lab at **390 CSS px width** in headless Chromium with real Tab/Enter keyboard events. [CI run 42668440686](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42668440686) **passed**: 35 source tests and the browser script; laboratory section 19–371px inside a 390px viewport; no document overflow; question and explanation focus survived keyboard-only progression; the automation master switch remained disabled. One earlier failing test run is retained in the [continuity handoff](CONTINUITY.md#november-9--mobile-width-chromium-browser-acceptance-and-keyboard-repair), along with its correction. These engineering outcomes do **not** verify a physical iPhone, Safari, assistive technology on device or long-term learning.

## v0.4 — narrow-phone touch and layout acceptance

The existing [Mission Control learning lab](https://whoiwts110217-creator.github.io/CF-0/mission-control/#learning-lab) has a touch-friendly source change: at least 44×44 CSS pixel targets for quiz buttons/select and evidence links; at least 16px select text; visible keyboard focus. The existing automation inventory's lengthy status labels and badges now wrap on smaller screens, preventing layout expansion without changing controls or their read-only/disconnected status.

[Reproducible Chromium browser check](../automation_200/mission_control/tests/browser_smoke.mjs) at **320, 360, 390, and 430 CSS px** checks no document or lab overflow, touch target dimensions, source-content parity, and keyboard transitions. [Strict CI run 42670072384](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42670072384) passed. Earlier failure/fix chronology and rollback references are in [public continuity](CONTINUITY.md#november-9--brainrot--brainpower-v04-narrow-phone-hardening). Headless Chromium phone-width emulation does **not** verify an actual iPhone Safari or VoiceOver run, nor study outcomes. No activity collection, mode randomization or real-world project achievements were added.


## v0.5 — reading size and system contrast (Nov 9)

The optional [Mission Control lab](https://whoiwts110217-creator.github.io/CF-0/mission-control/#learning-lab) now has a **Larger lesson text** checkbox. It adjusts visible reading size locally while preserving the identical source questions, answer keys, explanations and progress in Plain and Playful modes. It does not store a setting or collect responses. CSS responds to system increased-contrast and forced-colors preferences.

The [read-only hosted browser verification](https://agent.tinyfish.ai/runs/072a04d9-a7a5-4d1f-90b3-c7f0794e5c4f) found the checkbox operational with the original first claim and answer intact, the public workflow source count correctly rendered as 21 (5 scheduled, 16 event/manual), and the master automation switch still disconnected. Published source was displayed as `e3c9c811` during that run. This proves browser observation, **not** iPhone Safari/VoiceOver or a causal learning benefit.

An unrelated stale workflow-count assertion in several CI runs around this change expected 20 workflows after a 21st file existed. Its later source revision corrects that expectation. [Full history, failure status, source SHAs, and rollback](CONTINUITY.md#november-9--brainrot--brainpower-v05-readable-text-and-public-source-count-continuation). Confirm a fresh CI run at the current combined source before calling the whole suite green.


**Verified after the original v0.5 testing caveat:** [GitHub Actions run 42673680552](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42673680552) succeeded on commit `e9882d0f1df8bd0aeeff90d7ab76ea3f6d8cf056` with **43 passing Node tests, zero failures, and a passing headless Chromium mobile-width check**. Its checks included unchanged evidence with enlarged text, four widths, keyboard focus, source inventory, and increased-contrast rendering. Earlier red builds remain part of the [continuity history](CONTINUITY.md#november-9--brainrot--brainpower-v05-readable-text-and-public-source-count-continuation). This is an engineering verification, not an iPhone Safari/VoiceOver or educational efficacy result.

## v0.5.1 — source inventory continuity confirmation

The Learning Lab's v0.5 readability and two presentation modes remain unchanged. A separate iPhone Skill Foundry workflow was added to the same repository; Mission Control's **source inventory is now 22 workflows (5 scheduled, 17 event/manual)** rather than the earlier historical 21. [Inventory commit 1fd4279](https://github.com/whoiwts110217-creator/CF-0/commit/1fd42791938f119995c2bf23f2da3f489ddbf4fd) and [strict actual-file parity test commit 330cc35](https://github.com/whoiwts110217-creator/CF-0/commit/330cc35aa30248a02b4500ce5589ca86421d436f) preserve cross-project continuity without implying an iPhone-native installed program or live account action.

[Full source/Chromium CI](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42674408404) and [Pages deployment](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42674408782) both passed for `330cc35aa302`. [Independent public-browser readback](https://agent.tinyfish.ai/runs/b73eb15b-dbf7-4559-880d-3ebe4d388317) verified 22/5/17, disabled master switch, learning modes and Larger Text with unchanged first question. **Unverified:** physical iPhone Safari, VoiceOver, a randomized learning study and delayed retention. Full source/rollback [continuity entry](CONTINUITY.md#november-9--v051-cross-project-workflow-inventory-reconciliation).


## v0.5.2 — accessibility-tree and optional owner-device guide

[Chromium accessibility-tree checks](../automation_200/mission_control/tests/browser_smoke.mjs) verify that the source-labelled mode selector, Larger Text checkbox, quiz answer buttons, question, explanation/evidence link and DISCONNECTED automation master are discoverable as named browser accessibility nodes. The public lab now contains a collapsed native **Checking this page on iPhone Safari or VoiceOver** disclosure with four optional device-level checks and a clear no-upload/no-telemetry/no-certification boundary. It is informational and does not collect test results.

[GitHub Actions CI 42677698076](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42677698076) and [Pages deployment 42677698440](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42677698440) **passed** on source commit `27b2bc1bf7b1f4f6b382a273dacdba07d1c3216d`. A [read-only hosted browser run](https://agent.tinyfish.ai/runs/3b3dc652-2e9e-4143-9828-c53444ffa192) observed the disclosure opening and closing, 22/5/17 source inventory and disconnected controls on the public page. [Continuity with source commits, evidence limits and rollback](CONTINUITY.md#november-9--brainrot--brainpower-v052-accessibility-tree-and-owner-device-handoff). None of this substitutes for physical iPhone Safari/VoiceOver testing or a retention study.


## v0.6 — From a correct quiz answer to a real evidence-gated task (November 9)

**Trigger:** user reaction to `THE INVISIBLE PAYDAY` showed the prototype's biggest usability failure: it taught that grant submission is not revenue but did not lead to any real task. This is a **design correction**, not a claim of new grant money or live execution.

**Same identity/parents:** `CF-EXP-GAME-LEARN-001`; `FIN-09`, `CF-CORE`, `RES-04` under [UCC-001](UNIVERSAL_CONTINUITY_CONTRACT.md). Keep the four existing mission statements, grading, immediate transfer, Plain/Playful content parity, opt-in presentation and privacy boundary unchanged.

**New behavior:** Completing a second-scenario response reveals a read-only **NEXT: Real-world field brief** containing (1) one concrete suggested project action, (2) the acceptance evidence that would make it count, and (3) a link to the existing public record. Funding specifically requires distinguishing received application, verified award decision and actual payment; a submission is never booked as cash. Other briefs address scheduler/receipt correlation, falsifiable research, and preserved failure/version evidence. The brief resets on the next question or when the mode is restarted.

**Safety and truth:** No buttons that submit applications, send emails, read accounts, change source records, copy private data or claim task completion. This feature generates no donation, execution receipt, verification or new CF-200 work order. All field tasks remain *proposed* until separately performed and accepted through existing authority and evidence channels.

**Engineering acceptance:** [Mission Control source](../automation_200/mission_control/dist/gameful-ui.mjs); [mission definitions](../automation_200/mission_control/dist/gameful.mjs); [source assertions](../automation_200/mission_control/tests/gameful.test.mjs); [DOM interaction regression](../automation_200/mission_control/tests/gameful-ui-dom.test.mjs). Check the `gameful-field-brief` stays hidden until the remix, has a working source link and visible 44px minimum tap target on small screens, is screen-reader-reachable, and disappears on restart. A green CI check supports only code-level acceptance; real iPhone Safari and actual business outcomes still require independent verification.

**Rollback:** revert only the new static field data, learning-lab brief markup/styles, UI reveal/reset and tests. Preserve all previous learning material, original quiz jokes, current evidence links, Mission Control controls, roles and unrelated funding/HP records.

**Next:** independently inspect the deployed public lab and whether an owner can follow the business brief to an actual funding-status entry. Do not fabricate an award or send messages just to pass the game.


## Browser-stage gate regression and full progression — November 9

A new computed-style test revealed an **actual evidence-exposure bug**: the source link could be rendered `display:inline-flex` before the user answered even while it had the `hidden` HTML attribute. [Failing CI 42680515065](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42680515065) is retained. A scoped CSS rule now makes `[hidden]` authoritative inside the optional lab. TRUE/FALSE buttons also carry a description of the *current* question for assistive navigation, updated with the remix claim.

[Passing full source + Chromium CI 42681075971](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42681075971) and [website deployment 42681075732](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42681075732) verified the final code at `305a3ad1a03f158df1e614c4e84d08814ffc8edb`. The test now walks all four topics, all eight answers, gated proposed field-brief reveals and the final completion state, without account actions. The source-only scope remains `CF-EXP-GAME-LEARN-001`; this is neither evidence of delayed educational retention nor physical iPhone VoiceOver certification. [Detailed continuity, SHAs and rollback](CONTINUITY.md#november-9--cf-exp-game-learn-001-v06x-rendered-visibility-and-full-progression-repair).


## Internal item-quality review and v0.2 assessment candidate (November 9)

An [internal adversarial review](../research/gameful_learning/ASSESSMENT_ITEM_REVIEW_2026-11-09.md) found material problems with the original v0.1 assessment instrument: TRUE/FALSE attached to yes/no questions, highly similar question contexts across waves, repeatable public answer-key patterns, clue wording, only four binary items per wave, and no empirical form equivalence or blinded key custody. That review is **not independent expert validation**.

The original [v0.1 worksheet](../research/gameful_learning/ASSESSMENT_WORKSHEET_DRAFT_V0_1.md) and [key](../research/gameful_learning/ASSESSMENT_KEY_DRAFT_V0_1.json) remain unchanged. New separate [v0.2 worksheet](../research/gameful_learning/ASSESSMENT_WORKSHEET_DRAFT_V0_2.md) and [development key](../research/gameful_learning/ASSESSMENT_KEY_DRAFT_V0_2.json) try declarative statements, rotated scenarios and different answer sequences, but remain **unvalidated public drafts**. Both public keys preclude credible blinded administration and do not constitute an actual randomized study.

[Source-integrity tests](../automation_200/mission_control/tests/assessment-v02.test.mjs) and [GitHub Actions run 42686167379](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42686167379) **passed** at commit `ca476bf0f2263796e5ee2e495bbbcd71c8a87831`, including 50 regular Node tests, 3 standalone tests and browser checks; [website deployment 42686167089](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42686167089) succeeded. A prior failed test/document text assertion and its correction remain in [public continuity](CONTINUITY.md#november-9--cf-exp-game-learn-001-adversarial-assessment-review-and-v02-candidate). **No participants, actual delayed responses, income or independent item calibration**. These candidates do not change the published Plain/Playful Mission Control quiz or the higher-priority P0 automation mission.

