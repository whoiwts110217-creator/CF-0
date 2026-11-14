# Spider Millennium Puzzle — Parts Kit Quality Review
Date: 2026-11-14. Creator/developer: David Smith. Intended owner/beneficiary: Kiara Lynn Rose Smith.

## Scope
A **review only** of an existing, unassembled offline Parts Kit and a separate color-coded board candidate. This is not a Spider installation, automatic merge, or Windows HP acceptance.

## Reproducible findings (isolated Linux container)
- 1,394 ZIP entries; ZIP CRC PASS; 1,393/1,393 recorded content SHA-256 digests matched; no traversal or symlink entries found in the reviewed ZIP.
- Catalog has **1,388 unique indexed code entries**; 36 independent task contracts; 640 catalog dependency edges. The full board's embedded catalog and task records matched the ZIP records.
- Every catalog piece points to a present source excerpt with a matching SHA-256. All task code links and dependency endpoints resolved within the catalog.
- **10/10 included Python unit tests passed**, covering isolated cursor coordinate reading, movement, drawing, simulated overlay placement, work handoff, and static Python project scanning. Tests used simulated windows/coordinates and temporary files. No physical Windows HP execution was performed.
- A separate review-only HTML board rendered in headless Chromium: 36 task cards (7 RED, 29 YELLOW), code catalog count 1,388, six mouse-follow code pieces placed into the visual assembly view, and zero page JavaScript errors observed. The review-only board leaves the original source board and canonical ZIP untouched.

## What colors mean
- **RED** = known mismatch, missing capability, incomplete composite, safety uncertainty, or unverified critical integration. Every RED requires an explicit reason and an isolated repair plan.
- **YELLOW** = source found but its complete intended behavior lacks independent acceptance evidence.
- **GREEN (SANDBOX-TESTED ONLY)** = a directly exercised independent function passed the included isolated tests; **not Windows HP verified**. Even if component pieces are green in the sandbox, their composite task remains RED until real acceptance.
- The review board is a nondeployed, private candidate, not public source; the full code catalog must not be copied into public docs indiscriminately.

## Reproducible HTML serialization risk
One AST V2.2 HTML *variant* contained a literal closing `</script>` string inside a `<script type="application/json">` payload, prior to the intended closing tag. That prematurely terminates the JSON data block in an HTML parser. A separate AST V2.2 Library copy did not have this defect. Future board generation should encode literal `<` as `\\u003c` in JSON placed inside script elements and verify parser boundaries; do not blanket-label every V2.2 variant broken.

## Unverified
- Actual physical HP mouse-follow rotation/offset, Windows click-through layer, mixed-DPI and multi-monitor behavior.
- Ordinary Chrome discovery/inspection/action confirmation on the owner's signed-in session.
- STOP during in-flight actions, exact-window target locking, network/AI send reconciliation, and real external outcomes.
- Browser UI accessibility on the owner's iPhone and native Windows desktop.

## Next controlled work
Keep original pieces disassembled. Review one RED block at a time, attach actual source ID, contract, failing test, minimal fix, test outcome, environment and dated evidence. Do not mark entire Spider GREEN because the Parts Kit integrity and synthetic unit tests pass.

See the [public owner intent aliases](SPIDER_MILLENNIUM_PUZZLE_OWNER_INTENT_ALIASES_V1.json) and [block contract](SPIDER_MILLENNIUM_PUZZLE_BLOCK_CONTRACT_2026-11-14.md) for the nine initial ownership-level behaviors. These reference a different v3.3.14 AST catalog variant, so compare provenance before mapping to the repaired Parts Kit.

## SP-SAFE-002 isolated window-target gate (2026-11-14)

**State: RED for the owner-level behavior; isolated reference helper only.** Built a separate stdlib Python reference module (`sp_safe_002.py`), a 15-case deterministic unittest suite, and an operator-facing README. They are deliberately **not merged** into the Spider runtime or original puzzle board. The ZIP is held in private Spider Working Documents; public publication here covers the safe test contract and evidence, not the owner-only source/catalog ZIP.

- The gate captures foreground top-level HWND, process ID, GUI thread ID, window class, focused child HWND, and child class. A one-use approval ticket is bound to that tuple and expires after a short TTL. The caller provides an actual approval UI callback and an actuation callback; the helper itself sends **no mouse/keyboard input**, changes no focus, and contacts no network service.
- Before callback dispatch, a changed top-level HWND, reused HWND with different PID, changed focused control, expired/revoked/denied ticket, or Win32 read failure prevents the callback from running. It also samples the foreground before and after the internal Win32 inspection to notice a mid-read switch.
- **Observed isolated test result:** Python `unittest discover -s tests -v` on a Linux container: **15/15 PASS**; `py_compile` PASS; ZIP CRC PASS, 3 listed entries. The tests use injected fake foreground probes and a fake clock. One test deliberately switches target *during* a callback and confirms it reports `TARGET_CHANGED_AFTER_DISPATCH` rather than pretending the input was undone.
- **Remaining RED risk:** No pure userspace preflight provides atomic `check foreground + SendInput`; a window can still switch after the final check. Physical Windows HP Win32 API integration and adversarial Alt+Tab/remote-desktop focus tests are **UNVERIFIED**. The helper is not an acceptance pass for SP-SAFE-002 or for live Chrome control.
- Source reference/provenance for intended integration: v3.3.14 `spider/hands.py:562` (`_find_window_hwnd`), `:591` (`focus_window`), `:443` (`move_and_click`). These are *review targets*, **not proof** the reference helper is already integrated. Next task: independently audit the real actuation call path and propose a target-bound adapter; preserve STOP/PAUSE/RESUME and keep all blocks disassembled.

