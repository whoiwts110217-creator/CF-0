# CF-SPIDER-001 — Spider 3.3.3-R1 Windows preflight compatibility hotfix

**Evidence date:** 2026-11-13, America/Detroit. **Origin:** two actual owner Windows Python 3.15 preflight logs (no private path or contact details published). This report is public-safe; the patched source ZIP is **owner-private** and supplied separately in ChatGPT. **Creator/developer:** David Smith; **designated intended owner/beneficiary:** Kiara Lynn Rose Smith (not proof of legal transfer).

## Owner-reported red preflight

1. `tests/test_slowloris_bare_lf_and_regular_chrome_0030.py::test_55...` expected an HTTP 408 while dripping partial headers. Windows reported **ConnectionAbortedError [WinError 10053]** from `socket.recv_into` and an unhandled request-handler traceback.
2. `tests/test_v33_canonical_manifest_and_windows_harness_0015.py::test_40...` found **93 actual files** against `file_count=92`. Prior interrupted/failed preflight creates a `SPIDER_FRESH_TEST_RESULT_LOCAL.txt` in the hash-checked source tree; Windows Explorer metadata or test caches can also pollute source enumeration. The owner log did not reveal the exact extra path, so cause was reproducible as a release-workflow defect, not established as the unique file on that HP.
3. Original launcher **correctly refused installation and GUI launch** when preflight failed; it did not overwrite the existing Spider.

## Corrective source candidate — 3.3.3-R1-WinFix

- Two local HTTP server handlers now catch **ConnectionAbortedError** as peer disconnect, avoiding console traceback without removing slowloris monotonic-deadline enforcement.
- The *specific* incomplete-request regression permits WinError **10053/10054** as a Windows transport result while still requiring 408 for POSIX and requiring a follow-up healthy **200 OK**. Other socket errors and unexpected 200 responses fail.
- Strict manifest inventory explicitly ignores known disposable artifacts (`__pycache__`, `.pytest_cache`, `desktop.ini`, `Thumbs.db`, `SPIDER_FRESH_TEST_RESULT_LOCAL.txt`), while still **failing on untracked source files**. No blanket bypass of unknown Python/source files.
- Preflight now keeps failure details under the per-user temporary `CavemanFocus/SpiderPreflight` directory, **outside** the immutable release root. Removed packaged `.pytest_cache`; manifest regenerated for exact new contents. Separate new extraction folder required: do not overwrite the old package/install.

## Independent candidate checks (Linux source only)

| Check | Result |
| --- | --- |
| New ZIP SHA-256 | `eed9802fb8c80d9ef5816811609e6c33fcdd33d78049732687f0bb0449353617` |
| ZIP size/entries | **270,597 bytes; 90 entries** (89 hashed source files plus manifest) |
| Manifest integrity | **89/89 hashes verified** |
| Python compile | **73 files compiled** |
| Full clean-source preflight | **277/277 tests passed**, 35.234 s (Python 3.13.5 on Linux) |
| Fresh ZIP extraction and manifest/harness | **Passed**, ZIP CRC passed |
| Generated-file emulation | Existing local log and `desktop.ini` ignored as intended; untracked Python source still rejected |
| Physical HP Windows Python 3.15 | **NOT YET VERIFIED**; owner retest required |

## Next owner action and privacy boundary

Extract `CF0_Spider_333R1_Windows_Preflight_Fix.zip` to a **new directory**. Run **`START_VISUAL_SPIDER.cmd`** there. It verifies source and tests before opening the real animated desktop UI, and does not auto-activate Chrome. If it fails, provide only the last failure/error lines, without publishing personal Windows paths or tokens. If the GUI opens, test TRACK ACTIVE WINDOW → WALK TO MINIMIZE on a disposable Notepad window with owner approval, then STOP. Roll back by closing the new candidate and using the previous untouched Spider.

**Relay coordination:** the existing private ChatGPT↔Gemini Google Docs mailbox was updated with owner-directed priority switch at messages `CF0-RELAY-0058` and `CF0-RELAY-0061`. Those are *document writes*, not proof Gemini read, worked or returned. Gemini/other workers were asked to review the exact Windows-specific fixes instead of independently rebuilding a competing release. No Macro payment or external AI subscription is required.

**Still outstanding:** actual Windows 3.15 run, native HP input/action verification, signed-in Chrome/AI provider handoff, general screenshot semantics, and safe approval boundaries for generated commands. The ZIP and full owner logs are not published here.

Related: [3.3.3-R1 reconciliation handoff](SPIDER_333R1_RECONCILED_SOURCE_HANDOFF_2026-11-12.md) · [source version audit](SPIDER_SOURCE_VERSION_RECOVERY_AUDIT_2026-11-12.md) · [current gateway](CURRENT_SOURCE_GATEWAY.md).
