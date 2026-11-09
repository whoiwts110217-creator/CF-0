# CF-0 Mission Control

A read-only dashboard for Kiara Lynn Rose Smith’s Caveman Focus. It reads public CF-0 files and links back to the authoritative registry, mission board, receipts, and operating prompts.

## Source behavior

- The dashboard resolves the current main commit, then reads the registry, owner capability contract, continuity summary, fixed health report and documented ping pair at that one commit.
- The verified count comes from individual registry statuses. A checkpoint appears when the dated continuity summary agrees with the registry.
- A public ping is matched by request ID, canonical request digest and completion payload. The health row reports file availability. Windows Scheduler correlation needs independent evidence.
- The **Public cloud watchdog** row independently reads the latest metadata from the public GitHub Actions CF-0 channel evidence watchdog at its workflow-specific runs API; it shows cloud run success/failure/pending with a source commit and run link. The read is anonymous and read-only, and invalid, missing or non-main workflow metadata fails closed. A green cloud run is **not** physical HP identity, command execution, Windows Task Scheduler correlation, or continuous account autonomy.
- The [GitHub Pages dashboard](https://whoiwts110217-creator.github.io/CF-0/mission-control/) bundles a generated baseline with registry progress, tool IDs and source status, the public ping pair when available, and health-report availability at its build commit. A successful refresh replaces the view with the current public commit.
- **Show restricted:** the work-order view distinguishes verified, source-work candidate, physical HP, owner-local installation/evidence, and unverified dependency states. The toggle shows/hides the held rows without deleting them. Classification applies to the public registry and does **not** include private runtime overrides, so a source-work candidate is not execution authorization.
- **Tools and task power:** the tool table reads the version-pinned owner capability contract, distinguishing source-present public relay and documentation from the historical `open_notepad` regression. These are capability descriptions, **not** proof of physical deployment or permission to extend the relay. The L0/L1/L3 labels are descriptive scopes, not user-adjustable powers. External account, finance, shell, and private data permissions are outside this public source inventory.
- **Local runtime evidence (opt-in):** select a real owner-local `cf200.decision_proposal.v1` JSON report and/or a private `cf200.resumable_focus.v1` JSON state file in the browser. The file contents are read with `File.text()` in memory only, with a 64 KiB size cap; they are never uploaded or persisted by the page. The view reports sampled local holds as *unverified local evidence*, never superseding physical HP, owner-local or dependency gates. The focus display discards private checkpoint references and shows only task IDs and pointer presence. A source-commit change clears the imported overlay. The standard decision report includes at most ten held task IDs and does not establish a live task result or authority. The owner can clear both imports in one click. A static page cannot automatically read private ChatGPT or HP state.
- Example local output generation: `python -m automation_200.decision_engine > private-decision.json`. Save it privately, do **not** commit it. The [resumable focus CLI](../RESUMABLE_FOCUS.md) supports an explicit local `--state-file` with `--apply`; importing that file into Mission Control is a **manual** readback, not a scheduled handoff.
- **Hosted verification November 9:** [GitHub Pages Mission Control](https://whoiwts110217-creator.github.io/CF-0/mission-control/) exposed the new *Show restricted* and *Tool power* controls in its delivered page. The older `cf0-mission-control.whoiwts110217.chatgpt.site` copy was missing them; prefer GitHub Pages. Page content presence is not proof of JavaScript refresh, HP deployment or session-level autonomy.
- The application reads public GitHub URLs without authentication or write access.

## Development

Serve the dist folder with a static web server. The source distribution reads GitHub directly. Hosted packaging also includes a generated dist/snapshot.json baseline and its pinned commit.

Run the model and GitHub-loading tests using this command.

    node --test tests/*.test.mjs

## AUTO-08 Continuity Control (source prototype, November 9, 2026)

The [Continuation panel](https://whoiwts110217-creator.github.io/CF-0/mission-control/continue-control/) is a linked view in the existing Mission Control site. It adds an original dark, pale-blue reflective-jacket-inspired interface; explicit primary/secondary account selection; local-only import of conversation IDs/titles from a user-selected JSON export; local private checkpoint download; a copyable Work recovery handoff; and a clearly labeled manual fallback. No raw chat content is uploaded by the panel. Private checkpoint files must remain private.

**Automatic master switch: DISCONNECTED.** The static site cannot access personal ChatGPT sessions or send messages. The browser UI deliberately disables the switch until a separately authorized supported executor exists; it must not be described as functioning continuous account autonomy. The separate source-level `continue-control/loop.mjs` implements a bounded, serial adapter contract: send exactly `continue`, wait for the adapter to confirm the full response completed, then advance, with stop, unknown-result hold, and per-pass duplicate prevention. Unit tests cover the contract; they do **not** prove any real ChatGPT conversation was controlled.

See [owner intent and acceptance requirements](../../docs/AUTO_CONTINUATION_CONTROL_2026-11-09.md) and [PR #28](https://github.com/whoiwts110217-creator/CF-0/pull/28). The approved HP public-relay actions and all original CF-200 dashboard data remain unchanged.

## Consolidated automation controls — November 9, 2026

The **Automation control center** is a new section **within the restored original Mission Control**, at
[Mission Control → Automation controls](https://whoiwts110217-creator.github.io/CF-0/mission-control/#automation-controls).

It displays four automation categories without modifying the CF-200 registry or the existing dashboard:
1. ChatGPT personal automations — ten private placeholder slots based on the last observed count. Public GitHub deliberately contains no private titles, IDs, emails, prompts or schedules.
2. GitHub Actions — five scheduled workflows detected in public CF-0 `.github/workflows/` source. A cron in GitHub source is **not** a current running-state assertion.
3. Windows — the Fast Lane, CF-0 Relay and optional HP Bridge, each marked owner-local state unverified. Local schedules can be present even if the computer is turned off or not signed in.
4. AUTO-08 — keyboard-first, one-tab continuation code in `automation_200/continuation_keyboard/`, not a live panel executor.

**All Start/Pause/Resume/Emergency-stop controls and the master switch are deliberately disabled.** This public static web page cannot control ChatGPT scheduled automations, Windows Scheduled Tasks or GitHub workflows without separate supported authenticated adapters. It does not submit `continue` to conversations. The disabled state is intentional, not a green running indication.

The **research shutdown planner** *does* support local in-page staging by checkbox, 'Stage known research tasks', 'Clear staged list', and 'Copy shutdown plan'. **Staging only creates a draft for review** and does not stop, disable, update or cancel anything. Grant monitoring and core operational workers are not automatically selected by that research button. Verify live state before actually shutting down tasks through their separate authorized controls.

### Optional private ChatGPT automation names

Do **not** commit personal ChatGPT task inventories to public CF-0. A user can choose a local JSON file in the automation center, parsed in browser memory only (64 KiB maximum; no upload, network request or persistent local storage), with format:

```json
{
  "schema": "cf0.private_automation_inventory.v1",
  "automations": [
    {"id": "private-task-1", "title": "Example research brief", "is_enabled": false, "research": true}
  ]
}
```

The import is a **dated owner-supplied snapshot**, not a live API. Only sanitized titles and reported enablement are displayed; imported IDs, prompts, links, credentials and extra properties are ignored. 'Clear imported names' drops the in-memory copy. Without an import, ten numbered placeholders are shown; that count may become stale.

**Historical AUTO-08 note:** The earlier `/continue-control/` panel described above was reverted in [revert commit 7ca4e6c](https://github.com/whoiwts110217-creator/CF-0/commit/7ca4e6c6851ce0d7916f826e9a3f4753cb6e6118) when the user requested restoring the original dashboard. The separate keyboard runner was subsequently merged in [PR #32](https://github.com/whoiwts110217-creator/CF-0/pull/32). Do not treat the historic panel URL as deployed or operational. The new control center preserves the restored dashboard and introduces no unauthorized execution pathways.

Tests: `node --test automation_200/mission_control/tests/*.test.mjs`. Source UI and tests do not independently prove account authentication, running status, an HP process, or a real pause. The owner may need to refresh GitHub Pages to see the current deployment.

## Complete workflow inventory correction and severity audit — November 9, 2026

The [master controller source audit](../../docs/MASTER_CONTROLLER_AUDIT_2026-11-09.md) found a **High** inventory regression in the initial automation controls UI: it listed five GitHub cron workflows but omitted fourteen other public workflows triggered by push/PR/manual dispatch. The corrected inventory covers **all 19** existing `.github/workflows/*.yml` files (5 cron-scheduled, 14 event/manual) in the same control center. The 14 event/manual jobs are collapsible to keep the first screen readable.

`tests/controls.test.mjs` now compares inventory IDs and trigger classes against actual repository workflow files. That is source parity only, **not** proof a workflow is enabled, currently executing, or controllable by the public site. Ten ChatGPT private task placeholders, three documented Windows tasks, and one keyboard-only AUTO-08 source runner bring the dated source-model inventory to **33** known entries. No provider-wide completeness claim is made for private ChatGPT or physical Windows.

The operator's [narrowed master prompt](../MASTER_OPERATOR_PROMPT.md) governs next steps: (1) maintain inventory completeness and precise status provenance, (2) simplify overview into Now / Control / Evidence, (3) connect one authenticated adapter with read-back and rollback at a time, and (4) keep research shutdown staged rather than falsely claiming a pause. The prompt's amendment is recorded as PCE-006 in [approval bin](../PROMPT_CHANGE_BIN.md) and [append-only log](../PROMPT_CHANGE_LOG.jsonl). No original dashboard functions, schedules, HP actions or finance actions were altered.

## AUTO-08 existing Chrome tab adapter (source/owner installation, November 9)

An optional [owner-local Chrome extension](../continuation_chrome/) is now the preferred AUTO-08 **existing-tab** adapter. This is separate from the earlier Playwright CLI that launches its own Chrome profile. Its limited `tabs` / `scripting` / `debugger` capabilities allow it to query the user's *already-open* ChatGPT tabs and target exactly **one** owner-selected tab ID. It neither opens new tabs nor uses mouse coordinates. Keyboard input is sent through Chrome's debugger protocol, and the worker watches in-page overlays, JavaScript alerts, tab detachment, navigation, rate limits and unknown outcomes.

When manually installed via Chrome's developer-mode **Load unpacked**, a matching local content script can decorate just the AUTO-08 row in this GitHub Pages controller with tab count, local runner status, and owner-clickable Start / Resume / Stop for **that single adapter only**. Without an installed/authorized extension, the row remains disconnected and the global master switch remains disabled. No public host obtains Chrome secrets, personal chat transcripts or remote command privileges through the GitHub Pages site. The extension stores its checkpoint in its own owner-local Chrome storage.

**Status:** source, mock Chrome integration test and unit tests; **no actual signed-in Chrome/ChatGPT smoke test has been performed by this GitHub commit**. Known info overlays are dismissed by keyboard Escape; alerts are dismissed; unfamiliar, security, payment, sign-in or confirmation prompts are never automatically accepted. It cannot detect or control unrelated Windows CMD/UAC windows: only the selected Chrome tab and known Chrome popup-tab events. Current Chrome is required and the `debugger` permission triggers a visible Chrome warning.

[Install instructions and limitations](../continuation_chrome/README.md) · [Chrome extension manifest](../continuation_chrome/manifest.json) · [Chrome source tests](../continuation_chrome/tests/) · [AUTO-08 owner contract](../../docs/AUTO_CONTINUATION_CONTROL_2026-11-09.md).


## Optional Brainrot → Brainpower lesson overlay (November 9)

[Learning lab](https://whoiwts110217-creator.github.io/CF-0/mission-control/#learning-lab) is an **opt-in** source-only mini-quiz in the existing dashboard. It teaches receipt attribution, funding verification, mathematics evidence and preserving failed tests using game-style mission copy. The code lives in `dist/gameful.mjs` (bounded facts) and `dist/gameful-ui.mjs` (DOM-only interaction), with `tests/gameful.test.mjs`. It has no account connection, telemetry, localStorage, random rewards or modification to CF-200 data. Correct quiz answers are local answers, not business or research achievements. This feature is a first prototype, not demonstrated learning efficacy. [Pilot method](../../docs/BRAINROT_TO_BRAINPOWER_2026-11-09.md) · [Universal continuity](../../docs/UNIVERSAL_CONTINUITY_CONTRACT.md). Existing controls, source evidence and AUTO-08 contracts remain unchanged.


**v0.2 remix follow-up:** The optional lesson now asks a second differently worded application question after each initial answer, with both true and false keys. [Automated source and continuity checks](tests/gameful.test.mjs) passed in [CI run 42663949373](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42663949373), and the [Pages build](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42663949334) passed. Actual device interaction and educational improvement remain unproven. [Evaluation protocol](../../docs/BRAINROT_LEARNING_PILOT_PROTOCOL_V0_1.md) describes how to test those claims responsibly without turning the page into a tracking product.


## Learning lab Plain / Playful demonstration — v0.3, November 9

The optional [learning lab](https://whoiwts110217-creator.github.io/CF-0/mission-control/#learning-lab) now offers **Plain** (neutral evidence exercise) and **Playful** (gaming-style mission) presentations. The [single factual mission source](dist/gameful.mjs) is unchanged. A [pure presentation adapter](dist/gameful-modes.mjs) varies only headings, instructions and feedback copy; [browser UI](dist/gameful-ui.mjs) locks selection while a run is open, and stores nothing. [Source parity tests](tests/gameful.test.mjs) and [DOM simulation test](tests/gameful-ui-dom.test.mjs) check content parity, mode lock/reset and absence of account/storage capabilities. No participant assignment, live collection, or learning-effectiveness claim exists. The [evaluation protocol](../../docs/BRAINROT_LEARNING_PILOT_PROTOCOL_V0_1.md) distinguishes this demo from a randomized study; [continuity contract](../../docs/UNIVERSAL_CONTINUITY_CONTRACT.md) preserves the existing project identity and parent links.

**Deployment evidence:** see workflow runs after these commits; GitHub CI source checks and Pages success are separate from a real iPhone UI inspection. No HP permissions, automation schedules, or CF-200 registry updates are implicated.

## Responsive keyboard smoke check — November 9

The [dependency-free Chromium smoke script](tests/browser_smoke.mjs) is called by the [Mission Control CI workflow](https://github.com/whoiwts110217-creator/CF-0/blob/main/.github/workflows/mission-control-access-tests.yml) and uses the real local dashboard files, no external control adapter. It emulates a 390×844px mobile viewport, checks overflow, keyboard Tab/Enter answer selection, explanation focus and identical source facts across Plain and Playful. [Passing CI run 42668440686](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42668440686) showed 35/35 source tests and a passing browser smoke. The previous failed key-synthesis check and correction are in [continuity](../../docs/CONTINUITY.md#november-9--mobile-width-chromium-browser-acceptance-and-keyboard-repair). **This does not prove physical iPhone Safari or VoiceOver**, and no new signed-in account/HP behavior was enabled. Locally, use `node tests/browser_smoke.mjs` where headless Google Chrome is installed.

## iPhone-like viewport hardening (v0.4, November 9)

The optional learning lab has ≥44px touch targets (including source links), a ≥16px mode selector, clear focus outlines and narrow-screen stacking. [Browser smoke](tests/browser_smoke.mjs) now covers 320/360/390/430px, measures all visible learning-lab controls, checks **full document horizontal overflow**, and verifies intact disabled master-switch evidence and unchanged educational content. Both the learning lab and existing status badges/labels are now allowed to wrap on narrow screens; none of the original automation controls, status data or permissions changed. [Strict GitHub CI run 42670072384](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42670072384) **passed**. This is Chrome/Chromium width emulation and browser keyboard testing, **not a real iPhone Safari or VoiceOver accessibility certificate**. [History/rollback](../../docs/CONTINUITY.md#november-9--brainrot--brainpower-v04-narrow-phone-hardening) · [UCC-001](../../docs/UNIVERSAL_CONTINUITY_CONTRACT.md).


## Readability / public count display v0.5 (Nov 9)

The optional Brainrot → Brainpower quiz offers **Larger lesson text** without saving settings or altering grading. The dashboard responds to increased-contrast/forced-colors media preferences. [DOM tests](tests/gameful-ui-dom.test.mjs) verify that toggling size preserves the current claim; [browser smoke](tests/browser_smoke.mjs) includes large-text state and high-contrast checks in the existing four-width Chromium procedure. A [hosted browser walkthrough](https://agent.tinyfish.ai/runs/072a04d9-a7a5-4d1f-90b3-c7f0794e5c4f) observed the published checkbox working. That is **not** a physical iPhone or screen-reader certificate.

The **GitHub workflow count** in the separate automation control center is now rendered from `controls.mjs` via `controls-ui.mjs`, not hardcoded in the static HTML. The source inventory in the observed release listed 21 workflows (5 scheduled / 16 event/manual); the public master switch remained disconnected. Unreconciled older CI runs with a stale 20-workflow expectation are recorded in the [continuity file](../../docs/CONTINUITY.md#november-9--brainrot--brainpower-v05-readable-text-and-public-source-count-continuation). Source count is not live running state, nor a new remote-control permission.


**Latest passing engineering evidence (v0.5):** [CI run 42673680552](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42673680552) — 43 Node source tests passed and the headless Chromium responsive/keyboard/contrast smoke passed on commit `e9882d0f1df8bd0aeeff90d7ab76ea3f6d8cf056`. This resolves the earlier *provisional* CI status of the same feature while retaining the historic failing tests. The [live public browser run](https://agent.tinyfish.ai/runs/072a04d9-a7a5-4d1f-90b3-c7f0794e5c4f) independently observed the new readable-text option; neither constitutes physical iPhone Safari/VoiceOver certification.

## Cross-project inventory verification — November 9, v0.5.1

A new [iPhone Skill Foundry PR/manual test workflow](../../.github/workflows/iphone-skill-foundry-ci.yml) increased the repository to **22 GitHub Actions workflows (5 scheduled; 17 event/manual)**. The [source-only controller inventory](dist/controls.mjs) now includes it, and [controls.test.mjs](tests/controls.test.mjs) strictly checks IDs and triggers against **every actual workflow file** instead of trusting an obsolete fixed total. This changes only public documentation/display and regression checks; no automation is activated, linked, stopped, or authenticated.

**Evidence:** [passing source + phone-width browser CI 42674408404](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42674408404), [successful Pages deployment 42674408782](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42674408782), and [live read-only browser verification](https://agent.tinyfish.ai/runs/b73eb15b-dbf7-4559-880d-3ebe4d388317) showing 22/5/17, the additional row, a DISCONNECTED master and functioning Larger Lesson Text. Prior 21-count statements remain historically true of older source snapshots, not the current total. [UCC-001](../../docs/UNIVERSAL_CONTINUITY_CONTRACT.md) and [full event/rollback](../../docs/CONTINUITY.md#november-9--v051-cross-project-workflow-inventory-reconciliation) govern the next run; physical iPhone Safari/VoiceOver is still not independently checked.

