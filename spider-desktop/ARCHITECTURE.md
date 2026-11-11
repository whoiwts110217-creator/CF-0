# SPIDER Desktop — Master Architecture and Living Capability Map

**Project:** CF-SPIDER-001, child of CF-CORE/P0; related AUTO-08, CF-200, CF-MESH-001 and UCC-001.  
**Order:** 2026-11-10 owner clarification — build **its own Windows software**, not an animated web spider. It must use Python and other languages; control keyboard, mouse and applications; talk back and forth to ChatGPT; dynamically create/activate skills and delegate to other workers; proactively discover useful abilities.  
**Document status:** architecture and acceptance contract, **not** a claim that proposed capabilities are installed.  
**Machine-readable graph:** [ROADMAP.json](ROADMAP.json). Canonical record: [Spider handoff](../docs/SPIDER_SPHERE_WORK_HANDOFF_2026-11-10.md).  
**Base program:** CF0-Spider-Desktop-v0.2.zip, an owner-conversation artifact (35,083 bytes; SHA-256 219655cbc2bdfb2f2ce2853782d324bca6679f40c9d27dd476ebcd47f9a7b4c3). Not yet present as an executable in this public folder.

## 1. What the product must do

Spider is a **computer operator and a skill-building environment** with a graphical cockpit. It accepts goals, plans work, launches authorized workers, navigates Windows/Chrome/Google, tests code, verifies outcomes, gathers evidence, learns from failures and proposes tools that do not exist yet. A worker may author a new capability, submit it for tests, and activate **another approved worker or skill** through a shared registry. The owner can always inspect, pause, stop, revoke or roll back.

A representative finished task:
1. Owner says: "Find why CF-0's Chrome continuation is failing and fix it."
2. Spider reads the **current authorized** project sources and local capability/permission state, then decomposes the problem into evidence, reproduction, repair and verification.
3. It starts a **Researcher** to locate the failure and a **Coder** to propose a patch. It invokes Python, PowerShell and JavaScript toolchains only inside their allowed working directories with supplied time and resource budgets.
4. It starts a **Verifier** that independently tests the patch; if a missing UI-control capability is identified, Skill Forge produces a proposed skill with a manifest and tests.
5. The owner reviews any new permissions or consequential operations. An approved skill is enabled and installed into the registry with a rollback version; a failed test stays quarantined.
6. A **Windows/Chrome Operator** performs a small real-world acceptance in the exact authorized account and selected tab, captures a private receipt and returns the result to the same ChatGPT conversation without manual copy/paste.
7. Spider marks the task completed only with the required evidence. It can suggest other, previously unrequested improvements—but suggestions have no independent authority to send, spend, publish or execute.

**Success means the real task is done and measured, not that the spider moves or a prompt says "mission passed."**

## 2. Diagram — one program, many specialized functions

~~~mermaid
flowchart TD
    OWN[Owner / STOP / Approvals] --> APP[SPIDER Desktop App]
    APP --> ORCH[Mission Orchestrator]
    ORCH <--> MEMORY[Private Memory + Evidence Ledger]
    ORCH --> AGENTS[Agent Nest / Worker Manager]
    AGENTS --> PLAN[Planner / Researcher]
    AGENTS --> CODE[Coder / Language Workers]
    AGENTS --> OPER[Windows + Browser Operator]
    AGENTS --> VERIFY[Independent Verifier]
    AGENTS --> IDEAS[Discovery Scout]
    ORCH --> BROKER[Capability + Permission Broker]
    BROKER --> SKILLS[Skill Registry / Enable / Disable]
    SKILLS <--> FORGE[Skill Forge / Sandbox / Tests / Versioning]
    BROKER --> HANDS[Windows UIA / Screen / Mouse / Keyboard]
    BROKER --> LANG[Python / PowerShell / JS / Optional Toolchains]
    BROKER --> BROWSER[Chrome selected-tab Bridge]
    BROKER --> GOOGLE[Google Apps via Authorized Connectors / UI]
    BROKER --> GIT[Git + Files + CI]
    BROWSER <--> CHAT[Selected ChatGPT Conversation]
    BROKER --> RECEIPTS[Action Receipts + STOP / Recovery]
    RECEIPTS --> MEMORY
    RECEIPTS --> APP
~~~

**The broker is the only execution doorway.** Agents may propose commands and code, but their text alone is not a computer permission grant. The app's UI and queue are the control plane; individual adapters are replaceable. Don't build seven unrelated dashboards or schedulers.

## 3. Core layers and boundaries

