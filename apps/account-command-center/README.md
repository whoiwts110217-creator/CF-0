# Account Command Center iOS — feature build

This branch adds a native SwiftUI iPhone source archive for CF-0. It does not replace Mission Control, modify existing HP/CF-200 schedulers, or enable AUTO-08.

Archive: apps/account-command-center/CF0_Account_Command_Center_Native_iOS_v0.3.zip
Archive SHA-256: d30c025d1fba019ae59c5011ed5ba7f4d5643f944ac478a8368cd998982ed27b

Offline features after native installation: multiple HTTPS account shortcuts, local-only task drafts, review queue, local STOP, public CF-0 status. A shortcut is NOT an account connection.

Optional private server: GitHub and Google OAuth account links after provider configuration, read-only inspection, approval-gated GitHub issue creation, and separately billed OpenAI developer API planning. Consumer ChatGPT session control is unsupported.

GitHub Actions compiles with macOS and produces an unsigned IPA when passing. An unsigned IPA will NOT install directly from Files or Safari. Signing is required. Mac/Xcode Personal Team device build is one option, or the official Windows AltStore/AltServer approach: https://faq.altstore.io/altstore-classic/how-to-install-altstore-windows . Neither route has been verified on the user's physical iPhone.

Local evidence: Swift syntax parsed, Xcode project plist linted, 9 backend tests passed. This does not certify an Apple SDK build, signed installation, live accounts or automated HP actions.

Continuity: CF-ACC-iOS-001; parent CF-0 Mission Control; UCC-001; existing main kept unchanged; rollback by leaving branch unmerged.

## CI infrastructure diagnostic — November 9, 2026

The first macOS Actions run [42674108840](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42674108840) failed before allocating a job, with GitHub annotation `Internal server error. Correlation ID: 9412ef56-7d1a-474d-9ecd-ad799b9c218e`. This does **not** establish Swift compilation failure. The GitHub failed-job rerun endpoint returned 403 (zero retryable jobs). A new push of this note requests a fresh macOS build. No credentials or automation privileges have been added.
