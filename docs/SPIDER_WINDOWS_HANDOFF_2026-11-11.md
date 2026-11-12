# CF-SPIDER-001 — Windows HP Spider: owner decisions and public-safe engineering handoff

**Owner-directed checkpoint:** November 11, 2026, evening Eastern. **Status:** public-safe decision and source audit; **NOT** proof of live HP deployment, repaired UI, or a merged AUTO-08/Spider runtime.

**Identity and relationships:** CF-SPIDER-001, parent CF-CORE / P0-P1; related AUTO-08 (existing one-tab continuation), CF-200 (separate source-verified task registry), Spider Desktop, Spider Sphere / Link Vault, existing HP relay and append-only evidence ledger. Creator/developer: David Smith; designated intended owner/beneficiary: Kiara Lynn Rose Smith (not proof of legal transfer).

## Current owner priority, effective now

**Focus on the existing Windows HP Spider. Pause further iPhone app development/experiments until the owner explicitly resumes them.** A previously discussed unofficial/sideloaded iPhone path is exploratory and **not built, installed, running, or approved for paid distribution**. Do not divert the Windows workstream into a separate iPhone program.

The final desired Windows agent remains a **single integrated, local-first Spider** (GUI, screen/UI hands, browser companion, Python diagnostics and bounded repair, Sphere and continuity, ledger and STOP/PAUSE/RESUME). Preserve already working components and source history instead of discarding them for separate demos. Run on modest HP resources without mandatory paid APIs or new subscriptions. ChatGPT/Gemini may be consulted through specifically authorized browser workflows, never assumed to be continuously controllable.

## Owner-observed behavior vs verified source

- The owner reports Spider is **running on the HP and partly doing what they want**, including an overlay arrangement where Spider remains visible above a recurrent Windows command/power window. This is **owner report**, not independent inspection; do not claim the latest packaged source version has been installed.
- The recurring window may be launched by an existing automation, **but its process origin is unknown**. Owner explicitly prefers not to disturb it. Do **not** disable, hide, kill, reschedule or modify the task merely from suspicion. If a non-invasive diagnosis is later authorized, correlate actual process/task evidence first.
- The [public HP health snapshot](../relay/health/latest.json) reports the relay/receipt store, **not** a live Spider GUI heartbeat. At this checkpoint its collected UTC time is `2026-11-12T01:47:17+00:00`, with `receipt_count=32`, `ping_receipt_count=10`, `last_receipt_status=completed`; these historical totals do **not** prove the Windows Spider is alive or unattended.
- [Spider Desktop v0.14 source release](../spider-desktop/releases/v0.14.md) already includes a **source-tested, owner-clicked Chrome-to-desktop `/heartbeat`** and LIVE/STALE/NOT RECEIVED display. It is **not** a recurring full-process liveness monitor. No contradiction: extend that existing signal rather than replace it.
- [Gemini Spider Unified v1.1.1 paste-only](SPIDER_PASTE_ONLY_2026-11-11.md) has **44 isolated Python tests passing** and a reversible HP patcher, but real HP application and signed-in browser input/readback are still **unverified**. The ZIP and patcher remain owner-conversation artifacts, **not public GitHub download binaries**.
- Source-only [AUTO-08 Chrome continuation](../automation_200/continuation_chrome/README.md) still has a strict one-tab, one-owner-controller, no-duplicate-send, STOP/unknown-result checkpoint policy. There is no verified live Spider/AUTO-08 merge.

## New requested behavior — not yet implemented/verified

### 1. Spider web/overlay heartbeat and health display
Within the **existing** Windows Spider UI/web component, show a small continually refreshing status area: `ALIVE / IDLE / WORKING / PAUSED / STOPPED / STALE / FAULT`, last heartbeat, paired browser state, last **verified** action, current blocker, and local error/repair status. Refresh cheaply (a candidate interval is 30 seconds), show `STALE` when events stop, and preserve STOP state through restarts. Use only actually observed local signals; never infer HEALTHY from an open window or a static green label. Do not publish prompts, messages, credentials or private machine details to the public status feed.

### 2. Repair integrated into the web/Spider interface
The owner wants **repair-on-the-fly**. Reuse existing reviewed Python source/diagnostic adapters. Proposed safe loop: detect fault → capture bounded private diagnostic evidence → classify known failure → request owner permission where the action can change code/config/state → back up original → apply an allowlisted repair recipe → run a specific test → record `REPAIRED_VERIFIED` only if that test passes, else rollback or STOP and request review. A clicked “Repair” button must **not merely change its label to green** without an actual repair/test. No general self-rewriting code or arbitrary remote command authority is granted here. Existing web repair behavior is **not independently verified by this handoff**.

