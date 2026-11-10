# CF-MESH-001 — One-link cold-start for three chats


> **UNIVERSAL FRESHNESS CHECK:** Any older chat, source snapshot, task, story, science note, project or grant claim must be checked against [Current Source Gateway](../CURRENT_SOURCE_GATEWAY.md) and [CF-FRESH-001](../UNIVERSAL_FRESHNESS_CONTRACT.md) before presenting it as current. The public entrypoint is a moving `main` link; private original state remains private. This is additional source navigation, **not** a new scheduler or cross-account read.


**Public entrypoint.** Give this URL to a new chat: https://github.com/whoiwts110217-creator/CF-0/blob/main/docs/mesh/START_HERE.md

**Selected subject:** The owner's current topic is the anchor. A bare **continue** means resume the last unambiguously established active topic and perform a substantial authorized work session, not wander to an adjacent subject, generate another plan or stop at a token micro-checkpoint.

## Start without assuming memory

1. Retrieve and read from current public `main` in this exact order: [Master Operator](../../automation_200/MASTER_OPERATOR_PROMPT.md) → [Master Continuity](../../automation_200/MASTER_CONTINUITY_PROMPT.md) → [Work Prompt](../../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md). Record which files/SHAs you actually read, and read complete relevant contents in bounded chunks.
2. Read [CF-MESH-001](../PUBLIC_THREE_CHAT_CONTINUITY_MESH.md), [Universal Continuity Contract](../UNIVERSAL_CONTINUITY_CONTRACT.md), the [public topic graph](../PUBLIC_CONTEXT_GRAPH.json), and [current Mission Board](../../automation_200/MASTER_MISSION_BOARD.md) with relevant registry/issue/CI records. The Mission Board is historical and append-only in places: newer entries and real source state outrank stale headings.
3. Identify **`active_topic_id`** from an explicit owner request, or from a verified relevant handoff when no newer explicit request exists. For uncertain or missing context, state the uncertainty rather than assigning a convenient topic. Related links are **supporting context**, not a new active topic. The read-only [topic router](../../continuity/public_topic_router.py) can identify direct neighbors.
4. Inspect the [append-only public handoff ledger](handoff_events.jsonl) when present. Validate it with [public_mesh_handoff.py](../../continuity/public_mesh_handoff.py). **Never treat any self-declared worker label, a GitHub commit, or a generated event as authentic evidence that a distinct ChatGPT conversation actually read it.**
5. Continue the authorized task, with checks and source-backed artifacts. If GitHub write permission exists, use branch/SHA-safe edits and independently read back the result. Do not overwrite other chats' commits or publish raw conversations, private archives, payment details or credentials. If writing is unavailable, produce a bounded public-safe proposed handoff for an authorized operator.
6. On a meaningful milestone or owner-action requirement, report the result, evidence scope, broken connections, the next three tasks and a **single consolidated action for the owner (or none)**. Preserve the original active topic through the next handoff.

## Small, verifiable public handoff format

The [handoff validator](../../continuity/public_mesh_handoff.py) defines a deliberately restricted JSONL event. It accepts only canonical project IDs, known public source paths, source blob SHAs, SHA-256 chain links and fixed evidence flags. No free-text personal fields or raw conversation text.

- `handoff` means a writer created a source-only continuity checkpoint. It **does not** mean the task was executed successfully.
- `readback` means a later ledger entry cites the exact digest of an existing earlier handoff. Different `worker_label` values are a **syntactic guard only**, not proof of different ChatGPT accounts, sessions, devices or people.
- `provider_origin_verified=false` and `evidence_scope=github_source_only` are mandatory for public events.
- Use `python -m continuity.public_mesh_handoff --check` for chain validation, or `--rehearsal` for an explicitly **synthetic** A→B→C test. A `--propose handoff --worker A --topic CF-MESH-001 --read-head <actual-git-commit-sha>` output is only a draft until written with a GitHub SHA guard and independently read back. Do not insert a guessed SHA.
- A consuming chat must fetch current source and acknowledge the exact prior handoff digest with `--propose readback --worker B --topic CF-MESH-001 --read-head <actual-head-sha> --consumes <exact-digest>`. It must then verify the committed write and return to the active topic.

**Live acceptance still open:** A genuine cross-chat test needs three separately initiated conversations with provider-observed distinct session provenance, a real A→B and B→C source read, immutable digest correlation and owner confirmation of the intended account boundaries. GitHub checks alone establish only public-source consistency. Do not invent run IDs or claim success just because four synthetic events pass.

## The operating boundaries

This link does not grant cross-account access, scheduled ChatGPT execution, HP shell/GUI control, money movement, external posting or approval to publish private originals. The existing owner instructions, repository permissions, provider tools and safety boundaries prevail. Public documents are navigable shared records, not infinite model context or autonomous memory.

**Parent:** UCC-001 / CF-CORE. **Related:** CF-200, AUTO-08, CF-P1, Mission Control. **Next acceptance:** independent readback and documented no-topic-drift across actual separate chats; until then source-only.