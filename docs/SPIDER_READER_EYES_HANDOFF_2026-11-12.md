# CF-SPIDER-001 — Spider Unified 1.1.4 response-reader and Chrome-eyes handoff

**Dated:** November 12, 2026 (America/Detroit). **Evidence class:** source implemented / isolated synthetic tests passed; **NOT** installed or verified on the Windows HP, signed-in ChatGPT/Gemini, or a live browser. **Project:** CF-SPIDER-001 under CF-CORE / P0 automation. **Related:** Spider Unified v1.1.3, the v1.1.1 paste-only source checkpoint, Spider Desktop v0.14, AUTO-08 and CF-200. Windows Spider remains the active development priority; iPhone development remains on hold.

**Creator/developer:** David Smith. **Designated intended owner / beneficiary:** Kiara Lynn Rose Smith (not proof of legal transfer).

## Implemented in the existing Spider, not a replacement application

- The AI response reader now refuses to count a newly submitted **user** message as a newly completed **assistant** response. It requires a changed/new assistant answer or observed generation, three settled observations, unchanged tab/origin and owner STOP compliance. Unknown completion does **not** trigger a blind resend.
- A manual `CAPTURE CHROME TAB (PRIVATE)` control is integrated into the existing animated Spider GUI, reusing its authorized local Chrome DevTools connection. Its PNG screenshot has type/size/target safeguards, requires owner approval, and is saved only in the private Spider workspace. The existing Windows `SCREEN EYES (PRIVATE)` feature remains intact. Screenshot acquisition does not imply image understanding, OCR, or autonomous visual reasoning.
- A Python stdlib-only reversible one-click updater preserves the existing Spider installation, backs up recognized files, checks exact source hashes, refuses unknown/custom code, and includes CHECK / UPDATE / ROLLBACK CMD launchers. It carries forward the previously produced version-specific v1.1.3 migration source; it is not a new program and adds no HP relay actions.

## Evidence inspected and reproduced

- The owner-available Spider Desktop v0.14 source underwent **167 passing Python tests** in an isolated Linux container. This tests that historical source tree, not the owner-installed Windows build.
- Spider v1.1.3 files were reconstructed from the user's pre-existing known-hash offline update source. The **13 new v1.1.4 synthetic tests** passed. The mocks check stale-answer refusal, new answer recognition, STOP/tab/origin guards and bounded private PNG acquisition.
- The v1.1.4 installer was exercised against a synthetic recognized installation: CHECK, APPLY, repeat-APPLY, ROLLBACK, source-hash restoration, protected private file preservation and modified-source refusal. All passed locally. A complete live Windows Spider 1.1.3 app, its signed-in browser and the physical HP were **not available** for these tests. Do not add the 13 to the older 44 or 167 as though the same integrated build passed all tests.
- Conversation artifact: `Spider_1_1_4_Reader_Eyes_Update.zip`; exact ZIP SHA-256 `30f622dc29853ebc6ade81c25bacdc6232162e6bf6cee543aa53c641371bcad2`. This ZIP was supplied inside the owner's ChatGPT conversation, **not** published as a GitHub executable or public download. This record contains no screenshot, local credential, source payload or conversation text.

## Deployment and current capability limits

**HP owner action — REQUIRED_BEFORE_GATE:** On the HP, stop the currently running Spider, extract the ZIP, and run the packaged `SPIDER_CHECK.cmd` then `SPIDER_UPDATE.cmd` (only on a recognized build). Relaunch the **same** Spider. Approve one private Chrome-tab capture; verify the correct screenshot preview. On an authorized signed-in ChatGPT tab, send one harmless distinct test request; verify Spider waits for a fresh completed assistant answer and does not count the outgoing user message as a reply. Repeat with a different response and confirm STOP/PAUSE behavior. Use `SPIDER_ROLLBACK.cmd` to revert v1.1.4 changes. If the source is unrecognized or multiple installs exist, **stop**, inspect and choose the correct local install rather than forcing a patch.

Do not disable or change the owner-reported recurring Windows console process solely because its origin is unknown. Do not change the public CF-0 HP relay allowlist (`ping`, `hp_status`, configured read-only `sidecar_verify`), AUTO-08 scheduler or browser controller. No live message, software deployment, remote repair, standing computer permissions, revenue or unattended autonomous completion are claimed.

## Next executable batch

1. Verify **one** actual owner-supervised Windows HP install, live browser capture, two distinct ChatGPT responses, and STOP/unknown-send behavior, preserving screenshots privately.
2. Complete Spider's existing **ALIVE / WORKING / PAUSED / STOPPED / STALE / FAULT** local heartbeat and evidence-backed repair display, with timeout and restart regression tests. An open window alone does not prove healthy execution.
3. Guard the future Spider ↔ AUTO-08 adapter against **two active Chrome controllers / duplicate send**, preserve the prior continuation checkpoints and obtain a real owner-reviewed local acceptance before cutover.

**Registry/financial truth:** CF-200 remains **91/200 source-verified** at main blob `77d548b366ff5dc2070c74e30423a3495c6a73cb`; no registry, checkpoint or CF-200 event promotion is warranted by this Spider artifact. No income or grant award is verified here. Public-safe source handoff only. Rollback: the v1.1.4 updater's backed-up exact files locally; revert this additive GitHub documentation change if its account-level status is later corrected.

**Current operating-preflight Git blobs read for this work:** [Master Operator](../automation_200/MASTER_OPERATOR_PROMPT.md) `5dad8c17b04a4eb744e5a1474b2ecfb9ddd0abe0` → [Master Continuity](../automation_200/MASTER_CONTINUITY_PROMPT.md) `77900acb1c3eb75f8dfd3cef245503d052971479` → [Work Self-Reference](../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md) `d090f82eaf89d9cd339e7eef248750ebef965e88`. Future sessions must retrieve current main again; do not treat these blob SHAs as permanently current.

**Owner decisions and earlier handoffs:** [Windows Spider owner handoff](SPIDER_WINDOWS_HANDOFF_2026-11-11.md) · [Paste-only source checkpoint](SPIDER_PASTE_ONLY_2026-11-11.md) · [Current Source Gateway](CURRENT_SOURCE_GATEWAY.md). This documentation does not authorize new browser activity or publication of private ZIP contents.