### A. Desktop shell and owner control
- Standalone Python/Tkinter app initially (already source-tested as v0.2); later optional signed, bundled Windows executable if dependencies and 4 GB RAM allow.
- Navigation: **Missions / Active workers / Hands / Skill Forge / Skills on-off / Memory / Evidence / Connections / Settings**.
- Persistent STOP, Pause, Resume, explicit approval for one action or a reviewed bounded plan, safe exit. Always distinguish _proposed_, _staged_, _executing_, _blocked_, _observed_, _verified_.
- Readable at small resolution, keyboard-accessible, no false green status. A visible animated spider may represent state but does not own the automation logic.

### B. Orchestrator (task brain)
- Converts a goal into a dependency graph: source → diagnose → plan → approve → execute → test → verify → archive.
- Every task carries a stable ID, parent project/source, target application/account, requested effect, cost/effort budget, prerequisites, timeout, retry policy, approval level, stop rule and evidence target.
- Duplicate and uncertain send gates prevent an incomplete result from triggering a second execution. After restart, inspect and reconcile before retry.
- May choose the next task automatically **within previously approved scope**. It cannot promote its own role or treat raw chat text as authorization.

### C. Agent Nest (turn another one on)
- Agent roles: **Planner** (decompose), **Operator** (GUI work), **Coder** (programming), **Researcher** (find sources), **Verifier** (reproduce independently), **Scout** (invent/test opportunities), **Archivist** (dedup and preserve provenance).
- Spawn a worker from a **role template** with a narrow capabilities list, allocated time/tokens/memory/process budget and an expiry; a child never receives more rights than the spawning context.
- Local worker = separate task context or process, **not necessarily another paid LLM call**. Start with serial workers to fit a low-memory HP; only parallelize when measurement supports it.
- Workers exchange typed work packets, references and hashes; don't broadcast full private transcripts to every agent.
- One worker may request activation of another, but activation goes through the broker/permission and budget gates. It can turn an already-approved read-only skill on within its declared scope.

### D. Skill Registry and Skill Forge (teach itself new tools)
Each skill is a versioned, testable package with a declared manifest, permissions, supported OS/toolchain, input/output types, dependency IDs, source hash, test fixtures, rollback and runtime limits.

**Lifecycle:** discover need → propose → draft code → static checks → sandbox execution → repeatable tests → measure usefulness → owner review when scope expands → enable → monitor → disable/quarantine/rollback.

- A generated program is **never automatically trusted merely because Spider wrote it**.
- Read-only, already-approved skill revisions can be staged for evaluation automatically. Any new file modification, account access, browser sending, data export, network capability, credential interaction, shell freedom or payment action requires explicit review.
- A skill can be written in Python, PowerShell, JavaScript/TypeScript or, later, AutoHotkey, Rust, C#, etc. **Understanding a language's text doesn't mean its compiler/runtime is installed.** Capabilities report missing toolchains honestly.
- Skill Forge compares "with skill" and "without skill" on representative tests. Failed, non-reproducible or unnecessary skills are not promoted.
- Downloaded/community skills enter quarantine, are pinned to a source hash/license and tested before any activation. Never run arbitrary marketplace code or install its dependencies silently.
- Registry is **not** a new CF-200 master task list. Skill IDs live under SPDR; existing CF-200 evidence stays authoritative.

**Example manifest envelope (illustrative only):**

~~~json
{
  "schema": "cf0.spider.skill.v1",
  "id": "spider.windows.window-focus",
  "version": "0.1.0",
  "language": "python",
  "entrypoint": "main.py",
  "permissions": ["windows.window.inspect"],
  "requires": ["windows.uia"],
  "input_schema": "focus-request.v1",
  "output_schema": "focus-evidence.v1",
  "timeout_seconds": 10,
  "memory_mb": 64,
  "tests": ["tests/test_focus.py"],
  "sha256": "computed only from the actual package",
  "review_state": "draft",
  "enabled": false
}
~~~

A future implementation must validate manifest fields, entrypoint path containment, referenced dependencies, cryptographic hashes, signed/owner review for elevated rights, input types and output evidence. Do not treat this sample's placeholder SHA as a deployable package.

### E. Programming and local toolchain lab
- **Python:** parse/edit/test applications, small automation and data processing.
- **PowerShell:** Windows environment, file and app introspection, pre-reviewed local tasks, reversible system checks.
- **JavaScript/TypeScript:** Chrome extension, browser DOM, Node build/test workflows.
- **Additional languages:** through adapters when a verified compiler/interpreter is available; avoid redundant multi-gigabyte toolchain installs merely to satisfy a checklist.
- Before any execution: show working directory, requested filesystem delta, command category, environment dependencies, expected result and rollback. Run within a scoped workspace with process timeout and bounded output; no credential scraping or arbitrary unreviewed remote PowerShell.
- Code generation is cheap to propose; tests determine whether it works. A free static-only mode remains useful when no approved model route is connected.

