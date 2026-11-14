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
