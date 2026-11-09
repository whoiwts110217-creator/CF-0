# CF-0 Mission Control

A read-only dashboard for Kiara Lynn Rose Smith’s Caveman Focus. It reads public CF-0 files and links back to the authoritative registry, mission board, receipts, and operating prompts.

## Source behavior

- The dashboard resolves the current main commit, then reads the registry, owner capability contract, continuity summary, fixed health report and documented ping pair at that one commit.
- The verified count comes from individual registry statuses. A checkpoint appears when the dated continuity summary agrees with the registry.
- A public ping is matched by request ID, canonical request digest and completion payload. The health row reports file availability. Windows Scheduler correlation needs independent evidence.
- The [GitHub Pages dashboard](https://whoiwts110217-creator.github.io/CF-0/mission-control/) bundles a generated baseline with registry progress, tool IDs and source status, the public ping pair when available, and health-report availability at its build commit. A successful refresh replaces the view with the current public commit.
- **Show restricted:** the work-order view distinguishes verified, source-work candidate, physical HP, owner-local installation/evidence, and unverified dependency states. The toggle shows/hides the held rows without deleting them. Classification applies to the public registry and does **not** include private runtime overrides, so a source-work candidate is not execution authorization.
- **Tools and task power:** the tool table reads the version-pinned owner capability contract, distinguishing source-present public relay and documentation from the historical `open_notepad` regression. These are capability descriptions, **not** proof of physical deployment or permission to extend the relay. The L0/L1/L3 labels are descriptive scopes, not user-adjustable powers. External account, finance, shell, and private data permissions are outside this public source inventory.
- The application reads public GitHub URLs without authentication or write access.

## Development

Serve the dist folder with a static web server. The source distribution reads GitHub directly. Hosted packaging also includes a generated dist/snapshot.json baseline and its pinned commit.

Run the model and GitHub-loading tests using this command.

    node --test tests/*.test.mjs

## AUTO-08 Continuity Control (source prototype, November 9, 2026)

The [Continuation panel](https://whoiwts110217-creator.github.io/CF-0/mission-control/continue-control/) is a linked view in the existing Mission Control site. It adds an original dark, pale-blue reflective-jacket-inspired interface; explicit primary/secondary account selection; local-only import of conversation IDs/titles from a user-selected JSON export; local private checkpoint download; a copyable Work recovery handoff; and a clearly labeled manual fallback. No raw chat content is uploaded by the panel. Private checkpoint files must remain private.

**Automatic master switch: DISCONNECTED.** The static site cannot access personal ChatGPT sessions or send messages. The browser UI deliberately disables the switch until a separately authorized supported executor exists; it must not be described as functioning continuous account autonomy. The separate source-level `continue-control/loop.mjs` implements a bounded, serial adapter contract: send exactly `continue`, wait for the adapter to confirm the full response completed, then advance, with stop, unknown-result hold, and per-pass duplicate prevention. Unit tests cover the contract; they do **not** prove any real ChatGPT conversation was controlled.

See [owner intent and acceptance requirements](../../docs/AUTO_CONTINUATION_CONTROL_2026-11-09.md) and [PR #28](https://github.com/whoiwts110217-creator/CF-0/pull/28). The approved HP public-relay actions and all original CF-200 dashboard data remain unchanged.
