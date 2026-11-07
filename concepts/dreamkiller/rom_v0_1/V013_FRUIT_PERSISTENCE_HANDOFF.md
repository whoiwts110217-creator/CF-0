# Dreamkiller Road v0.1.3 — Fruit Persistence Engineering Handoff

**Project:** CF-CONCEPT-DREAMKILLER-001 · **Creator/developer:** David Smith · **Designated owner/intended beneficiary:** Kiara Lynn Rose Smith (not evidence of completed legal transfer)

**Status:** actual **locally built and limited-CPU-tested 32 KiB GB cartridge**, supplied with full source/tests as a downloadable attachment in the owner's originating ChatGPT conversation. **Not** yet incorporated into the public GitHub ROM downloads, hosted iPhone default game button, or browser/physical iPhone compatibility suite. The canonical public Road prototype remains [v0.1.2](dreamkiller_road_v0_1_2.gb).

## What changed (relative to v0.1.2)

- On Cactus Brink (scene S00), press A to take the one initial cactus fruit. A persistent bit 2 (`flags & 0x04`) is set, and a two-slot MBC1 battery SRAM commit records the action.
- Subsequent A presses at S00 do not re-grant or re-save another fruit. Screen rendering and the B observation journal distinguish **FRUIT: ON CACTUS** versus **FRUIT: TAKEN**.
- Sign chalking at S01/E01 (bit 1) and the B-001 Road observation (bit 0) continue to work and coexist with the fruit bit; a v0.1.2 two-flag save is read by v0.1.3.
- **This is a taken/untaken flag, not yet a general inventory system, fruit decay simulation, maggot lifecycle, chronological log or ending rule.** The actual ROM still contains four road scenes.

## Reproducibility / honest test scope

- Original, dependency-free Game Boy bytecode assembler: `build.py`. Original 5×7 font: `pixel_font.py`. Limited non-cycle-accurate LR35902 model: `test_rom_cpu.py`. All are in the owner's ZIP alongside the cartridge.
- Cartridge size: **32,768 bytes**, header MBC1 + RAM + BATTERY, 8 KiB external SRAM.
- **SHA-256:** `22f554915952d8b89e6be14f64d2a3a55991f8c4263718424b0e7dde312595e6`.
- Local Python tests: **8/8 passed**, covering input/movement, B-001, sign and SRAM persistence, fallback to prior slot on corrupted latest commit, fruit one-time acquisition and reboot persistence, all three flags across battery reload, and 300 alternating-save writes across 8-bit sequence wrap.
- Separate migration smoke: old v0.1.2 SRAM flags `0x03` were recovered as `0x03` by a v0.1.3 restart with the same 8 KiB save image.
- This does **not** prove Gambatte/browser canvas rendering of v0.1.3, physical Game Boy compatibility, real iPhone Safari usage, live browser SRAM lifecycle, or full Dreamkiller chapter completion. [Earlier v0.1.2 browser rendering evidence](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42412019117) applies only to that earlier exact ROM.

## Owner play/test path (no extra setup)

Download the v0.1.3 `.gb` conversation attachment to the iPhone Files app, open [Dreamkiller Pocket](https://whoiwts110217-creator.github.io/CF-0/dreamkiller/), choose **CHOOSE ROM FILE** and select the new attachment. Do **not** use the existing 'PLAY DREAMKILLER ROAD v0.1.2' button for this release. Press A on S00, cross to S01/E01, press A to chalk, then B to read three retained facts. Test a reset and an explicit state export before assuming persistent battery storage works on iPhone.

## Next acceptance

1. Validate the **exact** SHA-256 v0.1.3 ROM in the existing headless browser smoke test (rendering + touch input).
2. Publish that binary and its full Python builder/font/tests as explicit source-controlled files only **after** verifying the build source is faithfully represented; update hosted button/assets, offline manifest and source checks together.
3. Test actual iPhone Safari local-loading and save/restart behavior; separate battery-SRAM behavior from emulator savestates. No claim of hardware-tested success before evidence.

**Continuity:** The one Day-One fruit is not duplicated. Previous sign and Road observations remain intact. This release does not silently overwrite the master concept, old Android APK CR-10, or v0.1.2.
