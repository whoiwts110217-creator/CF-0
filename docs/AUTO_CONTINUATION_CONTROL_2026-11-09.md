# AUTO-08 — Continuity Control master-switch recovery (owner direction, 2026-11-09)

**Status: intent saved; conversation automation not deployed or authorized by this file.** Public-safe design/requirements only. Private chat originals, account sessions, tokens and exports must remain off the public repository.

## Owner intent — preserve exactly
One **Mission Control** panel should show all automation controls, task states, queues, priorities, and execution receipts. The dominant feature is a **single owner-controlled switch** for the signed-in ChatGPT account: visit every eligible conversation, send the literal message `continue`, **wait for that response to complete**, record the result, then advance to the next conversation. After finishing one sweep, continue further passes as configured, rather than opening all chats at once or merely pre-filling messages. The owner explicitly wants genuine execution, not a cosmetic switch or fabricated success log. Account selection must be explicit because two personal accounts are involved.

The conversation carrying further interface details was said to be in the secondary/free account during a separate signed-in cloud-browser session. A previous session reported recovering **95 conversations / 757 messages** there. These figures are *historical, unverified in the present session*; do not publicly publish raw transcripts or assume the cloud-browser session remains accessible. First recovery action in an authorized signed-in Work session: locate the recent chat about **building the auto-control interface** and recover the exact direction before replacing work.

## Required loop semantics

1. **Connect and verify:** explicit account identity selection; authorized first-party/Work integration, if available. Never infer access from having a URL, and never capture passwords/cookies/session tokens into public GitHub.
2. **Discover candidates:** obtain the complete accessible conversation list through a supported authorized means, then show the count and *allow exclusions*. Imported exports may be used for private indexing, but historical exports by themselves are not live chat control.
3. **Arm:** master switch has an actual wired executor; if no supported executor is connected, show **Not connected / cannot start**, never fake a running state.
4. **Serial execution:** for each eligible chat, navigate/open, verify correct thread, submit exactly one `continue`, wait until the response completes or a timeout/error is confirmed, and persist a per-chat receipt. No parallel flood of model runs. Do not send into a different account or a chat currently awaiting human input.
5. **Advance:** move to the next eligible chat only after completion. At the end of a pass, continue a further pass *only* if the user enabled repeat, respecting rate/usage limits and explicit caps.
6. **Stop/pause/restart:** owner kill switch; pause on sign-in loss, rate limits, safety/approval requirements, unavailable tools or unknown outcome; retry only when duplication risk is resolved. Resume from the durable checkpoint without restarting completed chats in the same pass.
7. **Visibility:** selected account, number of chats discovered/eligible, active title/ID, pass, queued/done/skipped/failed, last completion and reason, run receipts and clear **manual vs autonomous** distinction.
8. **Platform boundary:** a static GitHub Pages site cannot read personal ChatGPT history or send messages; the current public HP relay accepts only `ping`, `hp_status`, `sidecar_verify`. Do not silently add browser automation to that public relay. No paid API, scraping, or evasion of safeguards is authorized by this requirement.

## Interface art direction
Use the existing CF-0 Mission Control as the primary home. Dark charcoal/navy background, restrained **electric pale-blue / cyan glow**, structured utility/work-jacket seam shapes, reflective bands, dramatic but readable lighting, and original insignia/linework evocative of an anime emergency-response aesthetic. Inspiration: *Fire Force* jackets and luminous pale-blue accents; **do not reproduce characters, series logos or original art**. Keep primary controls high-contrast and non-decorative: absolutely no false active LEDs, flashy clutter or unreadable gradients. Mobile/iPhone layout matters.

## Work session recovery handoff
In the still-authorized cloud-browser Work session, sign in via the secure takeover if necessary. Search the secondary account for the *specific recent conversation* about the auto-control panel, extract user corrections and UI details privately, compare them with this file, and save a private provenance-linked record. Do **not** send `continue` to every chat as a substitute for implementing the actual control, and do not publicly expose account conversation content. Return exact coverage and the smallest viable supported execution bridge.

## Delivery acceptance
A visually wired **operator panel** is not completion of automatic execution. Completion requires a real signed-in account, a supported executor, a demonstrated small opt-in sweep with stable per-chat completion receipts, safe stop/resume, and permission/rate-limit behavior verified. Until then, label it *design/source prototype*, never *live*.

