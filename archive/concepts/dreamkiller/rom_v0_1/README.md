## Current build — Road v0.1.2 (November 7, 2026)

**[Download the latest playable-mechanics cartridge (.gb)](dreamkiller_road_v0_1_2.gb)** · [Open Dreamkiller Pocket](https://whoiwts110217-creator.github.io/CF-0/dreamkiller/)

**Creator/developer: David Smith.** Designated owner/intended beneficiary: Kiara Lynn Rose Smith (legal transfer unverified).

**Actual browser validation passed:** [Dreamkiller Browser ROM Compatibility run 42412019117](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42412019117) loaded this exact canonical build through GameBoy.js/Gambatte in headless Chromium and found a nonblank **160×144 canvas with two rendered colors**. [Website deployment run 42412019124](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42412019124) also passed. These tests do not independently verify a physical iPhone, button interactions, cross-session SRAM persistence, or native Game Boy hardware.

Version **v0.1** and **v0.1.1** remain preserved as failed browser-rendering history. v0.1.1 adjusted LCD initialization, and v0.1.2 corrects the original CGB-header / DMG-palette mismatch by marking this slice **DMG-compatible** (it still works in the Game Boy Color emulator). Correct ROM SHA-256: `04370dae88b8ebcce9014063267d03b2bfb32dbbee3e2133daf31f6313cb08d6`; Git blob `46b4c9a2a0a45d507daa2f6890ee304fb944fed3`. Current web-app file `../iphone-emu/site/road-v01.gb` must match this exact blob.

**Source rebuild:** original Python assembler, hand-made pixel font and CPU-subset tests are available in the accompanying Dreamkiller Road v0.1.2 source ZIP in the release conversation. The game itself has only four route scenes and two SRAM flags; the complete event journal and Chapter One are not implemented.

---

### Previous v0.1 release notes (historical, superseded)

# Dreamkiller Road — Game Boy Cartridge v0.1

**Creator/developer:** David Smith  
**Designated owner and intended generational beneficiary:** Kiara Lynn Rose Smith (designation; legal transfer not independently established).  
**Concept identity:** CF-CONCEPT-DREAMKILLER-001 (new Game Boy branch), related to but distinct from historical Breach Dungeon Android APK CR-10.

## What is actually implemented

**[Download the 32 KB executable ROM](dreamkiller_road_v0_1.gb)** — `dreamkiller_road_v0_1.gb`.

This is the first **working-code cartridge prototype**, not the two-floor Chapter One, completed game, or DK-000 ending. It contains four small Game Boy scenes with D-pad movement, a *deliberately misindexed* route table, a shared-sign marking action, an on-screen journal, and two SRAM-backed observation flags.

- **RIGHT / LEFT:** travel S00 Cactus Brink → S01 First Sign → E01 Sign Echo → S02 Cinder Ford; return by walking west. Up/down move the player marker within a small safe range.
- **A:** while in S01/E01, chalk the shared sign `OBJ_SIGN_037`. Both locations show the same persisted mark.
- **B:** inspect the compact observation journal. Crossing east from S01 to E01 forces `B-001 observed` under the documented route conditions.
- **Persistence:** the B-001 and chalk flags are saved to cartridge SRAM; on reboot the position resets to S00 while the two observations are loaded from validated save records.

This is deliberately an early **mechanics test**, not an artistic-quality game scene, and an A press anywhere on either sign scene currently marks the sign (precise physical proximity isn't implemented).

## Hardware/storage contract

- ROM: 32,768 bytes. Header: MBC1+RAM+battery `0x0147=0x03`, ROM size `0x0148=0`, SRAM size `0x0149=2` (8 KiB).
- Game Boy/GBC-compatible instruction code starts at `0x0150`. Rendering uses 20×18 background tiles and an original, hand-authored 5×7 pixel-font data set.
- SRAM slots are `A000..A005` and `A010..A015`. Each record holds magic `DK`, sequence, flags, salted XOR checksum and last-written commit marker. A valid preceding slot can be used if the newest has an incomplete record. This is still a **minimal** mechanism, not general-purpose lossless event history.
- SHA-256: `b3ae9b964f7f4515663230e1a52f8944c09da937a52a054991f1066b0f48879e`.
- Verified Git blob SHA-1: `4d611e8b9fac80ee68a4005d301867e9b8c36734`.

## Tests — explicit limits

Five tests passed on an independently coded **small LR35902 instruction-subset emulator**: header/global checksum, D-pad movement, B-001 + sign SRAM persistence over reboot, recovery from a corrupted newer record, and key release behavior. This is stronger evidence than Python-only story simulation, but **not** a cycle-accurate independent Game Boy emulator, physical cartridge test, or real iPhone gameplay proof. An emulator must also actually preserve cartridge SRAM for cross-session persistence; emulator SAVE STATE is a separate mechanism.

Editable generator/test sources for this initial release are included in the accompanying source ZIP provided in the creation conversation. Publishing the ROM does **not** mean Chapter One or the larger game is implemented.

## Playing on iPhone

Open [Dreamkiller Pocket](https://whoiwts110217-creator.github.io/CF-0/dreamkiller/) in Safari and choose this `.gb` cartridge from Files, or use the integrated prototype launcher when its updated website deployment is confirmed.

This file contains no third-party commercial game assets. Any distribution incorporating Pokémon Mystery Dungeon franchise material would require separate rights review. The design version's Cubone is not included in this original prototype.

[Canonical concept](../MASTER_CONCEPT_AND_CONTINUITY_PROMPT.md) · [Chapter One](../chapter_01/CHAPTER_ONE_DESIGN_V0_1.md) · [Stress-test results](../chapter_01/STRESS_AUDIT_2026-11-07.md).
