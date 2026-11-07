# CF-0 concurrent-chat execution handoff — 2026-11-07

**Scope:** Public-safe coordination only. The owner has reported that another chat is working on the same priority. This document does not add a scheduler, HP command, permission, task completion, or owner approval.

## Single authoritative state

- [CF-200 registry](../automation_200/registry.json) is the only task status/count authority; at this inspection it reported **69/200 verified**, blob `8114ecc161c4ffd8773913625b5b48b52f6ef5a7`. Historical board entries with 65/200 or 67/200 are snapshots, not the live count.
- [Mission board](../automation_200/MASTER_MISSION_BOARD.md) is the handoff surface. Its current blob at inspection was `620d4062190b7ac8feaddbedbdcfeaf302603426`.
- [Operator prompt](../automation_200/MASTER_OPERATOR_PROMPT.md) blob `f3d4d0d443323528a64c6aa9e9d4c9a3b30e8098`; [continuity prompt](../automation_200/MASTER_CONTINUITY_PROMPT.md) blob `cac63dead1e00592c1d12ea6562639b02893d81f`; [Work self-reference](../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md) blob `5da1a390f31ee8f57e5829ef368062f9215c28ac`. Every subsequent run must refetch these three in order from public main, rather than relying on these hashes.
- Source-only CF-091 and CF-109 are already **verified** in the inspected registry. Do not repeat them as uncompleted work or credit their completion twice. CF-141 remained **planned**.

## Safe parallelism rule

1. The existing CF-200 hourly executor remains the sole scheduled CF-200 owner. Other chats may audit or prepare distinct source changes, but must not duplicate schedules, HP queue commands, private archive imports, or task verification.
2. Before editing any shared file, refetch its current blob SHA and current registry; use SHA-guarded edits and stop/reconcile on conflict. Never overwrite another agent's newer board, registry or event entry.
3. Source-only changes can be tested and committed independently. Only one accepted task-level evidence chain may promote each CF-200 task; preserve the four-task checkpoint rules and append-only events.
4. For physical HP acceptance, a matched public receipt and Windows scheduled wrapper timestamp must be correlated; neither CI nor a public heartbeat alone proves unattended execution.
5. Keep private v2 originals, personal chats, financial records and device data off public GitHub. Do not infer missing original project identities from reconstructed atlas entries.

## P0 evidence gap and next work

At inspection, `relay/health/latest.json` on public `main` returned **404**. This is `not_published`, not evidence that the HP is offline. The permitted next actions are (a) inspect the existing publisher/workflow and safe failure modes, (b) test source-level fixes, and (c) retain the single outstanding scheduled-poll correlation gate. Do not request repeated owner clipboard diagnostics or silently enable local deployment.

**Suggested division:** main executor owns P0 HP health publication/CI and authoritative board updates; a parallel chat may audit source evidence, continuity and CF-141's public-safe project index, with an independent file path and no private publication. Reconcile each change against current main before claiming it is integrated.

**Evidence limit:** This file is a coordination artifact, not proof that two chat sessions are communicating automatically, that a private archive was imported, or that any additional CF-200 task is verified.
