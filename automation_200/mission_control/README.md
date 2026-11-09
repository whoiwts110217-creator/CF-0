# CF-0 Mission Control

A read-only dashboard for Kiara Lynn Rose Smith’s Caveman Focus. It reads public CF-0 files and links back to the authoritative registry, mission board, receipts, and operating prompts.

## Source behavior

- The dashboard resolves the current main commit, then reads the registry, owner capability contract, continuity summary, fixed health report and documented ping pair at that one commit.
- The verified count comes from individual registry statuses. A checkpoint appears when the dated continuity summary agrees with the registry.
- A public ping is matched by request ID, canonical request digest and completion payload. The health row reports file availability. Windows Scheduler correlation needs independent evidence.
- Hosted builds include a generated baseline snapshot so the dashboard can show an attributed count when GitHub is unavailable. A successful refresh replaces the view with the current public commit.
- **Show restricted:** the work-order view distinguishes verified, source-work candidate, physical HP, owner-local installation/evidence, and unverified dependency states. The toggle shows/hides the held rows without deleting them. Classification applies to the public registry and does **not** include private runtime overrides, so a source-work candidate is not execution authorization.
- **Tools and task power:** the tool table reads the version-pinned owner capability contract, distinguishing source-present public relay and documentation from the historical `open_notepad` regression. These are capability descriptions, **not** proof of physical deployment or permission to extend the relay. The L0/L1/L3 labels are descriptive scopes, not user-adjustable powers. External account, finance, shell, and private data permissions are outside this public source inventory.
- The application reads public GitHub URLs without authentication or write access.

## Development

Serve the dist folder with a static web server. The source distribution reads GitHub directly. Hosted packaging also includes a generated dist/snapshot.json baseline and its pinned commit.

Run the model and GitHub-loading tests using this command.

    node --test tests/*.test.mjs
