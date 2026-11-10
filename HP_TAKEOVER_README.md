# HP Takeover — One-click connection diagnostic

## November 10, 2026 — maintenance pause takes precedence over setup directions

**Current gate:** [Owner-supplied HP maintenance record #95](https://github.com/whoiwts110217-creator/CF-0/issues/95) states that `CavemanFocusCF0Relay`, `CavemanFocusCF0FastLane` and `CavemanFocusSupervisor` were deliberately disabled, the named CF-0 processes were clear after a local stop, 17 existing recovery files were preserved, and disk space was low (previously about 0.96 GB). These are owner-observed scope-limited facts, **not live Windows or machine identity attestation**. The original steps below are historical connection/setup guidance: **DO NOT follow steps 2–5, install/enable scripts, or run `-RunPoll` during this maintenance hold** unless the owner separately approves a reviewed restart.

**One-click read-only status, when at the HP:** In an existing, complete, trusted CF-0 working copy with this update, double-click [`CHECK_CF0_MAINTENANCE_READ_ONLY.bat`](CHECK_CF0_MAINTENANCE_READ_ONLY.bat). It invokes the new `relay/hp_takeover_check.ps1 -MaintenanceAudit` mode. This mode only queries whether the **three named tasks** are `DISABLED`/other/not visible and calculates a coarse local free-disk count and 2 GiB caution flag. It performs **no network request, receipt polling, process stop, install, task mutation, account/token read, copy, cleanup or writeback**. Keep the original maintenance exports and SQLite/credential state untouched. It does **not** check every possible process or prove physical provenance; do not publish personal paths, screen contents or full local logs to public GitHub.

**Interpretation:** `NAMED_TASKS_PAUSED=OBSERVED` means only that all three named Task Scheduler objects were visible and disabled at the instant of that local read; `NOT_ESTABLISHED` means an absent/inaccessible/enabled task prevents that conclusion. `LOCAL_DISK_BELOW_2GIB=YES` is a caution threshold, not a verified installation requirement. A public `relay/health/latest.json` with a new timestamp or the old 32 receipts does **not** override the owner's hold or authenticate a scheduled HP run.

**Owner action boundary:** Running this read-only check is optional until the owner is at the HP; restarting any task, deleting files, clearing disk, updating scripts, changing tokens or installing anything requires a **separately reviewed owner-local decision**. A future authorized restart should preserve current exports, first free and verify disk capacity safely, then establish a specific fresh scheduled task→wrapper→command UUID/digest→receipt chain. Source CI only tests the read-only function on a disposable runner; it does not claim it ran on the owner's HP.


Founder: **Kiara Lynn Rose Smith's Caveman Focus**.

1. Download or update the **complete** public [CF-0 repository](https://github.com/whoiwts110217-creator/CF-0) on the owner's Windows HP; extract it to one permanent folder. Do not overwrite the original Domino Sidecar data directory.
2. Double-click **RUN_HP_TAKEOVER_CHECK.bat**. It checks the Python relay locally, reads the Windows scheduled-task status, checks whether the encrypted return-channel token exists, and runs **one** bounded relay poll. Leave the window open to see SCHEDULE, WRITEBACK_CONFIGURED, and POLL.
3. If SCHEDULE=NOT_INSTALLED_OR_NOT_VISIBLE, double-click **INSTALL_CF0_RELAY.bat**, then repeat the diagnostic.
4. If WRITEBACK_CONFIGURED=False, and you want **public-safe receipts**, double-click **ENABLE_CF0_READ_WRITE.bat**. Enter a GitHub *fine-grained* token for only CF-0 with Contents read/write locally on the HP, **never in chat or a GitHub file**. The installer probes an authenticated write before changing the schedule.
5. Re-run the diagnostic. Verify a fresh receipt under command_queue/receipts/ matches the original request ID and canonical SHA-256. A local POLL=COMPLETED or Windows CI pass is not proof that the same ChatGPT account received a genuine HP result.

This is a **diagnostic**, not a remote Windows shell. The public worker executes only allowlisted ping, hp_status and configured read-only sidecar_verify, and publishes no confidential machine data. The script uses the existing task and ledger; it never registers a schedule, installs services, purchases anything, reads your account password, changes original Sidecar data, or sends private files. Its -OfflineOnly switch runs a local Python ping without network access and is suitable for CI; -RunPoll checks the real queue once.

**Known limitations:** The public CF-0 repository is not appropriate for personal documents or secrets. A separate private GitHub mailbox with explicit authorization is the planned route to broader but still controlled HP workflows. A scheduled task requires the HP to be on and its Windows user signed in. If GitHub writeback is not configured, the relay only saves results locally.

## Windows encrypted-token read fix (November 5, 2026)

Earlier versions read the encrypted DPAPI file with `Get-Content -Raw` and passed its trailing newline into `ConvertTo-SecureString`, which can cause `FormatException`. The updated reader trims only encrypted **file text** before decryption; it does not change, reveal, or trim the actual GitHub token. An offline self-test verifies a disposable dummy token can be encrypted and read back under the same Windows user.

If you see **ConvertTo-SecureString: Input string was not in a correct format**, download the updated CF-0 ZIP, extract to a new folder, and run `RUN_HP_TAKEOVER_CHECK.bat` from the new folder. Do not re-enter or regenerate the token unless the new reader specifically reports an undecryptable/empty credential. The encrypted token remains in your Windows user profile and the task name is unchanged.
