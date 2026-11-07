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
- **Current browser compatibility issue (November 7, 2026):** [independent real-browser ROM smoke test](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42411665407) launches the bundled Road v0.1 cartridge in Chromium, but the cartridge's canvas remains **blank**. The diagnostic cartridge draws nonblank pixels. **Road v0.1 is not yet verified as visibly playable in the bundled browser emulator or on an actual iPhone.** The previously reported successful launch/canvas creation was not proof of rendered game frames. SRAM persistence in iOS Safari remains unverified. This failing test stays active separately from the [public site deployment](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42411688727); do not silently relax the pixel-output acceptance requirement.
- The native Game Boy Color cannot provide an internet MMO without a separately designed service. This emulator player is independent of the game design.

[Master game concept](../../MASTER_CONCEPT_AND_CONTINUITY_PROMPT.md) · [CF-0 Continuity](../../../../docs/CONTINUITY.md)
