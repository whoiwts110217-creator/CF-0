# CF-0 HP relay: READ + WRITE

**Project:** Kiara Lynn Rose Smith's Caveman Focus  
**Owner-requested function:** phone message in this same ChatGPT account → public-safe job committed to CF-0 → existing HP Python poller → public-safe receipt committed to CF-0 → ChatGPT reads the receipt when invoked.

## What changed

The original `relay/cf_public_relay.py` already supports authenticated receipt publication when `CF_RELAY_GITHUB_TOKEN` is available. The scheduled Windows task did not have that token.

`relay/cf_public_relay_rw.ps1` adds a one-time local setup that:

1. Asks for a GitHub **fine-grained token** restricted to the **CF-0 repository**, with **Contents: Read and write**.
2. Checks the repository identity and makes an actual **public-safe test receipt** in `command_queue/receipts/<uuid>.json` before changing the schedule.
3. Saves the token **DPAPI-encrypted** in `%LOCALAPPDATA%\CavemanFocus\CF0Relay\write_token.dpapi` for the current signed-in Windows account.
4. Updates **the existing `CavemanFocusCF0Relay` Windows scheduled task** to run the relay with the token loaded only in its process environment. The original five-minute trigger and Python SQLite ledger are not reset.
5. Offers status and a disable action that removes the encrypted token and restores the token-free one-way worker.

## One-time setup on the actual HP

The current setup is **`SETUP_CF0.bat`** ([docs/SETUP.md](../docs/SETUP.md)). It asks for the token in a hidden prompt and stores it in the same DPAPI file described below.

1. Download the latest CF-0 ZIP and extract to a **permanent folder**. You can use your existing extracted CF-0 folder, but preserve your original data; do not move the existing SQLite database from your Windows user profile.
2. In GitHub, create a fine-grained personal access token with **ONLY CF-0 selected** and **Contents: Read and write**. Never send it to ChatGPT.
3. Double-click **`SETUP_CF0.bat`**, or the archived **`archive/launchers/ENABLE_CF0_READ_WRITE.bat`**, and paste the token into the hidden Windows prompt.
4. The program should print a public GitHub **test receipt URL**. That proves the HP was able to write to GitHub.
5. Double-click **`archive/launchers/READ_WRITE_STATUS_CF0.bat`** to inspect whether the existing scheduled task is using the new wrapper.
6. Leave your HP powered on and Windows user signed in. A later five-minute poll should write receipts for previously completed local jobs and future approved commands to `command_queue/receipts/`. ChatGPT can read those files using its connected GitHub access.

**No token, no automatic writeback.** Public GitHub does not support anonymous Contents writes. This one-time credential setup is unavoidable for this particular relay architecture. The GitHub token authorizes write access across CF-0, **not only** to the receipts folder; safeguard and revoke it if compromised. The return channel uses only the allowlisted `ping`, `hp_status`, read-only `sidecar_verify`, and `open_notepad` actions. Do not include private paths, bank data, usernames, hidden files or secrets in public receipts.

## Stop writeback without losing read/execute

Double-click `archive/launchers/DISABLE_CF0_WRITEBACK.bat`. This restores the original read-only scheduled poller and deletes the saved credential, **without deleting local task history**. `SETUP_CF0.bat -Uninstall` is different: it removes the schedule and keeps the token.

## Evidence standard

A successful offline test or Windows CI parser proves **source compatibility**, not HP installation. The writeback is proven only after the owner's HP publishes the nonce-tagged test receipt; automatic return is proven after a scheduled poll publishes a saved matching command receipt.

This does **not** make ChatGPT a continuously listening chat message hook, or provide unrestricted access to the HP. ChatGPT dispatches supported tasks when invoked in this account.