### F. HP hands: GUI + keyboard + mouse + screen
Use a layered approach, not blind clicking:
1. Windows **UI Automation** accessible names/IDs/control types; exact-window targeting first.
2. Chrome **DOM/keyboard** controls for browser forms and conversation navigation.
3. Image/screen interpretation, optionally with a model, for applications lacking accessible controls (not assumed free or running locally).
4. **Mouse pointer actions** (click, double-click, drag, scroll), anchored to verified window/control geometry; only last-resort image-relative coordinates, never fixed global screen pixels without validation.

Safety and quality: check foreground window/focus before typing; honor display scaling/moved windows; pause if the owner moves the mouse or changes apps; stop on login, CAPTCHA, security, payment, or destructive confirmation gates; do not read/record sensitive content outside the selected scope. Owner can teach a task by a consented demonstration; the learner converts gestures to selectors, tests repeatability and adds a reusable skill after review.

### G. Chrome, ChatGPT, Google and external systems
- Reuse the v0.2 **single selected ChatGPT tab** loopback bridge, rather than scraping all tabs or sending into a different signed-in account. Only one extension/controller should write to ChatGPT at a time; preserve AUTO-08 checkpoint history and don't run it simultaneously.
- Browser result states: queued → selected tab confirmed → **possibly sent** → exact user turn observed → assistant reply complete → local receipt → optional owner-approved next action. "Sent" is not "worked."
- Google apps: prefer appropriately scoped official connector/authenticated APIs where available; use owner-selected Chrome UI for tasks with no suitable API. A Google sign-in is done by the owner in Google's real interface. Public GitHub stores no OAuth tokens or private docs.
- PowerShell/HP relay: **do not** widen the existing public CF-0 relay (currently ping/status/sidecar verification) to act as a general command-execution backdoor. Spider's local computer execution is a separately owner-opted-in agent and must prove it can stop.
- Files and GitHub: parse allowed source files and source refs, stage changes, run tests, show diffs, publish **public-safe** source only with the existing review rules.

### H. Memory, experiment and invention radar
- **Private state:** local app database/JSONL receipts and indexed user-approved references; no raw conversation upload to public CF-0. Keep a separate small source-linked graph instead of one giant prompt.
- **Evidence ladder:** guessed → proposed → source-tested → GUI simulated → owner-observed on HP → externally/provider-verified. Claim only attained levels.
- **Discovery scout:** analyzes recurring errors, stalled tasks, repeated human copying, unused installed capabilities, missing dependency chains and unnecessary manual steps. It creates measurable proposals Spider's owner didn't explicitly anticipate.
- **Safe self-improvement:** proposal can build alternative skill in a sandbox, score it on reproducible tasks, and queue it for activation. No autonomous rights expansion or destructive self-update.
- **Unexpected but useful functions to design for:** dead-link repair, local tool inventory, repeated-failure heatmaps, explain-why-disabled, task rehearsal before sending, semantic source dedup, dependency impact analysis, screenshot privacy masking, cost guard, feature flags and one-click rollback. These are candidates, not implemented features.

## 4. Permissions and execution levels

| Level | What is allowed | Example |
|---|---|---|
| **Observe** | Read explicitly permitted source/status; report only | Check a Git working tree |
| **Propose** | Draft code/tasks/skills; no actual computer changes | Suggest a missing Chrome skill |
| **Supervised execution** | One reviewed scoped action or short plan on the unlocked HP | Move pointer to verified control and click |
| **Approved routine** | Reuse an earlier-tested skill within exact account/app/path/time limits | Re-run a read-only health check |
| **Sensitive gate** | Pause for specific owner approval | Submit message, publish, delete, pay, sign in or change permissions |

A mode label **cannot** create a capability; it must be backed by working permission checks, a STOP channel and an acceptance test. All generated instructions and downloaded skills are untrusted inputs. A fixed built-in command list is an acceptable early stage; higher power is introduced only with measured, reviewable tool adapters.

## 5. Build order: directed dependency graph, not vague promises

The graph in [ROADMAP.json](ROADMAP.json) records 18 modules with dependencies, evidence status and one acceptance test each, grouped in eight phases.

