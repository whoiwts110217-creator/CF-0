# HP Bridge v0.2.1 — Private mailbox pilot

**Creator:** Kiara Lynn Rose Smith's Caveman Focus. This is the transport *pilot*, not remote control of Windows or a ChatGPT API connection. The existing public CF-0 repository contains code only.

## Setup — on your real HP

1. In GitHub, create a **new PRIVATE** repository such as `YOURUSERNAME/CF-private-mailbox`. Do not change CF-0 itself to carry secret chat files.
2. In GitHub, create a fine-grained personal access token restricted to *only that private mailbox* with **Contents: Read and write**. Do **not** paste the token into ChatGPT, GitHub issues, public repos or screenshots.
3. Download the latest CF-0 ZIP, extract it, double-click `RUN_HP_BRIDGE_DEMO.bat` (the existing offline checks), then `SETUP_HP_BRIDGE_WINDOWS.bat`. The setup will securely prompt for `owner/repo` and your token and **verify GitHub reports the mailbox private** before installing the scheduled task.
4. You can run `HP_BRIDGE_STATUS.bat` to inspect schedule metadata. Run `STOP_HP_BRIDGE_WINDOWS.bat` to stop the schedule. Local logs and encrypted token remain for deliberate recovery.

The setup uses Windows-user DPAPI-encrypted credential storage under `%LOCALAPPDATA%\CavemanFocus\HPBridge`, not a plaintext token file. Only that Windows user can decrypt it. The schedule runs while that same user is **logged in**, including when the console window is closed; it does not run while the PC is off. Windows installer/schedule has not been tested on the owner's HP.

## Test a real request

Once the private repo is connected to ChatGPT's GitHub connector, the owner can ask ChatGPT to create a `ping` request file in `bridge/queue/UUID.json` there, with schema:

```json
{"version":1,"id":"<UUIDv4>","action":"ping","issued_at":<UNIX SECONDS>,"expires_at":<UNIX SECONDS PLUS 3600>,"params":{}}
```

The HP checks the private queue every fifteen minutes and writes a receipt to `bridge/results/UUID.json`. The GitHub connector can then read that receipt **when used again**, or via an explicitly scheduled ChatGPT automation if supported. Creating the request or receipt **does not directly send a message into this specific ChatGPT conversation**. The private mailbox needs to exist before the live round trip can be completed.

### Allowed actions

- `ping`: return a minimal `pong`, with no device identifiers.
- `sidecar_verify`: if a Sidecar directory has been explicitly configured to the worker, run the existing `domino.py verify` read-only check. By default this reports `not_configured`.

Anything else is rejected. No Python, shell, webpage, private chat or JSON job can grant new execution permissions.

### Reliability limits

v0.1 only saw the first ten sorted job files, and fresh jobs could be starved. v0.2 lists the queue up to the GitHub Contents directory limit and skips locally published request IDs before applying the ten-action-per-run cap. A 26-job local simulation drained 10 / 10 / 6 without duplicates. A lost reply acknowledgment can be handled by re-publishing a saved result without rerunning the job. Published IDs remain in GitHub queue history unless an authorized archival step is implemented; if a directory reaches GitHub's 1,000-item limit, the worker deliberately stops rather than silently losing jobs. No blind retries of interrupted local operations.

All code is Python standard-library only. GitHub mailbox visibility and delivery use authenticated HTTPS; local tests used a fake mailbox. No owner Windows credential or private GitHub repo has yet been configured in this chat.

**v0.2.1 Windows correction:** the demo and local ledger now close SQLite database handles after each operation, so Windows can delete temporary directories cleanly. Linux unit tests and authentic original Sidecar inspection passed locally; Windows GitHub CI must independently confirm.
