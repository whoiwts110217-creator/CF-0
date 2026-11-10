# AUTO-08: Chrome one-tab monitor (owner-local Chrome extension)

This is **source code**, not an installed extension or a tested signed-in Chrome deployment. It is an optional alternative to the older Playwright CLI. It attaches to **one already open Chrome ChatGPT tab** via Chrome's `debugger` permission and uses CDP keyboard commands without any mouse clicks, screenshots, new tabs or public ChatGPT APIs. It does not require a Chrome debugging port, restarting Chrome, a paid API, or a conversation export for the initial one-chat test.

## Install on your Windows Chrome (one-time)

1. Get this `continuation_chrome/` folder from the CF-0 repository or the ZIP. Keep it in a stable local folder.
2. Chrome address bar: `chrome://extensions` → turn **Developer mode** on → **Load unpacked** → select the folder containing `manifest.json`.
3. Keep **exactly one `https://chatgpt.com/c/...` conversation tab** open. Other non-ChatGPT tabs can stay open. The extension fails closed when zero or multiple ChatGPT tabs are present.
4. Select the new **CF-0 AUTO-08** extension icon; choose **primary** or **secondary** account, matching the account you can verify on screen.
5. Click **Continue current chat once**. It sends `continue` to the existing chat, waits for a new answer to stabilize, then stops. This is the live smoke test before larger sweeps.
6. Optional: import a private ChatGPT `conversations.json` export from the popup (local only). Choose **Start imported sweep** and enter a bounded number of conversations. Records/checkpoints stay in extension-local storage and are never published to GitHub.
7. You can also open the existing [Mission Control](https://whoiwts110217-creator.github.io/CF-0/mission-control/#automation-controls) in **the same Chrome browser**. With the extension installed, the AUTO-08 row can show a local tab-check status and enable its **Start/Resume/Stop** actions for that provider only, subject to account/one-tab/unknown-result checks. The global Master switch and other providers remain disconnected.

**Chrome will display a warning when a tab is being debugged.** This is expected with the powerful `debugger` permission. Inspect the source before installation. This extension is not a generic remote-control interface: code limits commands to a uniquely detected `chatgpt.com` tab and to the literal `continue` message.

## What happens when something pops up?

- A visible **informational** overlay with a known heading such as “What's new” or “Keyboard shortcuts” can be dismissed by **Escape** (twice maximum); work continues inside the same tab.
- An ordinary JavaScript `alert` can be dismissed while the run continues.
- Sign-in, account verification, rate limits, CAPTCHA, unknown dialogs, confirmation or payment prompts, a newly created tab, or the selected Chrome tab closing **stop the run** and leave a local reason. No hidden clicks, bypassing security checks, changing accounts, or spamming retries.
- The controller will not close popups, create new tabs, bypass Chrome security prompts, or interfere with non-ChatGPT tabs. Unknown send outcomes remain blocked until reviewed.

## Strict boundaries and limitations

- Not live until installed and tested on the owner’s PC. GitHub CI can test source logic but not a real signed-in ChatGPT session or a Chrome extension debugging session.
- Only one ChatGPT tab is allowed per Chrome browser profile while the runner is active. A second ChatGPT tab causes a stop.
- This is only the AUTO-08 adapter. It does not control ChatGPT scheduled tasks, GitHub Actions, Windows Task Scheduler, finances or other accounts.
- Browser service workers can restart. On restart, a formerly running in-flight attempt is flagged `needs_review` rather than resent.
- ChatGPT DOM selectors and browser behavior can change; on uncertainty, the runner stops rather than claiming a successful answer.
- To pause, use **Stop AUTO-08** in Mission Control or **Pause / Stop** in the extension popup; Chrome stays open. Do not terminate the browser as a routine pause method.
- Existing attempts, selected conversation IDs and account label are saved **locally** with Chrome extension storage; don't publish or share a browser profile. Extension uninstallation can erase this data.
- Pressing `Start` in Mission Control without an imported queue continues the **current** existing chat once. The extension popup operates the imported multi-chat sweep. This keeps a single browser tab, with no second control server or remote listener.

## Automated source tests

`node --test tests/*.test.mjs`

These are pure source-level checks; passing does not establish functioning Chrome on the owner's machine. The public project master controller may still show "DISCONNECTED" if the owner-local extension is not installed or not available in the browser displaying it.

## Interruption recovery / checkpoint repair (November 9 hardening)

- The worker rechecks **exactly one** ChatGPT tab on **every reply-poll iteration**, rather than only at the start of a conversation. A second ChatGPT tab, closed target, unexpected navigation, sign-in screen or unknown modal stops further sends.
- Recognized informational dialogs are dismissed with the Escape **keyboard** key (at most two attempts). The worker must **rescan the DOM and confirm the dialog has disappeared before continuing**; a persistent dialog is a blocker, never permission to type behind it.
- The extension now blocks **queue reimports and account switches while a potentially sent `continue` needs review**. These actions cannot erase an uncertain attempt. The completion list is deduplicated.
- If attachment failed before any chat send was recorded, the popup offers **Clear pre-send blocker** after the owner checks the tab. This only unblocks local state; it does not automatically start a run or approve unfamiliar prompts. If the attempt is uncertain, the popup instead requires the owner to inspect the actual chat and choose `NOT_SENT` or `COMPLETED`.
- A denied Chrome debugger attach releases internal runner state. The existing Chrome session stays open. Closing or reloading the extension while a send is in flight still requires review; this does not claim uninterrupted autonomy.

**Already installed?** After updating this unpacked extension folder, open `chrome://extensions` and use its **Reload** control. Private checkpoints should be backed up before moving/deleting the folder. Stop the runner before reloading; unexpected reload during a send deliberately leaves an uncertain outcome for review.

**Operational limit:** These safeguards are test-covered source behavior. They cannot detect arbitrary **Windows CMD/UAC** popups or verify the owner's real Chrome account; Chrome prompts outside the page and unrecognized dialogs may require human action. The live signed-in one-chat smoke test remains the acceptance gate. Don't interpret a CI green check as that live acceptance.

## Evidence-gated continuation: business reliability hardening (2026-11-09)

The owner requested an original, conservative adaptation of professional durable-workflow practices. No third-party framework or code is imported. The existing Chrome extension remains **owner-local**, **single-tab**, **keyboard-only**, and **not yet verified with a live signed-in account**.

**Side-effect checkpoint.** Each conversation begins with a persisted `pre_send` attempt during navigation and editor focus. Immediately before the first keyboard action, the worker persists `maybe_sent`. If the worker dies before that boundary, it can clear the pre-send attempt and request owner acknowledgement. If it dies afterward, a retry is **blocked** until the owner examines the actual conversation. A `maybe_sent` marker is not proof that ChatGPT received the message; it is a reason not to resend blindly. Legacy `in_flight` attempts remain uncertain, preserving earlier state compatibility.

**Actual acknowledgement.** A new user-turn count alone is insufficient. The extension now requires exactly one new visible user turn and a boolean DOM check that its entire visible text equals literal `continue`; private message contents are not saved in extension state, logs, or GitHub. Only after that check and a later stable assistant response can the conversation be recorded as complete. A changed ChatGPT DOM, hidden/virtualized message, or concurrent human submission may cause a conservative stop. Review the tab; do not bypass it with an unverified automatic retry.

**Account identity is still unverified.** Choosing `primary` or `secondary` is a local label, not a verified ChatGPT login. The owner must confirm the signed-in account before a live test. This patch does **not** claim to authenticate the account, control Safari/iPhone, provide a universal master switch, or establish an unattended sweep.

**Acceptance tests:** `node --test automation_200/continuation_chrome/tests/*.test.mjs`. These simulate the Chrome extension with a mock browser, not a real signed-in session. Verify one owner-approved conversation in the real account and review the visible actual result before broadening the queue.

**Rollback:** revert this branch's `core.mjs`, `background.js` and matching tests. Leave stored `maybe_sent` attempts in need-of-review state rather than silently converting them into safe-to-retry attempts. No remote actions or account changes were introduced.

## Optional no-export sidebar capture (2026-11-09)

The owner can now build an **incomplete but useful private queue** without a ChatGPT export:

1. In the single existing signed-in Chrome ChatGPT tab, keep the sidebar's conversation links visible. Open the CF-0 AUTO-08 extension popup and select the correct account *label* after checking the signed-in account yourself.
2. Click **Capture visible sidebar chats**. The extension reads only currently visible links in the page's `nav` or `aside`; it stores at most 500 exact ChatGPT conversation IDs per capture in the extension-local queue. It does not read or upload transcript contents, call a ChatGPT private API, click links, create a tab or change the page.
3. If the sidebar contains more conversations than it has rendered, use normal owner-controlled scrolling and capture again. Existing queue entries are deduplicated and prior completed IDs remain unchanged. **Zero captured does not mean there are zero chats.**
4. Select a small sweep through **Start imported sweep**. It uses the same queue whether it came from an export or visible sidebar capture; it still reuses one tab and sends the literal `continue` sequentially, subject to all existing safety gates.

**Account safety:** A visible URL and composer alone do not prove that a conversation from the selected account is open. Before typing, the runner now refuses a page with no rendered user/assistant history (`CONVERSATION_HISTORY_NOT_LOADED`). This can also block legitimately empty/temporarily loading or virtualized chats. It is deliberately fail-closed, but not proof of account ownership. The `primary` / `secondary` selector remains a manual label, not authenticated identity. A real signed-in one-chat test is still required.

**Compatibility:** Chrome desktop extension only. This feature does not turn an iPhone Safari or iPhone Chrome web app into a native agent and does not prove it can discover *all* history. No background scan or separate web API has been introduced.

**Verification:** `node --test automation_200/continuation_chrome/tests/*.test.mjs` covers strict link parsing, wrong-host rejection, repeat capture/deduplication, account-label queue separation, no-history refusal and no extra tabs. A passing source test does not prove that the current live ChatGPT sidebar markup exposes the same link structure.

**Rollback:** Revert this branch's extension source, popup and matching tests. The existing private queue/checkpoint state remains local; back it up before uninstalling the extension. Do not erase unknown-send attempts or turn a failed capture into an inferred complete chat list.

## Account-label checkpoint preservation (v0.1.3 · November 9, 2026)

**Fixed failure mode:** Prior to v0.1.3, importing an existing conversation list reset `completed=[]`, allowing previously completed chats to be selected again. Switching the manually selected account label also discarded the prior label's local queue and checkpoints. Both behaviors risk repeated `continue` sends and loss of useful progress.

**Current source behavior:** The extension now preserves the existing completed history when a queue is reimported under the same selected label. It keeps separate queue and completed snapshots for the `primary` and `secondary` labels in the **existing extension-local** `auto08_state_v1` store, and restores them when switching back. This is an additive migration: old extension state with only `account`, `queue`, and `completed` is copied into that label's snapshot on the next switch. There is no new storage permission, cloud sync, exported conversation content, or automatic account login.

**Important limitations:** Account labels are **not** authenticated provider identities; switching the label does not switch the signed-in ChatGPT account. The owner must inspect the real logged-in account and one existing Chrome tab before sending. Current-history replays and an explicit manual `Continue current chat once` are still possible by owner command; this fix prevents accidental duplicates from loss of the batch completion list. An uncertain `maybe_sent` attempt remains review-blocked across account switching and imports. Uninstalling or clearing extension storage can still destroy local checkpoints.

**Verification:** `node --test automation_200/continuation_chrome/tests/*.test.mjs` covers legacy migration, separated labels, reimport preservation and rejection of malformed list inputs; GitHub Actions validates in a synthetic browser environment. Live owner-account operation remains unverified.

**Rollback:** Restore the previous extension version via the Git history of the v0.1.3 changes. Existing `profiles` snapshots are purely additive; reverting to older code loses the ability to switch between them without data loss, so back up the private Chrome extension state locally first and do **not** clear pending uncertain attempts.

## Reliable owner STOP (v0.1.4 · November 9, 2026)

**Verified source defect:** an in-flight asynchronous extension storage write could race with STOP and overwrite the final visible state. A STOP during launch preflight was also not guaranteed to cancel a worker that had not yet attached the debugger. These are correctness problems for the existing owner's Stop/Pause controls, not new requested features.

**Source repair:** writes to the existing extension-local state key are now serialized. STOP sets a synchronous cancellation flag before awaiting storage, including during launch preflight. The worker checks cancellation before keyboard effects and on completion. A STOP before the command boundary stays paused with no uncertain send; a STOP after the `maybe_sent` boundary preserves `needs_review`, which blocks an automatic resend. A verified completed answer remains marked completed even if STOP races with the last checkpoint write. Chrome is left open; no tab duplication or mouse action is introduced.

**Synthetic regression tests:** `node --test automation_200/continuation_chrome/tests/*.test.mjs`. The new `stop.test.mjs` covers STOP during launch preflight, during editor focus, after Enter, and during a delayed completion storage write. A green source test does not prove that Chrome is running on the owner's actual machine or that a session is logged into the correct account.

**Boundaries and rollback:** no network access, new permissions, scheduler, HP command, payment action, private export or authenticated-account discovery. Revert the feature commit if needed while retaining the private extension checkpoint data and manually inspecting any `maybe_sent` attempt before a resend. The `primary` and `secondary` labels remain manually selected and do not authenticate ChatGPT identity.

**Owner-visible startup STOP:** The popup and existing Mission Control AUTO-08 row now enable STOP during the Chrome tab-check startup phase, before debugger attachment. STATUS reports `STARTING_TAB_CHECK` without blocking behind the same potentially slow tab query. The start buttons remain disabled while launching. Source tests cover the status contract and parse the UI scripts; a real signed-in Chrome trial remains the acceptance gate.

## Owner-ready install package and zero-send preflight (v0.1.5, November 9)

**Source/builder:** The existing [AUTO-08 source-test workflow](../../.github/workflows/auto08-chrome-source.yml) now runs tests and validates the manifest before creating the GitHub Actions downloadable artifact `CF0-AUTO08-Chrome-v0.1.5`. This is a ZIP of just the runtime files, `README.md`, and `FIRST_RUN.txt`, built with the Python-standard-library [package.py](package.py). The builder rejects unexpected permissions, host scopes, stale files, missing files and symlinks. No paid API, external installer or Windows privilege elevation is involved.

**Download:** Open [AUTO-08 Actions runs](https://github.com/whoiwts110217-creator/CF-0/actions/workflows/auto08-chrome-source.yml), choose a completed **successful main-branch** run, then download `CF0-AUTO08-Chrome-v0.1.5` from the run's **Artifacts** section. Extract it to a stable Windows folder directly containing `manifest.json`. GitHub may require signing in to download artifacts. Do not install a package from an unverified third-party source.

**First-run without sending:** Open one real existing ChatGPT conversation, select its correct manually verified account label in the extension popup, and press **Check readiness (no send)**. The extension checks that one tab exists; the visible page matches the selected chat; message history and an empty composer are present; and there are no known blockers such as a popup, pending draft, sign-in prompt or active generation. It does **not** attach Chrome debugger, type, focus the composer, navigate, or send any message. Only fixed reason codes (not transcript text, user email or cookies) are returned to the popup. A passing check explicitly says `READY_ACCOUNT_UNVERIFIED` because page readiness is **not** account authentication.

**Next acceptance:** After a passing readiness check and separate visual verification of the intended ChatGPT account, test **Continue current chat once**. Inspect the actual chat for one literal `continue` and a completed response; verify the popup says completed, and test STOP on a later safe trial. Only owner-observed, correctly scoped real Chrome results can establish live acceptance. A GitHub Actions ZIP proves packaging, not installation, account identity or 7-day unattended operation.

**Rollback:** Revert the v0.1.5 source changes via Git history, then repackage and reload the previous version in Chrome. Before changing/uninstalling the existing extension, privately preserve its Chrome-local queue/checkpoint state; unknown send outcomes still need manual review. No account permissions, HP relay actions, external posting, payment or master scheduler are modified by this work.


## Exactly-once keyboard smoke (November 9, 2026)

A new [inert Chromium contenteditable smoke](tests/keyboard-browser-smoke.mjs) exercises the extension's **unchanged** `Input.insertText("continue")` plus `rawKeyDown("Enter")` / `keyUp("Enter")` sequence against a synthetic blank editor. It asserts precisely **one** submitted literal `continue`, one Enter keydown, no leftover draft and no extra char/Enter event. No private chat, browser login, CAPTCHA, ChatGPT account or API is accessed. The [AUTO-08 source workflow](../../.github/workflows/auto08-chrome-source.yml) runs it with local headless Chrome and continues to package the extension.

**Verified source run:** [GitHub Actions 42728127448](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42728127448), on commit `39e811d81a3b8b7ce95eb1397840d5ad6fc7ca8b`, passed **28 Node source tests**, the headless keyboard smoke, manifest/source checks and permission-checked extension ZIP build/upload. This is real *inert-browser keyboard testing*, but **not the owner's signed-in Chrome extension and not a live ChatGPT send**. The previous `rawKeyDown` source sequence was retained because an actual contenteditable fixture submitted once; adding a `char` Enter event without proof could increase duplicate-send risk. See [Chrome DevTools Protocol Input.dispatchKeyEvent](https://chromedevtools.github.io/devtools-protocol/tot/Input/).

**Next acceptance (still blocked on owner-local Chrome):** follow the existing install/preflight instructions above with a deliberately chosen signed-in account, then run the one-chat send on a safe selected conversation and inspect its completion and pause/stop evidence. Preserve local checkpoints and stop on unknown outcomes. This update does not grant remote account access, start AUTO-08 automatically, or alter the separate static Mission Control master switch. Rollback: remove the isolated test and its CI workflow step; do not change `background.js`.


## Optional acknowledged-submit fast sweep (v0.1.6 · 2026-11-09)

**Owner's later explicit correction:** For a broad continuation sweep, do not have to wait for each ChatGPT response to finish; submit the exact literal `continue`, verify the new user turn, and move to the next conversation. This is a **new optional mode**, not a silent replacement of the original completion-verified runner.

In the local extension popup, check **Fast sweep** before **Start imported sweep**. The default (unchecked) still waits for each stable assistant response and records it under **Completed**. The fast mode still performs the exact per-thread loaded-history, no-draft, one-tab and known-blocker checks, persists its `maybe_sent` side-effect boundary, and requires a new visible user turn whose entire text equals `continue`. Once that exact submission is acknowledged, it stores the conversation ID under **Submitted (reply unverified)** and navigates to the next eligible queued ID in the same tab.

**Important distinction:** A submitted message is not a completed answer. Navigating away while generation is active might interrupt its answer; no attempt is made to prove otherwise. The fast-mode checkpoint is independent of `completed` and is excluded from future automatic queue passes to prevent duplicate sends. This checkpoint persists per manually selected account label (which is *not* verified identity); legacy checkpoint records migrate without a reset. An uncertain send is still review-blocked. Current-chat one-shot smoke test remains the older completion-verified path.

Start with **one** owner-approved existing chat on a visibly verified ChatGPT account, then a small bounded batch. Verify the live result before considering this deployed. The source tests include a mocked two-chat queue with no assistant replies and a test that a rerun never resends a fast-submitted chat; GitHub CI is not proof of a live account or iPhone compatibility. No cloud browser charges, API, new tabs, public transcript exports, HP relay permissions or GitHub Mission Control master-switch activation are introduced.

**Rollback:** uncheck the fast option (default safe mode) or revert v0.1.6 source changes. Do not clear the owner's local submitted/completed/uncertain records when reverting; older versions do not understand fast-submitted checkpoints and may re-send those chats. Backup the private local extension state before downgrading, or treat the existing queue as unsafe to replay until manually reconciled.
