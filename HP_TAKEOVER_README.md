# HP Takeover — One-click connection diagnostic

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
