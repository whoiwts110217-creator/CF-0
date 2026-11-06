# CF-0 phone → ChatGPT → HP public command relay

**Founder credit:** Kiara Lynn Rose Smith's Caveman Focus. New-code attribution includes reversible source comments (`cf.attr.v1`). Existing original files are untouched.

## Working communication path

1. In the **same ChatGPT account**, tell the assistant `HP: ping`. A GitHub-connected assistant with write rights to `CF-0` commits one valid request to `command_queue/inbox/<uuid>.json` on `main`.
2. Your HP has a stdlib Python poller that reads the **PUBLIC** GitHub queue over HTTPS (no GitHub login or personal access token required to **receive**). Only `ping`, `hp_status` and configured read-only `sidecar_verify` are accepted.
3. Local SQLite ledger prevents duplicate execution. By default the result is saved **only on the HP**; this is one-way control unless you optionally authorize a restricted GitHub write token for safe public receipts.
4. If owner sets `CF_RELAY_GITHUB_TOKEN` on HP using a token restricted to **CF-0 Contents write**, the HP can post the **public-safe** receipt under `command_queue/receipts/<uuid>.json` for this ChatGPT account to read later. Do not place this token in the repo/chat/logs. Do not use this public relay for confidential status or arbitrary shell commands.

## Run on actual HP (Python 3 available)

Download the full GitHub repo ZIP, extract it to a permanent folder; double-click `RUN_CF0_RELAY.bat`. No additional libraries. The console polls once. Run `INSTALL_CF0_RELAY.bat` to schedule polling every 5 minutes while signed in; `STOP_CF0_RELAY.bat` to stop the schedule. The local SQLite file is in `%USERPROFILE%\.caveman_focus_relay\relay.sqlite3` by default. This prototype does not auto-enable a job on the user's real HP.

## Important constraints

- Public by default for project artifacts; **do not put sensitive data into public commands or receipts**.
- Anyone who can commit to `main` can request *only the three allowlisted actions*. Do not enable arbitrary commands based on public input.
- `ping` and `hp_status` return canned public-safe results; `sidecar_verify` requires explicitly configuring `CF_SIDECAR_DIR` and returns only a small verification summary.
- The native ChatGPT product cannot guarantee a silent/no-reply dispatch when you send a message; responses can be kept terse. Nor does an automation automatically read every conversation message. Dispatch occurs only in a chat turn where the assistant uses its connected GitHub tool.
- A GitHub CI pass is not proof of deployment on the owner HP. Live HP proof requires a fresh command ID and the actual HP ledger/receipt.
- GitHub's Contents API max 1,000 entries means the queue requires archive/rotation before heavy sustained usage. This is a proof-of-control channel, **not yet general AI remote access**.


## Automated cloud-side channel watchdog (November 5, 2026)

The read-only `relay/channel_audit.py` compares public request IDs and canonical SHA-256 digests against public execution receipts. It counts pending/expired requests, invalid requests, mismatched receipts, orphan receipts, and setup probes. It **does not** treat a setup probe, CI pass, or matching public content as cryptographic proof of the physical HP's identity.

The [CF-0 Channel Evidence Watchdog](https://github.com/whoiwts110217-creator/CF-0/actions/workflows/cf0-channel-watchdog.yml) runs hourly and on changes to the public inbox, receipts, or audit code. Open a run's **Inspect live public queue and receipts (read-only)** step to see the JSON counts. The workflow has `contents: read` permission and requires no credential changes or new HP installation.

To run the same check in a local repository checkout, use `py -3 relay\channel_audit.py --live`. It makes GitHub HTTPS **GET** requests only. To run offline classification tests, use `py -3 -m unittest discover -s relay\tests -p test_channel_audit.py -v`. Unanswered commands remain pending or expired until a genuine matching execution receipt is independently observed; this watchdog never simulates one.

## Test locally

`py -3 relay\cf_public_relay.py ping-demo`

`py -3 -m unittest discover -s relay\tests -v`

## Operations

`py -3 relay\cf_public_relay.py make-job --action ping`

`py -3 relay\cf_public_relay.py status`

`py -3 relay\cf_public_relay.py once`

## Proof target

A normal ChatGPT message commits a `ping`; the actual HP sees it without a token and writes a local receipt; the owner provides the ledger output, or a separately authenticated public GitHub receipt appears. Confirm source ID, SHA256 digest and idempotent replay. This has **not yet been observed on the HP**.

## Owner-local, optional automatic health reporting

For a **single reversible activation** without repeated copied diagnostics, see [one-click HP health reporting](HEALTH_ONE_CLICK.md). The controls require the existing HP relay and authenticated writeback already configured; activation does not modify the Windows scheduled task or grant new remote actions. A fresh real HP health report is still needed as proof of unattended publication.
