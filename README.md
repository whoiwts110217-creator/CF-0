# CF-0

Caveman Focus (CF-0) is a public command relay.

ChatGPT writes one job file into `command_queue/inbox`. On the Windows HP, `relay/cf_public_relay.py` polls that queue and runs only the allowed commands `ping`, `hp_status`, and `sidecar_verify`. When writeback is configured, the relay writes a receipt to `command_queue/receipts`.

Notepad is currently not supported by this relay.

## What works in this checkout

- The checked-in relay allowlist is only those three commands. Offline tests cover the queue, duplicate handling, and receipt checks.
- A public `ping` job and a matching receipt are in `command_queue/`. That match is a file check. It does not prove the physical HP ran unattended. Record: [docs/CONTINUITY.md](docs/CONTINUITY.md).
- Separate current source from older notes: [docs/CURRENT_SOURCE_GATEWAY.md](docs/CURRENT_SOURCE_GATEWAY.md).

## Install and run the relay (Windows)

Python 3 is required. No extra packages.

1. Clone this repository and keep the folder.
2. One poll: double-click `RUN_CF0_RELAY.bat`, or run `py -3 relay\cf_public_relay.py once`.
3. Poll every five minutes while signed in: double-click `INSTALL_CF0_RELAY.bat` (this runs `relay\install_task.ps1`).
4. Stop that schedule: `STOP_CF0_RELAY.bat`.
5. Offline check, no network: `py -3 relay\cf_public_relay.py ping-demo`.

Do not put secrets in jobs or receipts. Anyone who can commit to `main` can request only the three commands above.

Before changing operating rules, read [automation_200/MASTER_OPERATOR_PROMPT.md](automation_200/MASTER_OPERATOR_PROMPT.md), then [automation_200/MASTER_CONTINUITY_PROMPT.md](automation_200/MASTER_CONTINUITY_PROMPT.md).

## Where archived work went

Nothing in this cleanup was deleted. Side projects and paused workflows are under `archive/`. The previous long README is [archive/README-previous.md](archive/README-previous.md).

Archived here: Dreamkiller and the other concept folders, Spider desktop and Spider puzzle, iPhone Skill Foundry, Link Vault, AI Tracker, Clarity Card, Clarity Brief, Clarity Check, First Drop, the Abund.ai integration, and the AI-agent invitation files.

Still in place: `relay/`, `command_queue/`, `automation_200/`, `continuity/`, `tests/`, `bridge/`, `skills/`, `finance/`, `docs/`, `research/`, `experiments/`, `agent-tasks.json`, and the root `.bat` launchers.

Paused GitHub Actions workflows are in `archive/workflows/`. They do not run from there. To re-enable one, move that file back to `.github/workflows/`.

The public website still publishes the archived pages at the same URLs. The publish workflow builds those pages from `archive/`.

## License

MIT. Copyright (c) 2026 David Smith. See [LICENSE](LICENSE). Some archived third-party files, including the Dreamkiller emulator, keep their own notices.