| Phase | Engineering outcome | Exit proof |
|---|---|---|
| **P0: v0.2 baseline** | Preserve native GUI, companion, local receipts, STOP | Existing source tests pass; no owner HP claim |
| **P1: physical truth** | One HP app action and exactly one selected ChatGPT conversation | Real observed send/reply/STOP, no duplicate |
| **P2: multi-app + code** | Named GUI/UIA, browser, Python/PowerShell/JS adapters | Safe cross-app task verified with evidence |
| **P3: skill on/off** | Dynamic registry, dependency resolver, scoped switch, rollback | Disable/re-enable an approved read-only skill |
| **P4: skill self-authoring** | Forge + benchmarks + quarantine + teach mode | New skill generated, tested, reviewed and toggled |
| **P5: worker delegation** | Spawn/stop agents, assign tools, compare results, scout | Coder → Verifier handoff with actual receipts |
| **P6: Google workflows** | Scoped Google app work, link to CF-0 task evidence | Real owner-approved Google task with no token leak |
| **P7: optional packaging/phone** | Signed Windows distribution and private iPhone status | Owner device installation + explicit remote-security acceptance |

**Do not wait for P7 to make it useful.** The minimum compelling demonstration is **P2 + P3**: request a task in ChatGPT, Spider uses an approved real app and a code tool, replies with measured evidence, and enables/disables a test skill. After that, build self-authoring and multi-agent growth.

## 6. Tests that determine whether it really works

Acceptance suite must cover: clean launch with existing Python; low RAM and disk; Chrome account/tab mismatch; blank vs nonblank composer; pending ChatGPT answer; exact message/reply match; unknown send after crash; no duplicate/replay; offline/sleep/locked desktop; popup/security gate; Windows focus/DPI/moved window; mouse STOP; untrusted tool text; missing Python/PowerShell/Node; invalid manifest; dependency cycle; skill activation with insufficient permission; source hash mismatch; compromised external skill; worker budget exhaustion; child privilege escalation refusal; task-scoped Google access; rollback to prior skill; secrets omitted from receipts; and exact receipt-to-task evidence reconciliation.

Run simulation/source tests in CI, then **separately** one real Windows/Chrome owner opt-in test; the former never substitutes for the latter. A claimed new capability needs its own acceptance proof, not just a new feature label.

## 7. Resource budget and practical defaults for the current HP

Earlier owner observation: approximately **4 GB RAM, integrated graphics and 4.88 GB C: free**, subject to fresh recheck. Use existing Windows + Python stdlib + Chrome, no Docker/WSL or local LLM as a prerequisite, no silently added subscriptions. Keep worker count **one at first**, load other agents lazily, cap output/state, do not start background model processes. Generate code and run tests with available interpreters; an eligible connected ChatGPT session can supply reasoning through the separately authorized browser workflow, but a Plus subscription is **not** proof of unrestricted paid API use.

Packaging: prioritize a small readable source folder; optional signed .exe when measured. User's finite disk is part of the acceptance suite. The computer must be powered on in an available session for GUI control. Offline mode can queue and evaluate deterministic tasks but cannot claim to converse with cloud ChatGPT.

## 8. Honest baseline and next build tickets

**Actually present in v0.2 conversation artifact (source-tested only):** standalone Tkinter interface and local loopback server; selected-tab Chrome companion; fixed HP health/git/Notepad proposals; one-off approval; receipt metadata/STOP; 19 Python + 3 Node synthetic tests and isolated graphical launch. **Not present as a proved real-world capability:** arbitrary mouse control, automated Google work, self-writing enabled skills, unrestricted Python/PowerShell execution, agent spawning, autonomous novelty discovery, successful signed-in HP/ChatGPT operations.

**Next implementation priorities:**
1. **SPDR-10 Skill Registry** — implement manifest validation/enable-disable with one harmless built-in skill, no dynamic code execution. Tests include dependency cycle, missing permission, version pin and rollback.
2. **SPDR-09 Code Lab** — add bounded Python/PowerShell/JS toolchain availability probe, static checking and working-folder guard. Keep real execution in supervised mode until tested.
3. **SPDR-05/SPDR-06 Hands** — add proper UIA and relative mouse/keyboard abstractions, mock tests and physical STOP drill. Browser/Google UI workers must reuse one selected-account/session contract.
4. **SPDR-11 Forge** — generated skill draft + offline test harness + owner review, with an explicit *disabled* default.
5. **SPDR-12/SPDR-13 Nest and Scout** — agent delegation, goal-based resource limits and evidence-scored self-proposed improvements.