### 3. Spider + AUTO-08 integrated operating path
Owner raised combining these systems. **Integration is an engineering direction to investigate, not proof of an approved immediate cutover.** Keep Spider as the visible native Windows controller; adapt the existing AUTO-08 one-tab continuation worker behind a single explicit capability broker, shared STOP/PAUSE, idempotent action IDs and append-only ledger. First compare running Chrome control paths and prevent two controllers from typing into the same tab. Preserve AUTO-08 checkpoint storage, `maybe_sent` uncertainty, STOP/unknown-send blocking and tested behavior. Do not uninstall or retire the existing extension or alter the CF-0 public relay allowlist (`ping`, `hp_status`, and configured read-only `sidecar_verify`) without a separate owner-gated, rollback-tested decision.

### 4. Unexplained speech-to-command concern
An unexplained assistant utterance was reported in this voice session. **No evidence establishes that Spider, a scheduled executor, or another application acted on it**; previous evidence checks saw scheduled work but not command execution attributed to the utterance. Treat this as an **unresolved command-origin/provenance diagnostic**, not a confirmed intrusion or proof nothing happened. Separate conversational/audio text from executable owner-approved commands; retain bounded local logs and require concrete action/result correlation before claiming a command was executed. No private transcript or personal details are reproduced here.

## Acceptance and next executable work

1. **P0 source inspection**: identify the actual owner-installed Spider build, and compare its desktop overlay, heartbeat, web Repair control and browser companion with the preserved current private packages. No blind patching of an unknown installed version.
2. **P0 bounded implementation/test**: connect a local periodic process/GUI heartbeat to a live status textbox; test WORKING→STALE on simulated timeout, STOP remains stopped, recovery after restart, and no false “repaired” result. Keep the existing v0.14 one-shot Chrome handshake separate from periodic process health.
3. **P0 adapter review**: inspect AUTO-08 and Spider's Chrome controllers for simultaneous-send and state-conflict risks; design a single-controller handoff with owner approval and rollback, then test with synthetic fixtures before any signed-in live send.

**Owner action class:** `REQUIRED_BEFORE_GATE` only for eventual real HP acceptance, not required for this public documentation update. When testing: use **one** owner-supervised launch/update, confirm overlay remains visible, health changes on deliberate STOP and browser disconnect, Repair shows evidence only when a repair truly passes, and no AI messages are sent without explicit permission. Preserve the previously working install and a rollback ZIP; do not request passwords, tokens or private chats.

**Evidence this handoff actually proves:** canonical source was read and new owner decisions were documented; **no** new working code, Windows installation, extension cutover, exact process identification, repair, app-store release or new financial receipt has been verified here. [Authoritative CF-200 registry](../automation_200/registry.json) remains **91/200 source-verified** (blob `77d548b366ff5dc2070c74e30423a3495c6a73cb`) at this check. No task promotions or append-only ledger mutations resulted from this documentation-only checkpoint.

**Preflight source SHAs** (re-fetch on next run; these are dated evidence, not a permanent latest claim): [Operator](../automation_200/MASTER_OPERATOR_PROMPT.md) `5dad8c17b04a4eb744e5a1474b2ecfb9ddd0abe0`; [Continuity](../automation_200/MASTER_CONTINUITY_PROMPT.md) `77900acb1c3eb75f8dfd3cef245503d052971479`; [Work](../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md) `d090f82eaf89d9cd339e7eef248750ebef965e88`; [Spider v0.14](../spider-desktop/releases/v0.14.md) `cf61a50105320358370202b5a53e54294c072f50`; [AUTO-08](../automation_200/continuation_chrome/README.md) `af1bc609e27e6558c9a3f2db193f2f67c875dcb2`; [Spider roadmap](../spider-desktop/ROADMAP.json) `f1c666603616ee4a41e9b691b2a12aee1482d63d`.

**Rollback:** This is an additive public-safe handoff. Revert its linking commit(s) if the owner corrects the decision; do not rewrite prior accepted events, private packages or source records. The target remains the existing Windows Spider program.


## Additive source-tested update — task assignment, bootstrap and Screen Eyes (November 11, 2026)

**Scope:** This section records a separately packaged, reversible **local Spider Unified 1.1.6 source patch** produced in the authorized ChatGPT conversation. It is not an HP installation, GitHub-hosted executable, or proof of a live browser round-trip. The owner artifact is `CF0_Spider_Bootstrap_Screen_Eyes_Fix_v1.1.6.zip` (SHA-256 `ccb4b763b7bff6dab0a16edc7969beb429796159ea705321e11b28668ca2d6ce`). Its private package contents and owner screenshots are **not** published here.

**Corrected delegation:** The exact request `ask gpt to task you` routes to a direct, bounded ChatGPT task-assignment request rather than the generic open/inspect planner. The outgoing task prompt identifies the current public [CF-0 memory bootstrap](CHATGPT_MEMORY_BOOTSTRAP.md), three linked master prompts in their required order and the existing [Spider/Sphere handoff](SPIDER_SPHERE_PROJECT_CHAT_PROMPT.md). **Including links does not verify ChatGPT actually fetched or read them.** Work remains restricted to reviewed allowlisted actions; uncertain sends do not auto-retry.

