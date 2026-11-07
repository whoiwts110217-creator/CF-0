# Dreamkiller — Chapter One Adversarial Stress Audit
**Audit ID:** DK-STRESS-CH01-001 · **Date:** November 7, 2026  
**Creator/developer:** David Smith  
**Designated owner/intended beneficiary:** Kiara Lynn Rose Smith (legal transfer not verified)  
**Evidence class:** Python reference-model stress test, NOT a Game Boy ROM or physical iPhone test.

## Verified tests

- [Final passing CI: 28/28 checks](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42408145018), source fix [80d6300](https://github.com/whoiwts110217-creator/CF-0/commit/80d6300494cdab56a37eb06bfe2bbc0ceb3c34a9).
- 72 distinct modeled outcome combinations: Pip (3) × fruit (2) × watergate (3) × rescue (4). These now carry distinct **reference states**, not just 72 identical map checks.
- 38,400 randomized reference actions (96 deterministic seeds × 400 actions), periodically checking event order, inventory and object identity, access, and reference state save/restore.
- Four mutation probes detected a damaged B-001 route, duplicated sign identity, dangling map exit, and incorrect creator attribution.
- Closed and open cave entrance phases, B-001 repeatability, sign marking, water conservation, fruit harvest without magical seed reappearance, P-001 chronology, and reference history retention after a hypothetical later Road repair were also exercised.

## A defect was actually found and fixed

**BUG-R01: 'rescue neither' could be followed by 'rescue both'.** An empty escort list looked like no decision had been made. It was possible to rewrite a completed choice, including after a reference save-and-restore.

Two new regression checks **failed** in [the adversarial pre-fix run](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42408090856) (26/28 passed). A source repair added a persistent **rescue_decided** flag and asserted no more than one choice event per encounter. The same checks and all others then passed in [the corrected run](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42408145018). This was a **real reference simulator defect**, not a detected Game Boy hardware defect.

A future second rescue attempt should become a new **event/episode ID** if designed; it must not overwrite the old decision.

## Seven open source/design gaps

| ID | Priority | What is missing from the Chapter One source model |
|---|---|---|
| **SPEC-001** | High | The cave's entrance is conditional in the prose but always open in the published JSON map. No explicit phase/gate rule. |
| **SPEC-002** | Critical | No byte-bounded journal / cartridge SRAM save schema, overflow, recovery or migration policy. |
| **SPEC-003** | Medium | No actual water flow quantities, lag, production, or economy calculation. |
| **SPEC-004** | Medium | No exact seeded fruit/larva/planting/loss lifecycle and object transfer rules. |
| **SPEC-005** | High | P-001 doesn't specify whether 'one Cairn' means one named individual, person, identity, or simultaneous exit. |
| **SPEC-006** | High | DK-000 true ending has no executable transition in the Chapter One state model. |
| **TECH-001** | Critical | No playable Dreamkiller Game Boy / GBC ROM exists. The iPhone ROM player contains a diagnostic ROM, not the actual game. |

All seven are deliberately recognized by the source audit routine. The test-only model assumes a four-phase gate (two open phases), a two-unit water budget, a three-tick delivery lag, and fruit stages at ticks 20/40/60. **None of those numeric hypotheses is promoted to established canon.** Passing tests of the hypotheses do not close these gaps.

## Interpretation limits

This work tests an **executable Python model**, not a commercial game, real Game Boy memory effects, native cartridge save files, visual rendering, player experience, or physical iPhone controls. It cannot yet establish perfect continuity or whether the game is fun. The test runner confirms that its own assumed logic is self-consistent for the covered scenarios, and it found one implementation flaw through adversarial testing.

Chapter One remains **PROPOSED** under the [Dreamkiller master constitution](../MASTER_CONCEPT_AND_CONTINUITY_PROMPT.md). Its creator credit remains David Smith; the historical Breach Dungeon Android APK CR-10 is a separate project. No CF-200 work-order completion, HP operations, money or rights to third-party assets are claimed by this creative stress test.

## Next three engineering actions

1. Specify the actual cave-phase rule and the exact quantifier for P-001 in a proposed v0.2 chapter state schema.
2. Specify a realistic Game Boy Color SRAM budget and journal-retention/safe-migration strategy for Day-One observations.
3. Implement and run a small **actual** GB/GBC cartridge demonstrating movement, B-001, one sign object and persistent journal state; then test via the existing iPhone player and a reference emulator.

**Verdict:** 28/28 reference tests passed **after** finding and repairing a repeat-choice defect. Seven important design/implementation gaps remain. Continuity is improved, **not yet perfected**.
