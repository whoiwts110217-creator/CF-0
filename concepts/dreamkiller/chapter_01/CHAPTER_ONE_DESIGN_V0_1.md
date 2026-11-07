# DREAMKILLER — CHAPTER ONE: THE MISSING CAVE

**Design ID:** DK-CH01-001 · **Draft:** v0.1, November 7, 2026  
**Project:** CF-CONCEPT-DREAMKILLER-001 · **Creator/developer:** David Smith  
**Designated owner / intended beneficiary:** Kiara Lynn Rose Smith (designation; legal transfer unverified)  
**Status:** **PROPOSED additive story and mechanic design**; not an owner-confirmed canon replacement, working ROM, functional multiplayer game, or emulator-tested exploit.  
**Canon parent:** [Dreamkiller Master Concept](../MASTER_CONCEPT_AND_CONTINUITY_PROMPT.md). **Historical predecessor:** CR-10, separate Android Breach Dungeon APK; not modified by this design.

> The player does not unlock curiosity. The Road exists from the first input, and its signs are there for anyone willing to look.

## 1. The first five minutes

The player begins beside a cactus fruit, old cart ruts, a dry creek and a damaged sign. It reads **THREE STEPS TO CINDER FORD**.

Walk east three steps. Another sign appears, almost identical to the first. The music continues normally. Nothing says GLITCH. If the player continues east, they reach town; if they stop, read, count and use chalk, they can investigate what seems like a return to the same place.

A small **Cubone** named Pip then asks if the player has seen its brother **Cairn**, who entered a cave that has vanished from the latest survey. The player can say **help**, **refuse**, or **go alone**. The request introduces the rescue story, but does **not** gate entry to town, encounters or the first glitch.

Cubone is an existing fan-fiction placeholder from the earlier pitch. This public design includes no third-party images/audio/code. If the future standalone ROM cannot legally use Pokémon assets, design an original creature while recording the change to identity and function; do not silently revise history.

## 2. One geography, three styles of gameplay

| Stable ID | Place | Role | Connections |
|---|---|---|---|
| S00 | **Cactus Brink** | Starting road; original fruit and seed lifecycle | East to S01 |
| S01 | **First Sign** | Old atlas claim, beginning of B-001 | West S00, east E01, north W01 |
| E01 | **Sign Echo** | A nearly identical road segment; sign appears here too | West S01, east S02, north D00 |
| S02 | **Cinder Ford** | Town, merchants, guild board, professions and supplies | West E01, north W01, south D01 (when open) |
| W01 | **Thornbank Wilds** | Creature society, creek, alternative cave route | West S01, south S02, east D01 |
| D00 | **Below the Sign** | Hidden survey room and return path | South E01, east D01 |
| D01 | **The Missing Cave, B1** | Tactical dungeon, rats, floodwater and traps | West D00, north W01, south S02, east D02 |
| D02 | **The Archive Sluice, B2** | Rescue, maintenance intelligence and watergate | West D01 |

**Surface** uses SimpleMMO-like short travel, trade, professions and changing social conditions. **Wilds** supplies a society of recruitable or independent creatures and rescue teams. **Deep** is one tactical tile-based RPG with survival, equipment, terrain and a real retreat route. These are connected places, not three isolated menus.

A Game Boy Color cannot natively host the full always-connected MMO described by SimpleMMO. For the proposed cartridge, guilds and town economies are simulated offline, with optional later link-cable or external companions scoped separately.

## 3. People who exist even when ignored

**Pip:** a Cubone looking for Cairn. On **help**, Pip accompanies the player and grows trust through fulfilled actions. On **refuse**, Pip visits the rescue board and seeks other help, rather than being automatically punished with death. On **go alone**, Pip remains wary and can later reassess evidence the player brings back.

**Mara Finch:** a Surveyor who mapped the town. Mara says her previous map contained one direct eastward road segment and no entrance to the cave at that moment. She can lend chalk or compare observations. Her belief is not world truth; she is allowed to be an honest, careful person who is nevertheless wrong.

**Knuckle:** a skeleton baker. This intentional absurdity is part of a coherent economy: flour, water, heat, delivery routes and customers determine stock. Cinder Ford's mill is affected by the dungeon watergate, which in turn changes bakery prices after supplies arrive.

**Mosskin:** an original sapling-like Thornbank creature that can hold a wet floor tile with its roots and open an alternate cave path. It can cooperate or decline; defeating it never automatically forces recruitment.

**Registrar Four:** a damaged Continuum maintenance intelligence in the cave. It predicts the last repeated player command and prepares a counter to that pattern. A changed tactic, companion action or physical lever interrupts the prediction. It is limited, not necessarily evil.

## 4. Glitch B-001 — THE SIGN THAT POINTS BACK

**Classification:** deliberate route-index alias expressed as a controlled Game Boy-era glitch effect. **Not** a verified hardware memory exploit. **Status:** proposed/unimplemented.

The Continuum's old atlas claims **S01 east → S02**. The observable world contains a missing intermediate route: **S01 east → E01 east → S02**. Both S01 and E01 reference the exact same persistent object, **OBJ_SIGN_037**, seen from two apparently incompatible positions. The world did not spawn a second copy of the sign.

**Exact trigger:** from S01, step across the eastern map boundary. The result is always E01, regardless of the player's name, mission progress, day/night, random-number state, friendship, or choice about Pip. The player can force it on Day One.

**Independent observation:** mark the sign with the starter chalk, then cross. Because the two images refer to the same underlying object, the chalk mark is still there. Marking does **not** cause the Breach; it makes an existing property easier to observe. Open the journal to compare the claimed atlas destination with the actual destination.

