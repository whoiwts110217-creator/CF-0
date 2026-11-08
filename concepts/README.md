# Caveman Focus — Public Concept Registry

This folder is for owner-directed creative and product **concepts** with explicit status, provenance, and continuity rules. A filed concept is not a finished product, a deployable ROM or proof of commercial success.

| ID | Filed concept | Creator | Present state |
|---|---|---|---|
| CF-CONCEPT-DREAMKILLER-001 | [Dreamkiller / BreachDungeon: The Road That Was Always There](dreamkiller/MASTER_CONCEPT_AND_CONTINUITY_PROMPT.md) | **David Smith** | Filed master concept and Chapter One proposal; **Road v0.1 executable GB prototype** with B-001 and two saved observation flags. Full game, complete journal, real hardware and physical iPhone compatibility **not yet verified** |

**Designated owner/intended generational beneficiary:** Kiara Lynn Rose Smith (creator-designated; not proof of completed legal transfer).

**Historical relationship:** The earlier Breach Dungeon Android APK / Pixel Dungeon × Pokémon Mystery Dungeon ambition remains a separate archival identity **CR-10**. Dreamkiller adds SimpleMMO-inspired systems and the Game Boy Color/glitch design without replacing the old project.

[Public project index](../docs/PROJECTS.md) · [Creative work](../docs/CREATIVE.md) · [Continuity](../docs/CONTINUITY.md).

No proprietary assets from Pixel Dungeon, Pokémon Mystery Dungeon or SimpleMMO are included in this concept file. Any future distributed implementation would require an asset and licensing review.

## Dreamkiller Pocket — iPhone web app

[**Open iPhone emulator (GitHub Pages)**](https://whoiwts110217-creator.github.io/CF-0/dreamkiller/) · [Source, license, usage and limitations](dreamkiller/iphone-emu/site/README.md).

This is an installable **Home Screen web app** for Game Boy/Game Boy Color ROMs, not an App Store `.ipa`, and the original built-in road test is **not** the Dreamkiller game. Home-screen installation and gameplay still require real-device validation. ROMs remain in the user's browser; do not publish someone else's commercial ROMs.

## Chapter One design — DK-CH01-001

[**The Missing Cave — full first-chapter concept**](dreamkiller/chapter_01/CHAPTER_ONE_DESIGN_V0_1.md) · [structured branch/glitch model](dreamkiller/chapter_01/BRANCH_AND_GLITCH_MODEL.json) · [model consistency checks](dreamkiller/chapter_01/test_chapter_model.py).

New **PROPOSED** layer beneath the existing Dreamkiller constitution: first town, rescue choices, two cave floors, persistent fruit state, and glitch B-001 with deterministic entry/exit. The 72 combinatorial source-model scenarios are **not** an emulator or Game Boy ROM test.

**Adversarial stress audit:** [28/28 final reference checks; one repaired rescue-choice bug; seven open specification/ROM gaps](dreamkiller/chapter_01/STRESS_AUDIT_2026-11-07.md) · [Stateful simulator](dreamkiller/chapter_01/stress_reference.py) · [Regression tests](dreamkiller/chapter_01/test_stress_edge_cases.py). These are source/reference tests, not Game Boy gameplay.

## First executable ROM — Road v0.1

[**32 KB Dreamkiller Road v0.1.2 cartridge — latest rendered build**](dreamkiller/rom_v0_1/dreamkiller_road_v0_1_2.gb) · [Features, save layout and test limits](dreamkiller/rom_v0_1/README.md) · [Open iPhone player](https://whoiwts110217-creator.github.io/CF-0/dreamkiller/).

One-tap prototype loading is integrated into the iPhone web app. The exact v0.1.2 ROM **rendered a nonblank frame in headless Chromium and GameBoy.js** ([CI evidence](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42412019117)); physical iPhone controls and SRAM persistence remain untested. This is a *tech slice*, not the two-floor Chapter One, complete social RPG or secret ending. Historical CR-10 APK remains separate.

**Next cartridge slice (local handoff):** [v0.1.3 fruit persistence, build hash, migration test and still-unverified browser/iPhone acceptance](dreamkiller/rom_v0_1/V013_FRUIT_PERSISTENCE_HANDOFF.md). This version is a downloadable owner-conversation artifact, not yet the hosted default cartridge; the public on-site button remains v0.1.2.

**Live playable Dreamkiller v0.2:** [Open Dreamkiller Pocket](https://whoiwts110217-creator.github.io/CF-0/dreamkiller/) and choose **PLAY DREAMKILLER v0.2**. [Full ROM source, 13 limited-CPU checks and limitations](dreamkiller/rom_v0_2/README.md). Current browser core compatibility [passed](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42430061229). The game is a *vertical slice* and not yet iPhone hardware-validated.
