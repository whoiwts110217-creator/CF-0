# CF-200 checkpoint 029 — evidence review

Recorded: 2026-11-05T17:43:29.403Z

- **CF-026**: Windows GitHub Actions run [42074418183](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42074418183), job 127410672836, passed `test_cf026_spaces_in_python_path`, launching a copied relay from a spaced folder.
- **CF-061**: `relay/cf_public_relay.py` canonical JSON request SHA-256 is checked in the HTTP transport test; CI passed.
- **CF-081**: `ALLOWED = {'ping', 'hp_status', 'sidecar_verify'}`; validation rejects arbitrary shell and nonempty arguments; CI passed.
- **CF-101**: Owner-defined automation > priority-intelligence > finance > other-work ordering is recorded in `docs/OPERATIONS.md` and `automation_200/README.md`.

All 34 relay Python tests passed on GitHub Windows runner for commit c36e236 (same run linked above). The passing worker smoke test runs **on GitHub infrastructure**, not the owner's HP.

## Pending real-HP proof

- Owner's actual HP read/write installation and a matching authenticated return receipt are **not yet verified**.
- New explicit owner-authorized test request: `command_queue/inbox/d016c9f0-838c-4782-a532-c0ee1b68f3d0.json` from commit `3808015`, action `ping`.
- Expected request_sha256: `fa4ab44537551b248e648d3c1e0af353472769697ed3822f983f79f80de7bd8f`. No corresponding receipt existed when checked, so this is not owner-HP execution evidence.
- CF-027 (physical non-admin install), CF-028 (actual 5-minute schedule), and all later HP attestations remain **planned**, notwithstanding source-design tests.

No credentials, confidential machine identifiers, or unrestricted commands are included in this evidence.
