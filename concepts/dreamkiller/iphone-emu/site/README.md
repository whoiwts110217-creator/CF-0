# Dreamkiller Pocket — iPhone GB/GBC Emulator

**Creator/developer of the Dreamkiller concept:** David Smith. **Designated owner/intended beneficiary:** Kiara Lynn Rose Smith (not proof of completed legal transfer).

## Open on your iPhone

Visit https://whoiwts110217-creator.github.io/CF-0/dreamkiller/ in **Safari**, then select **Share → Add to Home Screen → Add**. Open it from the new Home Screen icon. Tap **Choose ROM File** and select a personally held .gb or .gbc file in iPhone Files. No ROM files are uploaded to a server. Tap **Run Built-In Hardware Test** for an original 32 KiB diagnostic ROM (not the Dreamkiller game).

Controls: D-pad, A/B, Start/Select. SAVE STATE downloads a snapshot, LOAD STATE imports a snapshot, SOUND may need to be tapped after Safari backgrounds, RESET restarts the loaded cartridge. Backup states in Files. PWA cache is intended for offline reuse after one successful online visit; iOS can remove cached data under storage pressure.

## Source, license and honest status

- The emulation engine is the **Gambatte-derived GameBoy.js** from https://github.com/lrusso/GameBoy/tree/9c848d857d772bfbfabf7c9c374a848c6c530029 . Exactly copied `GameBoy.min.js` and `GameBoy.js` hashes, covered by original Gambatte GPLv2 rights; this directory contains the GPL-2.0 text and the full unminified engine source.
- The touch launcher/PWA shell is original project integration. Nintendo's Game Boy and Game Boy Color marks are not affiliated with this project.
- This is a **web app**, not a signed iOS .ipa. It should run in Safari but has **not yet been verified on an actual iPhone**.
- No commercial ROM is included. The bundled `road-test.gb` is an **original diagnostic cartridge** that displays a text screen; A inverts the palette, B resets it. It is not a completed Dreamkiller game.
- The native Game Boy Color cannot provide an internet MMO without a separately designed service. This emulator player is independent of the game design.

[Master game concept](../../MASTER_CONCEPT_AND_CONTINUITY_PROMPT.md) · [CF-0 Continuity](../../../../docs/CONTINUITY.md)
