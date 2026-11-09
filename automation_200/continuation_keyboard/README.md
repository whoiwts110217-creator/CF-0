# AUTO-08 — Keyboard-first, same-tab continuation (owner-local)

**Source/test implementation; real-account automation not yet verified.** This is separate from the restored original Mission Control dashboard. It does **not** make the public GitHub Pages master switch live, change GitHub schedules, or extend the HP public relay.

## What changed

- Reuses one Playwright `Page` for the entire sweep: `page.goto(conversationURL)` changes the current conversation **in place**. No `newPage()` per chat, `window.open()`, Ctrl+Tab tab hopping, pointer movement, clicks, coordinates, or screenshots.
- Uses keyboard input only: focus the composer, `keyboard.insertText('continue')`, `keyboard.press('Enter')`. Direct URL navigation is faster and more deterministic than searching a sidebar with mouse or keyboard shortcuts; unlike browser tabs, it doesn't accumulate RAM use for each conversation.
- Serially waits for a new user message, a new assistant message, and a stable end-of-response observation before advancing. If DOM signals change or the outcome is uncertain, **stop and require review**, never duplicate-send blindly.
- Uses an explicit selected account and distinct private browser profiles for primary/secondary accounts. `--login` lets the owner sign in once without exposing authentication to the public repo. The runner **cannot independently attest account identity**; verify the selected account before the first live send.
- Writes a private, atomic checkpoint **before** any possible send; Ctrl+C/timeout/unknown state stops further work. Completed chats are skipped on resume in the same pass. New passes require `--pass 2` etc. No infinite repeat or hidden background automation.

## Set up on Windows with an existing Chrome or Edge installation

From this folder (Node.js required), run `npm install playwright` (free; use existing installed browser, not Playwright's bundled Chromium). Do not install on GitHub Pages or the public HP relay.

```powershell
node cli.mjs --account primary --login
node cli.mjs --account primary --queue "C:\private\conversations.json" --dry-run
node cli.mjs --account primary --queue "C:\private\conversations.json" --max 1
# Only after you verify the first chat was sent/completed on the CORRECT account:
node cli.mjs --account primary --queue "C:\private\conversations.json" --all
```

Use `--account secondary` for a **separately signed-in** secondary account. Add `--browser msedge` if you only have Edge; use it consistently for login and live runs. Private browser profiles and checkpoints live under `%LOCALAPPDATA%\CavemanFocus\auto08-private\`. The supplied `conversations.json`/metadata is read locally; do not commit it to GitHub. An export identifies historical conversations; some IDs may no longer be accessible, and the runner must stop rather than silently skip an inaccessible chat. On Ctrl+C, stop/resume is conservative: a potentially sent but unconfirmed chat remains unknown and needs review of the live thread before changing its checkpoint.

### Source tests

`node --test tests/*.test.mjs`

**Not yet demonstrated:** a full real signed-in 17-conversation sweep, UI selector stability on current ChatGPT, independent identity verification, Mission Control's live master switch, or unattended Windows scheduling. An actual browser smoke test with a single selected conversation is the next verification gate. Do not claim that the original dashboard is now controlling chats automatically.
