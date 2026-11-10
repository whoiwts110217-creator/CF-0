# CF-0 — Universal Continuity Contract (UCC-001)

**Owner directive:** November 9, 2026. **Status:** public-safe operating continuity contract; not a new account/HP permission. **Scope:** every Caveman Focus project, tool, task, creative branch, scientific experiment, financial initiative, UI feature, automation and message-derived decision.

## One continuity spine, not isolated projects

On every consequential CF-0 run, read the current public `main` in this order:
1. [Master Operating Prompt](../automation_200/MASTER_OPERATOR_PROMPT.md).
2. [Master Continuity Prompt](../automation_200/MASTER_CONTINUITY_PROMPT.md).
3. [Work Execution Prompt](../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md).
4. [Owner capability contract](../automation_200/OWNER_CAPABILITY_CONTRACT.json), [prompt-change approval bin](../automation_200/PROMPT_CHANGE_BIN.md), [public project index](PROJECTS.md), [mission board](../automation_200/MASTER_MISSION_BOARD.md), and the relevant project's original sources/registry/ledger.

These pointers must be re-read on later runs; merely referencing this contract or having it in an earlier conversation does not prove any source was consulted. A current user instruction overrides stale project assumptions, subject to platform and safety constraints.

## Universal record: no orphan features

Every new artifact or modification must be traceable with the following fields, either in its own metadata, an existing project record or a public-safe handoff:
- `continuity_id`: stable identity; reuse prior ID where it exists.
- `parent_id` and `related_ids`: where it fits without merging distinct projects.
- `owner_intent` and `decision_source`: user directive, date when known, original source reference, correction history.
- `purpose` and `acceptance`: user-visible benefit and how it will be tested.
- `version`, `source_ref`, `source_sha`: actual bytes and provenance, not an assumed latest revision.
- `status` and `evidence`: idea / source present / tests passed / owner observed / live verified / financial verified / blocked. Preserve the limits of each.
- `dependencies`, `risks`, `permissions`, `privacy`: never infer a right to publish, spend, message third parties, control an HP or export private chats.
- `next_action` and `rollback`: one actionable next step, and how to reverse a change without erasing history.
- `event_ref`: append to the applicable existing event/decision record when actually executed. The CF-200 registry is reserved for its 200 defined work orders; unrelated experiments do **not** inflate its verified count.

## Freshness is universal, not a property of one document

The owner's November 10 correction applies the Jungle Map's old-to-current logic to **EVERY** project, task, experiment, story, automation, financial initiative, private source, future idea and status claim. Use the **[CF-FRESH-001 Universal Freshness Contract](UNIVERSAL_FRESHNESS_CONTRACT.md)**, [Current Source Gateway](CURRENT_SOURCE_GATEWAY.md), and [read-only source resolver](../continuity/public_freshness.py).

An old UCC-001 handoff is a historical snapshot even if its file remains at the latest public path. Re-check its exact Git blob/source version and separately verify provider-live/device/account/financial claims. A mismatch is **STALE**, a missing source or timestamp is **UNKNOWN**, and a matching local checkout is only **same public source bytes**, not proof of running systems or financial outcomes. All new records keep a moving latest-source route without erasing the original record. Private material retains a private-safe pointer, not a public original URL or copied bytes. This is an additive source-navigation requirement, not authority to revise permissions, restart HP schedules, publish private data, spend funds or make a new scheduler.

## The continuity loop

**Recover → identify → cross-reference → compare → implement → test → record → link → hand off → resume.**

Before making a new copy, check the current canonical artifact. Keep originals and corrections, record a conflict rather than invent a reconciliation, and attach updates to the proper project family. Public-safe derivatives belong in public GitHub; private transcripts, source exports, manuscripts, local credentials and payment details stay private.

**Never confuse:** a published page with a live visitor, a requested grant with revenue, GitHub CI with physical HP operation, a matched receipt with unattended scheduling, a pleasant educational animation with demonstrated learning, or a game badge with a verified operational achievement.

## Presentation continuity

Humor, game UI, accessible explanation and the proposed Brainrot → Brainpower experiment are overlays over the *same* evidence. The underlying source state is never modified to satisfy the fiction. Any game/reward display must identify whether it is a demonstration, an actual source-level milestone, or a separately verified external outcome. Users may turn the overlay off; professional grant, legal and finance records stay factual.

**Registered pilot:** [CF-EXP-GAME-LEARN-001](BRAINROT_TO_BRAINPOWER_2026-11-09.md), linked to existing `FIN-09` (gamified business), `CF-CORE` (clarity method), and `RES-04` (epistemic boundaries). This pilot does not silently create a sixty-third recovered original project.

## Cross-run handoff (compact)

```
continuity_id=<existing or new stable ID>
parent_id=<actual identity, or unresolved>
source_and_sha=<re-read actual source/version>
owner_instruction=<what changed and when known>
state_and_evidence=<exact milestone and verification type>
links_and_dependencies=<canonical public/private boundaries>
tests=<run IDs or unverified>
impact_and_rollback=<what was preserved and recovery path>
next_action=<single specific safe step>
```

A handoff without an executed change is a handoff, not completed work. This contract extends documentation consistency only and does not authorize new executor privileges.
