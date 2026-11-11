# CF-SPIDER-001 — Spider Desktop v0.4 source release

**Owner direction:** Standalone, self-extending Windows Spider that uses Python/PowerShell/JavaScript, Chrome/ChatGPT, mouse/keyboard, Google apps, skills and eventually multi-agent delegation. This is a real software release in the user's ChatGPT conversation, **not** the static animated web spider.

## Exact artifact

- **Name:** `CF0-Spider-Desktop-v0.4.zip`.
- **Size:** 55,692 bytes.
- **SHA-256:** `5bd4f2287b5eec178c23519ef01e9d15b348dd2b9b319bf00da5945a06a983f8`.
- **Distribution:** Current ChatGPT Spider project conversation attachment, **not** hosted on GitHub or installed on the owner's HP. This page is a source release handoff, **not an installer link**.
- **Structure:** Native Windows Tkinter GUI `START_SPIDER.cmd`, Python modules and tests, narrow Chrome extension, 28 manifest-listed source hashes, README and change history.

## What this adds beyond v0.3

**SPDR-05/06: bounded Windows Hands.** A new Python stdlib `ctypes` Windows module can inspect the foreground process/window and client rectangle, and (with explicit owner approval) move the mouse to the **center** of a uniquely identified foreground Notepad window. An additional separately approved click is implemented only for an owner-confirmed blank, untitled Notepad document. The desktop GUI provides a four-second switch-to-Notepad countdown, then rechecks executable identity, window handle/PID, client geometry and STOP before acting. Unknown apps, user/model-supplied screen coordinates, changed windows, stale inspections, missing approvals and STOP refuse input. No new network access, Chrome action, OS privilege, scheduler or public relay command is introduced.

**Preserved:** v0.3 version-pinned built-in skill ON/OFF switchboard, restricted Code Lab toolchain/source inspection, inert Skill Forge idea staging, one-chat Chrome pairing, unknown-send hold, owner-gated fixed PowerShell/Git/Notepad tasks and private metadata receipt journal. v0.3 skill versions were intentionally not inflated merely to change application packaging.

## Acceptance checked in isolated build environment

- **49/49 Python tests passed**, including **13 fake Windows-backend Hands cases** for target identity, focus/geometry change, STOP, owner approval, stale state, click gates, unsupported coordinates and simulated movement/click.
- **3/3 Chrome companion Node mock tests passed**, plus JavaScript syntax and Python compilation checks.
- **700×500 Tkinter GUI startup** and off/on reviewed-skill toggle passed using an isolated Xvfb display; **no physical HP action executed**.
- Re-extracted the exact release ZIP into a fresh temporary folder, validated **28/28 internal SHA-256 manifest entries**, reran 49 Python tests and three browser tests. Release ZIP digest computed after packaging.

**Important separation:** These tests are **source-only and simulated GUI**, not evidence that the mouse moved on the user's HP, that Chrome sent a real ChatGPT message, that a Google account was accessed, or that general autonomous operation exists. Public GitHub architecture CI does not currently build this conversation-only ZIP, and must not be presented as such.

## Next steps and no-device gate

**Owner action now:** None while away from HP. Later, use one version only; stop other active ChatGPT writer extensions; extract v0.4 ZIP and run `START_SPIDER.cmd` with an existing Python 3 + Tkinter installation. First test the harmless one-tab ChatGPT round trip and STOP; then open an empty Notepad on the unlocked HP and choose **Move mouse (Notepad)**. Confirm the action and switch to Notepad during four seconds. Observe actual pointer movement or a safely refused test. Only attempt **Click once (Notepad)** after successful move-only test and explicit owner decision. This is a small supervised native-action test, **not** license for general GUI automation.

**Next engineering goals:** scoped Python/PowerShell/JavaScript code execution with resource/test guards; Windows UI Automation+accessible selectors and approved mouse controls for additional apps; self-authored skill tests/sandbox/approval; serial Agent Nest/Scout workers. The standalone app [architecture](ARCHITECTURE.md), [capability DAG](ROADMAP.json) and canonical [handoff](../docs/SPIDER_SPHERE_WORK_HANDOFF_2026-11-10.md) govern sequencing. No verified new independent revenue, no CF-200 task promoted, no prior HP maintenance HOLD or relay allowlist changed.

**Bootstrap source:** [Operator](../automation_200/MASTER_OPERATOR_PROMPT.md) blob `5dad8c17b04a4eb744e5a1474b2ecfb9ddd0abe0` → [Continuity](../automation_200/MASTER_CONTINUITY_PROMPT.md) blob `77900acb1c3eb75f8dfd3cef245503d052971479` → [Work](../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md) blob `d090f82eaf89d9cd339e7eef248750ebef965e88`. Re-fetch public main next session; never treat this document as HP permissions. Roll back from v0.4 by STOP + removing extracted folder/extension; keep v0.3 ZIP and private receipts.
