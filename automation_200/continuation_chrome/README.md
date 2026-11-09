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
