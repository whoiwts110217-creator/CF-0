# SPIDER Desktop — standalone program engineering home

**This directory is the architecture and machine-readable map for a separate Windows application**, not the existing public Link Vault spider graphic. The app must be capable of work in Python, PowerShell, JavaScript, Chrome/ChatGPT and authorized Google apps, plus owner-controlled mouse/keyboard, self-authored skills, skill switches, multiple workers and proactive invention.

- [Complete architecture and flow diagram](ARCHITECTURE.md)
- [18-capability dependency graph and eight phases](ROADMAP.json)
- [Architecture validation tests](tests/test_roadmap.py)
- [Canonical CF-SPIDER-001 continuity handoff](../docs/SPIDER_SPHERE_WORK_HANDOFF_2026-11-10.md)
- [Existing AUTO-08 Chrome code](../automation_200/continuation_chrome/README.md)
- [Existing optional Windows HP walker](../link-vault/spider-hp/README.md)

**Actual v0.4 application:** the latest ChatGPT conversation ZIP attachment is `CF0-Spider-Desktop-v0.4.zip` (55,692 bytes, SHA-256 `5bd4f2287b5eec178c23519ef01e9d15b348dd2b9b319bf00da5945a06a983f8`), **not a GitHub-hosted executable or an installed HP application**. It retains v0.3 skill switches, Code Lab, inactive draft Forge and one-tab Chrome bridge, and adds bounded owner-approved native Win32 foreground-Notepad relative mouse movement/click code. Fresh extraction passed **49 Python**, **3 browser mock** tests and **28 internal file hashes**; simulated 700x500 Tkinter GUI/toggle smoke passed. No signed-in Chrome or physical HP mouse trial was observed. See [v0.4 release evidence](RELEASE_NOTES_v0_4.md) and historical [v0.3](RELEASE_NOTES_v0_3.md). This directory currently publishes a **plan**, not a replacement executable. Do not tell users to run these docs as software.

**No current owner action:** no HP access is available in this source session. Next physically verified step is supervised v0.4 single-chat + native Windows STOP test before asserting autonomous control. Prefer incremental free tooling and the existing low-resource HP; no paid API, local large model or account takeover is assumed.

**Do not duplicate** CF-200 registry, Mission Control, private contacts, AUTO-08 browser writers or the existing public HP relay. New desktop capabilities are versioned child modules, not owner-permission grants. Use public canonical Master Operator → Continuity → Work prompts first for future CF-0 operations. Tests check the architecture only, not deployment.

## November 11, 2026 — v0.5 Spider Vision source-tested checkpoint

**Actual user-conversation deliverable:** `CF0-Spider-Desktop-v0.5.zip` (68,093 bytes, SHA-256 `178af3e0ac70b776cb5f61566c0fdea7ee7d808ffb201cc25d20bc16023bf298`). The ZIP was generated in the active conversation runtime and linked to the owner, **not** uploaded to GitHub and **not** installed on the HP. It contains all v0.4 files plus `spider_vision.py`, `spider_vision_uia.ps1`, `tests/test_vision.py`, new GUI buttons, a default-disabled, owner-enabled Vision skill and updated source documentation. The v0.4 Chrome companion remains version 0.4.0 and retains its original Chrome permissions; this release does not broaden its account control.

**What works in source:** one explicitly approved capture of a fresh *foreground, untitled Notepad* client area using standard Windows GDI calls (max 960×720), privately rendered as an in-memory PNG in Spider's Tkinter window; a fixed Windows UI Automation probe that returns only limited button/menu/tab/toolbar names and IDs, no document text; a bounded same-window pixel-diff signal. Captures stay in process memory, are not written to disk or sent to ChatGPT, Google, GitHub or any cloud. STOP discards the preview. Wrong focus/window, stale snapshot or missing approval is refused. Owner must turn on the distinct `spider.vision.notepad` skill and approve each observation. **Not yet:** OCR, whole-screen vision, image reasoning, autonomous application navigation or verified native HP capture.

**Tests:** 62 Python tests, 3 mock browser-side Node tests, successful 700×500 Tk/Xvfb window opening with synthetic PNG preview, 32 re-extracted file hash checks, Python compilation and browser JS syntax. These were run in the conversation's Linux build environment, **not GitHub CI for the ZIP** or physical Windows. Device-side Windows GDI and PowerShell UIA behavior remain separate acceptance gates.

**Owner's additional environment note:** a cloud storage service may be available on the HP with roughly 5 GB; provider, quota and current accessibility are **unverified**. This could hold versioned source backups/receipts after explicit owner selection, but it does not substitute for working RAM or C: disk; no auto sync was added. Never put raw screenshots, private transcripts or credentials in public CF-0 or an unspecified sync folder. No cloud credential is requested.

**Next acceptance:** on owner HP, run v0.5 on the unlocked desktop; enable Vision skill, open new empty Notepad, click Look at blank Notepad, switch focus during countdown and confirm local preview; then Read Notepad buttons and exercise STOP. If capture fails, record only the error code and Windows version, no screenshot upload by default. A real ChatGPT one-thread bridge test remains separately required, and other AUTO-08 controllers should be paused for that test. Rollback: STOP, close v0.5, disable/remove companion as selected, and restore v0.4 if needed. No scheduler/HP relay authority changed.