**Evidence:** 2026-11-14, `SP-SAFE-002-GATE-V1`, ZIP SHA-256 `4b29c42db04721effb17bc077e359e90bd5bbada3098db5f349eb1bf041bf708`. Creator/developer: David Smith; intended owner/beneficiary: Kiara Lynn Rose Smith. This is an engineering record, not a statement of completed ownership transfer.

## SP-SAFE-002B read-only source audit, simulated input adapter, and manual visual lab

**Date:** 2026-11-14. **Parent owner behavior:** SP-SAFE-002 remains **RED**. This is a new **nondeployed, independent** child-block review; it is NOT a Spider patch or automatic assembly.

**Source evidence:** Retrieved private user-owned canonical `CF0_Spider_Unified_System_v3.3.14_Canonical.zip` (94 entries; ZIP CRC PASS; archive SHA-256 `438c442a781b028b1ef8fc336585e540e14dfb5e3828a8d2e8ab35857e2dec24`). A SHA-pinned read-only AST audit found these method-local facts:

- `spider/hands.py:591-612` (`focus_window`) invokes `SetForegroundWindow` without checking the actual foreground HWND/control again inside that method.
- `spider/hands.py:443-475` (`move_and_click`) emits multiple mouse input events, without foreground-control identity verification between those calls.
- `spider/hands.py:532-557` (`keyboard_type`) checks STOP in the character loop, but does not read focused-window/control identity in that method.
- `spider/hands.py:360-392` (`paste_via_clipboard`) calls paste even if the optional `focus_window` operation reports failure; its optional Enter step follows paste without target-identity verification.
- `spider/hands.py:499-530` (`drag`) calls `check_interrupt` during dragging but has no foreground-identity readback inside that method. **Method-local call absence does not prove an external controller never checks.**

**Isolated deliverable:** `SP-SAFE-002B` references the previously tested `SP-SAFE-002A` approval/foreground gate and adds a bounded (1–5 event) step sequencer with injected authority, exact-target probe, and fake/supplied input driver. No native driver is shipped; it does not call `SendInput`, change focus, or install. Owner approval is still externally supplied; native integration must not skip it. Receipts distinguish **BLOCKED_BEFORE_DISPATCH**, **BLOCKED_BEFORE_INPUT**, **ATTEMPTED_UNVERIFIED**, **PARTIAL_DISPATCH_UNVERIFIED**, and **DISPATCHED_UNVERIFIED**, never claiming OS-recipient verification from an input count.

**Reproducible isolated tests:** 35/35 Python unit tests passed (earlier V1 tests + new V2 and one static-audit fixture), Python compilation PASS, canonical source audit 8/8 assertions true, candidate ZIP CRC PASS. A separate offline HTML manual puzzle sidecar showed ten movable inspection cards (the extra card depicts Gemini's distinct high-level Hands adapter); Chromium `page.set_content` smoke at desktop 1280px and narrow 390px viewport tested click-to-inspect, manually adding a dashed design link, a fixed focus-switch replay, and no JavaScript errors. The sandbox blocked direct `file://` navigation, so **real local-file, iPhone Safari, and Windows HP acceptance remain unverified**. The code, test results and HTML are private Working Documents; this public note intentionally includes only source-file names/line ranges, architecture, and test evidence.

**Cross-worker reconciliation:** Gemini's separate `HandsTargetBoundAdapter` wraps an entire `SpiderHands.move_and_click`/`keyboard_type` call with a ticket/STOP boundary; its 6/6 synthetic tests were independently rerun with v3.3.14 source in a sandbox. SP-SAFE-002B is a distinct, unintegrated **per-emitted-event** adapter with a fake/supplied driver. They are NOT two deployed implementations of the same working skill; the event interface has yet to be designed, and blindly feeding raw high-level `move_and_click` to the per-event adapter would not check its internal SendInput calls. The private final review ZIP has 13 manifest/asset entries and SHA-256 `1c7c0ab89fc37e41b41d787451ddb3cac3944b90b3c97bfc9c0ca16c04d07a43`. Neither Gemini's code nor the owner canonical archive is copied into this public QA file.

**Remaining RED flaw:** There is no universal atomic `check target then SendInput`. A foreground change or STOP after the final preflight can still cause a misdirected/partial input, including a held-down key or mouse button. **SP-SAFE-002C** is now defined as a separate RED *design contract* for recipient evidence, held-key/button recovery, secure-desktop handling, and seven adversarial acceptance cases; it is not implemented or tested on Windows.

**Attribution:** Creator/developer David Smith; intended owner/beneficiary Kiara Lynn Rose Smith. No ownership-transfer claim.
