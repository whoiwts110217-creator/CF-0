# DREAMKILLER — THE ROAD REMEMBERS / v0.2

**Created by David Smith.** Designated owner and intended generational beneficiary: Kiara Lynn Rose Smith (not evidence of completed legal transfer).  
**Project:** Caveman Focus / Dreamkiller.  
**Build:** original Game Boy-compatible 32 KiB MBC1 + RAM + battery cartridge.  
**Status:** small **playable vertical slice**, not a complete RPG, not a 10–15 minute polished chapter. The GBC/iPhone player is a separate emulator; this cartridge is DMG-compatible and can run in its GB/GBC mode.

## What is actually included

- Original 8×8 hand-authored pixel tiles (48 terrain/object/sprite tiles), high-contrast original font, six location maps, and a two-frame **hardware sprite** for the Wayfarer. None of the game art was generated with an image model or copied from another game.
- Opening fall and indentation at Cactus Brink.
- Real D-pad movement and terrain collisions, not a text-only `@` cursor.
- Reproducible B-001 Road crossing between First Sign and Sign Echo, which the official atlas describes incorrectly. Chalk on the shared sign can be marked; all discoveries persist through flags in battery SRAM.
- One original cactus fruit, which can only be taken once.
- Cinder Ford town, Pip conversation with A/B response, and a cave entry.
- A turn-based shade that chases the player, blocks a tile, attacks, can be defeated in three blows, and opens the archive gate.
- The Archive Sluice with two figures and a record of prediction P-001, **not** a complete rescue/true-ending storyline.
- Journal available with B, with observations saved and shown without resetting the screen state.

## iPhone play instructions

Open [Dreamkiller Pocket](https://whoiwts110217-creator.github.io/CF-0/dreamkiller/) in Safari. Use **Choose ROM File**, select `dreamkiller_road_v0_2.gb` from Files, and wait for the game screen. The built-in prototype button may still point to the older v0.1.2 until updated in the public site.

- **D-pad** move one 8-pixel tile per press. On the current iPhone app, hold-to-repeat behavior is dependent on the launcher, so short taps are the known input path.
- **A** interact/take fruit/chalk sign/speak to Pip/enter cave/attack adjacent shade/open archive gate.
- **B** read and close journal (or decline Pip's pending request).
- **At the start:** move left 4, up once, then A by the cactus to take its fruit. Move east along the road. At the First Sign, A near the sign marks it. Cross right; Sign Echo looks similar, but the mark remains.
- **Town:** find Pip near the southwest plaza. Press A to speak, then A or B to answer. Walk to the south cave entrance and A to descend.
- **Cave:** shade attacks on turns and falls after three adjacent A strikes. At the east latch, press A to descend into the archive. The archive's record can be examined near the bridge/gate.

## What testing verifies and what it cannot

- `python build_v02.py` rebuilds the exact ROM with Python standard library and the files in this package.
- `python -m unittest test_v02 -v` ran **13/13 passed** in the **limited opcode-level LR35902 simulator**, exercising a live bytecode ROM, tilemap/OAM writes, movement and collision, two-slot battery flag migration, an enemy encounter, and repeated Road crossing.
- The test is **not cycle accurate**, and does **not prove** that the ROM renders or that SRAM actually persists in Safari or a real Game Boy. The public v0.1.2 browser rendering proof does not transfer automatically to v0.2. Those tests must be run on this exact ROM.
- Full battle balance, original 10–15 minute gameplay target, independent creature relationships, wider dungeons, functioning economy, Floor 000 and secret true ending remain unfinished.
- The existing older APK and v0.1.2 ROM have not been overwritten.

**Build SHA-256:** `df42c2a1d155b929cef09d4648b9ac80e95eb4a6eab8da44da894fa98f57ee2c`

## Files

- `dreamkiller_road_v0_2.gb` — cartridge.
- `build_v02.py` — tiny original assembler and game engine.
- `art.py` — tile data and six scene layouts; the source of all pixel art.
- `pixel_font.py` — original hand-authored 5×7 glyphs.
- `cpu_harness.py` — limited opcode simulator (not an emulator certification).
- `test_v02.py` — game-state and CPU execution tests.
- `ROM_START.png`, `PROBE.png` — screenshots rendered from the test CPU's VRAM, useful for visual review but not live iPhone screenshots.

**Continuity principle:** What happened remains part of what happens next.