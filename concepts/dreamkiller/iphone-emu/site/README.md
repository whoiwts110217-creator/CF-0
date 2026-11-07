# Dreamkiller Pocket — iPhone GB/GBC Emulator

**Creator/developer of the Dreamkiller concept:** David Smith. **Designated owner/intended beneficiary:** Kiara Lynn Rose Smith (not proof of completed legal transfer).

## Open on your iPhone

Visit https://whoiwts110217-creator.github.io/CF-0/dreamkiller/ in **Safari**, then select **Share → Add to Home Screen → Add**. Open it from the new Home Screen icon. Tap **Choose ROM File** and select a personally held .gb or .gbc file in iPhone Files. No ROM files are uploaded to a server. Tap **Play Dreamkiller Road v0.1** to run the first original executable Dreamkiller cartridge, or **Run Built-In Hardware Test** for the older diagnostic ROM. Road v0.1 only implements movement, B-001, sign marking and two recorded observation flags; it is **not** the whole Dreamkiller game.

Controls: D-pad, A/B, Start/Select. SAVE STATE downloads a snapshot, LOAD STATE imports a snapshot, SOUND may need to be tapped after Safari backgrounds, RESET restarts the loaded cartridge. Backup states in Files. PWA cache is intended for offline reuse after one successful online visit; iOS can remove cached data under storage pressure.

## Source, license and honest status

- The emulation engine is the **Gambatte-derived GameBoy.js** from https://github.com/lrusso/GameBoy/tree/9c848d857d772bfbfabf7c9c374a848c6c530029 . Exactly copied `GameBoy.min.js` and `GameBoy.js` hashes, covered by original Gambatte GPLv2 rights; this directory contains the GPL-2.0 text and the full unminified engine source.
- The touch launcher/PWA shell is original project integration. Nintendo's Game Boy and Game Boy Color marks are not affiliated with this project.
- This is a **web app**, not a signed iOS .ipa. It should run in Safari but has **not yet been verified on an actual iPhone**.
- No commercial ROM is included. Two original ROMs are bundled: `road-test.gb` (diagnostic test) and `road-v01.gb` (first Dreamkiller Road B-001 mechanics prototype). The new ROM is verified to have the exact SHA-256 of the [canonical public Road cartridge](../../rom_v0_1/README.md).
- [GitHub Actions browser-integration test](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42411050395) launched Road v0.1 inside Chromium using the bundled GameBoy.js core and found a game canvas. A passing browser test is not a physical iPhone test. SRAM persistence in iOS Safari is not yet confirmed.
- The native Game Boy Color cannot provide an internet MMO without a separately designed service. This emulator player is independent of the game design.

[Master game concept](../../MASTER_CONCEPT_AND_CONTINUITY_PROMPT.md) · [CF-0 Continuity](../../../../docs/CONTINUITY.md)