**Recovery:** E01 east takes the player to S02; west takes them to S01. E01 north opens D00, which returns south. Repeating the action reproduces the same result. There is no deliberate memory overflow, infinite loop, inaccessible return or save destruction.

**Game implementation hypothesis:** a deliberate destination-table mapping for the S01 eastern edge loads E01, while the town's recorded map text points to S02. A brief tile/palette misalignment creates the glitch aesthetic, but the route semantics are explicit and safe. This is not the eventual, still-unverified Floor 000/player-name interpretation from DK-000.

**Continuity test:** if the road is repaired in Act III, the player journal continues to show what happened on Day One, including the exact original conditions. The repair changes subsequent routes; it cannot silently rewrite prior observations.

## 5. The expedition

### Floor B1 — The Damp Corridor

Room anchors: entrance shelf → rat burrow → spillway → supply alcove → archive staircase. Other passages may vary from a fixed seed, but the necessary anchors cannot randomly disappear.

A rat eats something blue beneath an overturned table. Pip hears a voice claiming to be Cairn. The rat's behavior and the sound are observations, not proof of an identity.

Water extinguishes torches and moves floating items. Mosskin's roots can brace one wet tile; a mechanical lever offers another option; retreating to buy bread and equipment is valid. Scratches on the old stone echo the four marks of the ancient Road/hammer imagery, without explaining the symbol.

The town-side entrance may be temporarily occluded by the local Breach phase. It is **not** tied to iPhone wall-clock time and is never the only entrance: Thornbank and Below the Sign permit entry by alternative routes.

### Floor B2 — The Archive Sluice

Registrar Four guards a real watergate and a damaged historical record. Two physically separate characters emerge:

- **Cairn-A:** Pip's injured brother who entered the original cave.
- **Cairn-B:** a reconstructed individual with memories of Cairn's life, its own fear of erasure, and its own continued physical existence.

Within this fiction, both are people. Neither is automatically a disposable fake. Whether their memories imply one continuing identity is an unanswered question.

A machine ledger made its prediction **before** the player's rescue:

**P-001: ONE CAIRN MAY EXIT THE ARCHIVE.**

If two independently existing Cairns leave by a safe passage, P-001's one-person prediction is falsified. That does **not** establish that reality is logically contradictory, or that both individuals share a single identity. If only one exits, a single observation does not prove the universal prediction.

Registrar Four's encounter can be solved tactically, through physical manipulation, companionship, or another consistent method. A stronger sword is not the only route.

## 6. One practical choice with two legitimate interests

At the archive watergate:
- **Route water to the surface mill:** Cinder Ford eventually gets cheaper flour and bread; Thornbank's downstream nursery loses protective flow and requires adaptation.
- **Keep water below:** the nursery remains stable; mill production stays constrained and merchants seek other supplies.
- **Leave the gate as found:** a guild or other character may operate it later. The recorded actor is then that person, not the player.

Bread quantities, costs, habitats, and people react to this single physical decision. Neither option awards a mandatory moral label.

The world advances through deterministic action-based **world ticks**, not the time the iPhone is left idle. Pip and the guild can pursue rescue on their own milestones. The player never has to accept the quest just to keep living in the world.

## 7. The cactus, fruit and maggot — preservation rather than a forced lesson

IDs: **OBJ_CACTUS_001**, **OBJ_FRUIT_001**, **OBJ_SEED_001**.

If the player leaves the fruit, it may ripen, fall, feed larvae, rot and scatter seeds under known conditions. If the player harvests the fruit, the original is gone from the cactus. Seeds, carrying, planting, and loss must be accounted for. A later cactus does not materialize solely to make the final scene poetic.

The story's significance is open for discovery. There is no achievement called "UNDERSTOOD LIFE".

## 8. Recording evidence on a Game Boy cartridge

The design proposes a bounded event journal with: **event ID, world tick, place ID, actor ID, conditions, observation, interpretation and affected entity IDs**. An event remains fixed; an interpretation may later be revised in a separate record.

Example: OBS-0007 states that the player moved S01 east and arrived at E01. The current atlas claimed S02. Seeing chalk on OBJ_SIGN_037 supports the single-object hypothesis, but the ultimate cause of the spatial fold remains unproven.

The intended Game Boy Color display is **160×144 pixels**, or **20×18 8-pixel tiles**. A possible dungeon view is **20×15** map tiles and **3** HUD rows. A future larger cartridge may require an MBC5 memory bank controller. These are proposed design constraints, not evidence a working game ROM exists. Hardware references: [Pan Docs](https://gbdev.io/pandocs/) and [GBDK banking guide](https://gbdk.org/docs/api/docs_rombanking_mbcs.html).

Game-specific save data must be distinguished from emulator save states. No real-cartridge persistence or iPhone runtime performance is yet verified.

## 9. What can be completed, and what cannot be claimed

The chapter's **play goals** are to reach a living town, witness an independently reproducible road anomaly, make a meaningful rescue-related choice, attempt a two-floor dungeon, and see the consequences return to town life.

Future design validation must check: all location references exist; every scene can return to town; S01 east always yields E01 without quest gating; both sign scenes share OBJ_SIGN_037; B1 has at least two entrances; all three Pip responses have consequences; P-001 is recorded before outcome; water transfers affect both communities; the original fruit is never duplicated.

The design remains **PROPOSED** and does not supersede the master constitution, historical Breach Dungeon APK CR-10, or the independent iPhone emulator package.

**Next design sequence:** screen-by-screen maps and UI → creature/terrain combat matrix → journal/save-state layout → second independent glitch → eventual real playable cartridge proof.

*What happened remains part of what happens next.*
