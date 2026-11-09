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
