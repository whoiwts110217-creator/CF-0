# CF-0 AUTO-08 — Chrome extension development and distribution readiness

Status: **development guidance only**; not submitted to Chrome Web Store, not installed on the owner's PC by this change, and not live-account tested. Parent: AUTO-08 / P0. Canonical implementation: [continuation_chrome](./README.md). Public bootstrap: [memory bootstrap](../../docs/CHATGPT_MEMORY_BOOTSTRAP.md). Preserve the current Manifest V3 extension, existing checkpoints, single-tab rule, keyboard-only behavior, STOP safety, and explicit owner acceptance gates.

## Chrome team Modern Web Guidance adoption

Source: https://developer.chrome.com/docs/extensions/ai/build-with-ai

On a developer workstation **with Node.js/npm already installed and after owner review**, install the official skills interactively:

```powershell
npx modern-web-guidance@latest install --choose
```

Select `chrome-extensions` and `modern-web-guidance` for the developer's actual coding agent. The installation is **not performed by this GitHub commit**. Do not add paid APIs, install an unrelated agent, or replace the existing AUTO-08 runner. The Chrome DevTools MCP server is optional for isolated developer debugging; the documented default starts a **separate Chrome profile**, so it does **not** establish acceptance in the owner's already signed-in one-tab Chrome profile. Never use a remote debugger to bypass account verification or access private chat content.

## Current manifest permission review (v0.1.9 on this proposal; same permissions as v0.1.8)

- `tabs`: enumerate and validate the uniquely selected already-open ChatGPT tab; stop if multiple ChatGPT tabs or unexpected navigation appear.
- `debugger`: attach Chrome DevTools Protocol to the selected local ChatGPT tab to send keyboard commands; powerful permission requiring explicit owner review and a visible Chrome debugging indicator.
- `scripting`: perform bounded extension-side tab inspection/interaction as implemented; audit call sites before publication and remove if genuinely unnecessary.
- `storage`: retain local account labels, queues, interruption markers, completed IDs, and uncertain-send checkpoints; do not publish these.
- `https://chatgpt.com/*`: narrowly scoped ChatGPT host access; no wildcard host permission.
- Mission Control content script match: `https://whoiwts110217-creator.github.io/CF-0/mission-control/*`; used to bridge owner-local dashboard controls, not a server-side remote command channel. Confirm actual site access requirements and privacy implications before store submission.

These are **draft justifications**, not a declaration of Chrome Web Store policy approval. Review against current source, extension behavior, Chrome policy and user consent before distribution. A broad `debugger` permission warrants special scrutiny.

## Required acceptance sequence

1. Run existing source tests (`node --test tests/*.test.mjs`) and package/manifest parity workflow; record exact commit and run ID.
2. Review every permission and any changed source with the official `chrome-extensions` guidance; keep minimum necessary permissions, no remote hosted extension code or secrets.
3. Owner on Windows Chrome: preserve local checkpoints and install/reload the **existing** extension in a stable unpacked folder. Use one signed-in ChatGPT conversation tab, check readiness **without sending**, then send exactly one `continue`, observe completion, STOP. Preserve ambiguous `maybe_sent` state for manual review.
4. Test STOP, interrupted response, account mismatch, second-tab detection, extension restart, and Mission Control integration with a low-stakes conversation. A source test cannot substitute for these live checks.
5. Only after explicit owner decision to publish: prepare truthful Chrome Web Store listing, permission rationales, privacy policy and data-handling disclosures. Do not submit or create developer accounts automatically.

## Hardware, privacy, and rollback

The owner's low-resource Windows machine is **not assumed capable of running Chrome's on-device AI models**. Modern Web Guidance is a development skill, not a free hosted AI service or a promise of offline AI. Keep current no-paid-dependency path. Never commit Chrome profiles, cookies, credentials, chat exports, personal conversations or local extension storage. Rollback this documentation separately without changing the runtime. Existing AUTO-08 release and maintenance gates remain unchanged.
