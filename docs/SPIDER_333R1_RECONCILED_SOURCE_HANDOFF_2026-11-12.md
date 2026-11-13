# CF-0 Spider 3.3.3-R1 — reconciled code integration handoff

**Date:** 2026-11-12 (America/Detroit). **Evidence:** private source candidate assembled and tested in isolated container; not installed or verified on the owner's HP. **Creator/developer:** David Smith. **Designated intended owner/beneficiary:** Kiara Lynn Rose Smith (no legal ownership transfer established).

## Which branch this is

The primary architecture is **Unified System 3.3.3 Canonical**, not the unrelated Integrated 1.3.1 release branch. This reconciled **3.3.3-R1** is a new optional, side-by-side source candidate; it does not claim to be the reported 3.3.4 build, and does not replace the source or installed files of 3.3.3, WholePC 1.3.4, Integrated 1.3.1 or Desktop 0.15.

### Reused and verified code changes

- From **WholePC 1.3.4**: fuller Windows UI Automation map, native Edit/RichEdit/Scintilla editor detection, restored-window postcondition checks, stronger window HWND/PID/title pinning and sensitive-control checks against both visible name and AutomationId. No password field values are read.
- From **Integrated 1.3.1**: `WindowPilot`, approximate animated Spider walk toward a selected window's titlebar, one separately owner-approved native Win32 minimize and verification with `IsIconic`.
- In original 3.3.3 GUI: added **TRACK ACTIVE WINDOW • 3 SEC** and **WALK TO MINIMIZE (ASK)** to the *existing* animated Tk application, without replacing its existing Screen Eyes, Chrome adapter, bounded reentry, project analysis, ledger, pause or STOP controls.
- Additional regression fixes: block hyphenated sensitive internal names such as `delete-account`; stale async scan results cannot cancel an active newer scan; canceled visual walks release the local action lock after STOP/PAUSE; source launchers and optional setup path use the candidate-specific destination, not the earlier WholePC installation directory.
- New `START_VISUAL_SPIDER.cmd` verifies source integrity and runs tests before launching the existing native animated Tk app with **automatic Chrome startup disabled**. The original 3.3.3 `--gui` command remains a separate browser dashboard, not the new launcher. `RUN_TESTS_ONLY.cmd` also exists.

### Actual source checks

| Check | Result |
| --- | --- |
| Independent Python unittest discovery | **275/275 tests passed** in isolated Linux environment |
| SHA-256 package manifest | **92/92 files matched** |
| Python source compile | **72 files compiled** |
| Isolated Xvfb Tk smoke | Real Tk root and floating Spider window created; walking animation reached its mock destination; cancellation worked; no auto browser connection |
| ZIP clean extraction / integrity | CRC verified; extracted source reverified against manifest |
| Source ZIP SHA-256 | `01128fb46f328f554763be446efb0b5e18b31b9ec49e2f7367c854f12f80a448` |
| ZIP compressed size | 272,629 bytes |

The private ZIP is supplied to the owner in the active ChatGPT conversation, **not as a public binary or executable download**. This public document records only derived hashes, safe test counts and architecture. No private screenshots, contacts, account credentials, transcript, local paths or payment records were published.

### What remains unproven

**No physical HP test**, live Win32 window minimizing, real Windows UIA edit typing, signed-in Chrome/ChatGPT/Gemini exchange, general semantic screenshot understanding, verified keyboard-shortcut diagnosis on a real site, unattended safe source repair or actual external revenue has been demonstrated by this release.

The original 3.3.3 code contains experimental command execution and clipboard autopilot routes with insufficient security boundaries for unattended generated Python/shell. **Do not activate those routes autonomously.** The new default native launcher does not arm `--watch-clipboard`, `--exec-clipboard`, `--autopilot`, or `--live-ui`; this is not a sandbox claim. Do not automate human-verification challenges.

### Exact Windows owner action / rollback

1. Preserve the existing Spider installation; extract the new ZIP into a **separate new folder**. Do not overwrite the old version.
2. On unlocked Windows with Python/Tk available, run **`START_VISUAL_SPIDER.cmd`**. First-run source and tests should finish before the graphical window opens. Browser does not auto-start.
3. Open a disposable blank Notepad window. In Spider, tap **TRACK ACTIVE WINDOW • 3 SEC**; during the countdown bring Notepad forward. Then select **WALK TO MINIMIZE (ASK)** and approve **only that Notepad**. Watch spider movement and check that Notepad really minimizes. Try STOP during a second pending walk; verify it cancels.
4. Inspect the Windows controls map and Screen Eyes separately, with private data closed. No account login or passwords should be copied into the release evidence.
5. To **rollback**, click STOP, close R1, and reopen the prior Spider. No installer runs against prior Spider directories.

**Next engineering gate:** owner-supervised HP acceptance and a formal guarded AI-to-skill execution allowlist with per-action review, trustworthy postconditions and no duplicate Chrome writers. Preserve private evidence and update this public record only with new dated verified facts.

**Continuity:** [Version recovery audit](SPIDER_SOURCE_VERSION_RECOVERY_AUDIT_2026-11-12.md) · [Current Source Gateway](CURRENT_SOURCE_GATEWAY.md) · [master operator](../automation_200/MASTER_OPERATOR_PROMPT.md) · [continuity](../automation_200/MASTER_CONTINUITY_PROMPT.md) · [work prompt](../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md).