**Owner action now:** NONE (owner away from PC). Do not claim that any physical HP feature became live. Next owner-side gate is one supervised v0.2 launch/pairing smoke. Re-read canonical public main prompts, consult current source/board and preserve existing HP maintenance HOLD before consequential changes.

## 9. Design decisions that remain open

- **AI reasoning provider:** configured external assistant vs eligible ChatGPT bridge vs future lightweight local model. Existing subscription does not imply separate model API access; choose only after current eligibility, price and performance tests.
- **Windows UI backend:** Microsoft UI Automation native, future WinApp CLI or validated alternative; avoid using a paid dependency where a built-in one works.
- **Code execution sandbox:** workspace-scoped Windows process with file/permission limits vs stronger isolation later, selected by test results and host constraints.
- **Agent compute:** first serial tasks, then parallel when memory/latency measurements justify it.
- **Phone remote:** start read-only; no public listening socket, private authentication design before enabling remote control.

Every decision must include an owner-readable tradeoff, test, evidence, reversible change and explicit next step. No scope creep through downloaded community skill instructions.

## 10. Ownership, history, provenance and rollback

**Source of truth:** existing CF-0 public GitHub repository and canonical CF-200 registry; this SPDR graph is a child **architecture map**, not a duplicate task/contacts registry. Creator/developer David Smith; designated owner/intended beneficiary Kiara Lynn Rose Smith per current public master; legal transfer is not independently established.

Read [Operator](../automation_200/MASTER_OPERATOR_PROMPT.md) → [Continuity](../automation_200/MASTER_CONTINUITY_PROMPT.md) → [Work](../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md) at current public main before future decisions. The existing Spider/Sphere and AUTO-08 sources remain preserved; no new HP scheduler, public relay command or permission is created by the architecture. **Reversibility:** revert this documentation/graph only; v0.2 and any owner-local artifacts remain untouched. A future runtime upgrade must be versioned, testable and independently rollbackable.

## Implementation checkpoint — November 11, 2026, Vision v0.5

For `SPDR-05` and `SPDR-06`, the **conversation-packaged** `CF0-Spider-Desktop-v0.5.zip` contains executable source for a bounded local Notepad screenshot and limited UI Automation control metadata, rather than just the prior design. Its Python/Node synthetic tests and GUI PNG preview passed. The new `spider.vision.notepad` skill starts disabled and requires a separate enable approval and per-capture consent. Image pixels live only in RAM; no file, cloud or ChatGPT export is performed, and STOP discards the preview.

This does **not** satisfy `SPDR-06`'s full-screen understanding criterion or the physical Windows mouse/screen acceptance gates. The screenshot uses Win32 GDI; UIA uses a bundled read-only PowerShell script to inspect button/menu/tab/toolbar identifiers, not document text. Screen-reading compatibility must be verified on the owner's actual HP. A pixel difference is an observation, not task-success verification. See [current release note](README.md#november-11-2026--v05-spider-vision-source-tested-checkpoint) and [source/proof graph](ROADMAP.json).

A possible owner cloud allocation (~5 GB) is a **future optional storage adapter**, not a model, RAM extension or current connected service. No screenshot syncing is allowed by default. 

## Source implementation checkpoint — November 11, 2026, v0.6

The owner required 85% *developed groundwork* before physical HP testing. A reviewed 20-gate **source-only** acceptance checklist inside the v0.6 conversation ZIP now records 17/20 = 85% of **that checklist**: [release evidence](releases/v0.6.md). This is not a forecast, finished project percentage or a statement of real autonomous HP capability.

The **actual v0.6** source extends `SPDR-03` with an evidence-ordered private mission DAG and stop-bounded local source analysis, `SPDR-09` with selected-project syntax diagnostics, `SPDR-10/11` with a quarantined real skill-source draft pathway (never activated), `SPDR-14/15` with persisted mission/patch metadata and exact-hash reversible local source edits after explicit review. Mocked/pure-source tests passed. The owner must approve source transmission to ChatGPT one file at a time, and proposed chat text cannot silently run as PowerShell/Python or install a skill. All general Google browsing, independent code execution, autonomous multi-agent planning and full screen semantics remain future work. Nothing here widens the public HP relay or existing AUTO-08's browser writer.

Versioned full source is stored in the private ChatGPT Library and the active conversation artifact; this public repository currently holds **architectural truth and release evidence**, not the v0.6 application ZIP. Source checksum and exact test provenance are in the [release note](releases/v0.6.md). Next gate is supervised disposable-project testing when the owner is at the HP. 