Related: `automation_200/mission_control/`, `automation_200/MASTER_OPERATOR_PROMPT.md`, `automation_200/MASTER_CONTINUITY_PROMPT.md`, `automation_200/OWNER_CAPABILITY_CONTRACT.json`. Existing CF-200 registry/HP relay and its schedule remain unchanged.


## Owner-local Chrome extension keyboard integration evidence (November 9)

The source-level `continuation_chrome/background.js` still uses **one** keyboard `continue` insertion and `rawKeyDown("Enter")` / `keyUp("Enter")` after saving a `maybe_sent` checkpoint. A suspected Enter delivery mismatch was investigated using **real headless Chromium** and a synthetic contenteditable field (not a private ChatGPT page). Contrary to that suspicion, the original sequence produced exactly **one** submitted `continue`; no key-input change was made to avoid an unnecessary duplicate-send risk.

[New regression smoke](../automation_200/continuation_chrome/tests/keyboard-browser-smoke.mjs) (creation commit [`3f1636b`](https://github.com/whoiwts110217-creator/CF-0/commit/3f1636befb58fff625a490417b7ff5121c9200be)) was added to the [AUTO-08 Chrome source workflow](../.github/workflows/auto08-chrome-source.yml) ([commit `39e811d`](https://github.com/whoiwts110217-creator/CF-0/commit/39e811d81a3b8b7ce95eb1397840d5ad6fc7ca8b)). [Actions run 42728127448](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42728127448) **passed** the **28 existing extension Node tests**, real inert Chromium keyboard integration, syntax/manifest checks, and owner-installable extension ZIP build/upload. This is *real synthetic browser test evidence*, not authenticated owner-Chrome acceptance.

**Remaining critical gate:** owner-selected and visually verified ChatGPT account, installed unpacked extension and explicitly opt-in **one chat** send/ack/complete receipt observed on the actual device. Until that happens, AUTO-08 is not certified live, and the static Mission Control master control stays disconnected. No ChatGPT conversation, account credentials, HP relay or CF-200 registry record was touched by this smoke. The test is reversible independently of the working extension; see the extension [README](../automation_200/continuation_chrome/README.md) for installation and troubleshooting.


**Keyboard-test infrastructure correction (Nov. 9):** a later [red run 42728326511](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42728326511) exposed a test-only Chromium debugger startup timeout despite 28 passing extension source tests. The isolated fixture now uses Chrome's ephemeral `--remote-debugging-port=0`, the `DevToolsActivePort` profile file, longer startup tolerance and diagnostics ([commit `c9136ca`](https://github.com/whoiwts110217-creator/CF-0/commit/c9136ca1d4b4ab697d6728cc767c534a356bc063)). [Rerun 42728716822](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42728716822) **passed** (28 source tests, one literal `continue` submission in inert Chromium fixture, ZIP artifact). The failed run is preserved in [continuity](CONTINUITY.md). Neither test establishes live user ChatGPT control or iPhone support, and the extension's actual send sequence was **not** changed.


## Later owner correction — optional submit-and-advance sweep (November 9, 2026)

The founder explicitly changed the **current sweep preference**: after sending `continue` in an eligible chat, the operator **does not have to wait for the model reply to finish** before moving to the next chat. This supersedes the wait-for-answer requirement **for owner-selected fast sweeps only**; preserve the original completion-verified mode and prior design history as a separate option. Fast mode still requires evidence the exact literal user message was submitted and a durable duplicate-prevention checkpoint. It must not call a submitted chat an assistant-completed chat or claim that navigating away preserves background generation.

Implementation proposal is isolated in the v0.1.6 AUTO-08 Chrome extension branch, with a distinct submitted state; a real owner-selected, signed-in Chrome acceptance test remains open. This public policy update does **not** grant browser sign-in, private ChatGPT data access, payment, extra tab, HP relay command, or remote publishing permission. An iPhone is not a supported Chrome extension host. The third-party TinyFish account balance was exhausted during the earlier Free-account sweep; do not automatically purchase credits, restart billable runs, or call the remaining account conversations complete.
