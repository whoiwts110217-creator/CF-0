# CF-SPIDER-001 — Spider Desktop v0.3 source release

**Owner directive:** A standalone Windows software program with Python, PowerShell, Chrome/ChatGPT, skill creation and switches, later real mouse/keyboard/Google and multiple agents. Do not substitute the public animated website.

## Release identity

- ChatGPT conversation artifact: `CF0-Spider-Desktop-v0.3.zip`.
- ZIP bytes: **47,372**; SHA-256: **`dd92a349fe051a7c238e8f6cadeefb091d2acbcb9d00b66edbe10613353fed0e`**.
- Contents: 24 archive files, including 23 file hashes declared in `SOURCE_MANIFEST.json`; program source, tests, Tkinter desktop shell and Chrome extension.
- **Distribution:** A ZIP attached to the user's original ChatGPT Spider conversation; **not** a public GitHub installer, prebuilt .exe or an installation on the owner's HP. This is a metadata record, not the executable itself.

## Implemented in v0.3, with source tests

- **SPDR-10 Skill Switchboard:** Five reviewed built-in skills can be turned on/off with persistent version-pinned state and dependency checks; malformed/unknown manifests are refused; community/generated executable code cannot be loaded from these manifests.
- **SPDR-09 Code Lab (partial):** Detects Python, PowerShell, Node, Git and other toolchain paths without launching them. Inspects the metadata and Python/JSON syntax of one owner-selected small text file, without returning its contents or executing it.
- **SPDR-11 Forge staging (partial):** Owners can save inert, inactive skill ideas for Python/PowerShell/JavaScript. The application does **not** yet write executable skill code, benchmark it or activate it.
- **SPDR-15 Recoverability (partial):** Uncertain ChatGPT sends block queueing until explicit owner review; restored local unfinished receipt records also enforce an owner review hold. Previous Chrome companion's independent uncertain-send protection stays active.
- Preserved from v0.2: paired one-tab ChatGPT companion, approval-gated fixed HP checks, STOP, source-output receipt limits and local metadata journal.

## Tests run on the exact ZIP

- **36 Python unittest cases passed** after extracting the finished ZIP.
- **3 mock browser-side Node tests passed**; JavaScript syntax checked.
- GUI started in an isolated graphical Xvfb smoke with a narrow window; skill switch off/on was exercised.
- **23/23 SHA-256 file hashes matched** `SOURCE_MANIFEST.json`.
- The external ZIP digest is shown above; it was independently recomputed from the ZIP bytes.

**Evidence class:** `source_tested / simulated_gui`, **not** `physical_HP_verified`, `signed_in_chatgpt_roundtrip`, `autonomous_multitool_agent` or `external_paid_receipt`. This GitHub repository's architecture CI does **not** independently test the conversation-only v0.3 ZIP. Do not assert otherwise.

## Limitations / next gate

The app does **not** yet independently navigate arbitrary Windows programs, browse Google accounts, move the mouse, operate a free-form shell, spawn reasoning agents or safely execute self-written skills. Owner's earlier HP observations were ~4 GB RAM and 4.88 GB free disk; no large model is bundled and no paid API is required for the included deterministic features.

**No action until owner at the HP.** Before a genuine live trial, stop existing AUTO-08/Master Continuation Switch Chrome writers, open one selected signed-in ChatGPT tab, start one Spider Desktop v0.3 instance through `START_SPIDER.cmd`, pair once, exercise the innocuous connection prompt and STOP; observe exact sent message, complete reply and receipt separately. Do not paste passwords, private chat exports or device logs into public GitHub. If it fails, capture an error category, review source and roll back by stopping/removing v0.3 without deleting private local data.

**Next implementation:** (1) source-reviewed Code Lab runtime workspaces with process budgets and tests; (2) bounded Windows UI Automation and relative mouse controls; (3) staged Skill Forge execution sandbox, tested manifests, owner-approved activation and eventually serial Agent Nest workers. Keep the architecture source [here](ARCHITECTURE.md) and the authoritative CF-SPIDER-001 [handoff](../docs/SPIDER_SPHERE_WORK_HANDOFF_2026-11-10.md).

**Source continuity:** Current bootstrap blob `9c15c103015699a9b166bf8230d798b6a571d35a`; Operator `5dad8c17b04a4eb744e5a1474b2ecfb9ddd0abe0` → Continuity `77900acb1c3eb75f8dfd3cef245503d052971479` → Work `d090f82eaf89d9cd339e7eef248750ebef965e88`. These sources must be re-read from `main` each consequential session. CF-200 is unchanged by this source release (last inspected **91/200**). Public-safe metadata only.