**New capture capabilities:** Existing Screen Eyes now offers owner-approved, local-only virtual-Windows-desktop PNG capture and selected-Chrome-tab PNG capture using local DevTools. Both display a local Tk screenshot preview and keep screen pixels outside the public ledger and ChatGPT/Gemini; no background polling or automatic screenshot upload. A new `CHECK GPT REPLY (NO SEND)` read-only status check helps diagnose an unverified reply but cannot cryptographically correlate it to a prior send. Screen capture is **not** autonomous computer vision or model interpretation.

**Verified only in isolated source tests:** Original 1.1 / 1.1.1 / 1.1.3 reentry baselines passed **43 / 60 / 80 Python tests** respectively with the change. Upgrade tests from recognized 1.1.5 (including 1.1.3 reentry) and one 1.1.4 baseline passed; rollback restored the previous source. Installer detects known source hashes, backs up and refuses unknown edits. **Owner's physical Windows screenshot, real Chrome capture, signed-in ChatGPT send/reply, and real installed build remain unverified.** No CF-200 registry status or financial evidence was changed.

**Owner gate and rollback:** On the owner PC, close Spider, install the reversible patch only against a matching known version, restart, test `capture screen` and `capture browser screenshot` with explicit approval, inspect the preview, then use `check gpt reply` without resending the previously uncertain message. Run `ask gpt to task you` only after verifying the old conversation's outcome. The package's included `ROLLBACK_SPIDER_FIX.cmd` restores the backed-up version if no subsequent edits changed it. No replacement Spider app, scheduler cutover, public relay permission increase, payment or external publishing is authorized by this note.


## Conversation-to-source audit: gaps remaining after Spider 1.1.6 (November 11, 2026)

**Source and boundary:** The private owner-delivered 1.1.6 Spider patch was audited against the owner's repeated request for one visible local-first Windows robot that sees, thinks, uses GUI/Python hands, asks ChatGPT/Gemini for substantive help, verifies changes and continues safely. An isolated clean 1.1.3-reentry-profile install ran **80/80 Python tests** successfully in Linux; this is **source-tested only**, not physical HP, signed-in browser or real screenshot evidence. No private package bytes, screenshots, conversations, credentials or paths have been published.

**Confirmed gaps requiring development / HP acceptance:**

1. **The complete see→understand→act→verify loop is missing.** 1.1.6 has owner-approved desktop and Chrome-tab PNG capture/preview, but no connected screenshot-understanding/Windows UI Automation model or end-to-end screen-derived action verification. The existing `SpiderHands` foundation defaults to dry-run UI.
2. **ChatGPT response attribution and interrupted-send recovery remain insufficient.** The read-only `check gpt reply` sees the most recent visible assistant answer and explicitly marks it uncorrelated; it may be an older answer. A send-specific durable pending state, exact reply correlation and no-duplicate recovery are not implemented.
3. **Immediate ledger evidence-label defect:** `SpiderOperator.log()` selects `Human-tested on the HP` on Windows purely by `os.name`, even if the logged action was `Unverified`. Replace this with result-specific verification status and regression tests; do not rewrite historical entries without append-only corrections.
4. **GPT task assignment is still a short fixed-action plan.** The `ask gpt to task you` branch only accepts browser navigation, inspection, optional Python scan/tests; it cannot perform an owner-reviewed and reversible real source repair. Current bootstrap is included as URLs in the outgoing prompt, **not independently fetched/verified by Spider**.
5. **Two-model implementation, reliable self-setup, crash-safe mission resumption, and integration with Mission Control/Sphere/AUTO-08** are unproven as one live installed Windows workflow. A source acceptance demo is not a signed-in ChatGPT/Gemini exchange, code repair or financial receipt.

**Corrected false-positive:** The latest 1.1.6 GUI patch **already removes** the duplicate screenshot-preview enqueue; do not queue that as a defect. The assignment text is approximately 1,763 characters against the browser sender's 1,800-character limit with a project selected, so prompt growth must be tested.

**Next acceptance sequence:** (a) repair and test exact send/response evidence and ledger labels, (b) connect reviewed screen/UI evidence to safe physical actions, (c) authorize and verify one `inspect → proposed diff → owner approval → apply → tests → verify or rollback` workflow, (d) demonstrate the single-controller ChatGPT/Gemini/Python loop on the owner HP. Preserve STOP/PAUSE, one-tab/no-duplicate invariants, working previous capabilities, private files and existing canonical registries. No remote HP permission or public relay expansion is granted by this audit.

**Status:** documentation handoff of an **audit**, not implementation of these missing capabilities. No CF-200 promotion, HP deployment, GitHub CI pass, external sale or payment is claimed.
