# AUTO-08 — Local v1.3 extension audit and one-tab review candidate (2026-11-10)

**Continuity:** AUTO-08 / CF-CORE / UCC-001 / CF-MESH-001, related to Mission Control and CF-200. **Evidence:** private owner-Library extension *candidate* inspected and simulated locally; no live authenticated HP/Chrome acceptance.

## Do not confuse the two implementations

The owner-local **Caveman Focus — Master Continuation Switch v1.3.0** dashboard has `02 / Eligible conversations`, `SAVE CHAT LIST`, `Strict serial` and `START SWEEPS`. The repository's separate public `automation_200/continuation_chrome` **v0.1.6** has `Start imported sweep` and a different state/permissions model. Do **not** treat these as interchangeable, install both simultaneously or migrate checkpoint state by assumption.

## Observed defect, verified locally

The saved v1.3 source's `prepare` stage calls `chrome.tabs.create` for any eligible conversation not already open. Busy/uncertain conversations may remain open. Thus a 17-chat source test saying "no tab explosion" is **not** proof of the owner's required **one selected existing ChatGPT tab**. The source also submits via in-page send-button `click()`, **not** keyboard-first focus/type/Enter. Three synthetic v1.3 smoke tests passed on November 10; none is a live signed-in account test. We could not inspect the actually installed HP extension or see user account state.

## New local review candidate (not installed or merged)

A separate **v1.4.0 one-existing-tab candidate** was built as an isolated, reversible source artifact, with original v1.3 intact. It requires an explicit pre-existing working-tab selection, navigates only that tab via `chrome.tabs.update`, refuses invalid/missing target tabs, and checks the working tab before navigation for owner drafts, active generation, uncertain previous sends and wrong conversation URLs. Unresolved states **pause** without navigating away. The candidate refuses fast submission across multiple conversations, where immediate navigation could interrupt generation, and retains the old candidate's permission scope.

**Fresh local synthetic tests passed:** one-chat exact send/completion; **17 chats × 2 passes, 34 completions using the same one tab ID, no conversation tabs created or closed**; strict-serial waiting; timeout->paused/pending; resume blocked until prior reply confirmation; draft/busy protection; missing-tab and navigated-away detection; multi-chat fast mode refused. JS syntax and ZIP integrity passed. These are **mock tests**, not deployment, and neither proves reliable keyboard Enter nor exactly-once behavior under arbitrary Chrome crashes.

**Still open:** trustworthy keyboard-first input (the candidate still uses an in-page send-button click), actual signed-in UI compatibility, verifying the chosen ChatGPT account, owner acceptance on one low-stakes conversation, and any wider sweep. No HP scheduler, ChatGPT account, automation schedule, public v0.1.6 source, revenue state or CF-200 registry changed.

## Owner gate and cross-chat handoff

Keep the installed v1.3 extension unchanged for now. If testing it, choose **one already-open low-stakes ChatGPT conversation with no draft**, Strict serial ON, one pass, five-minute timeout; observe **one** literal `continue` and a **completed** assistant response; then check the dashboard ledger and any extra tabs. Do not expand until the actual behavior is verified. Before *any* candidate upgrade, STOP, export/privately back up the old ledger and installed folder, and avoid a second active extension or storage-key collision.

**Next three:** (1) collect one real owner-observed run receipt, (2) finish and verify keyboard-first one-tab control after reviewing any extra permission, (3) reconcile real browser evidence with Mission Control and public AUTO-08 continuity before authorizing multi-chat sweeps. Public-safe reporting only: never publish raw chat URLs, transcripts, browser identities, tokens or owner-private ZIPs.
