# Spider Millennium Puzzle — Owner Assembly Contract (revised 2026-11-14)

**Creator/developer:** David Smith. **Intended owner/beneficiary:** Kiara Lynn Rose Smith.  
**Boundary:** This is a **disassembled** visual-code puzzle, not a working or newly merged Spider release. The owner chooses when and how to connect blocks.

## Correct interpretation of the puzzle
- **One useful, independently testable behavior = one puzzle block.** A working calculator is one block, not one block per number. A spider follows the mouse only if real cursor reading, movement, rotation, trailing distance and non-interference can pass the intended behavior contract; separate them further only when each can be independently repaired and verified.
- **Never count a source symbol as a working skill merely because it exists.** The AST map contains **1,289 source nodes** (94 files, 1,007 functions, 181 classes, 7 JS declarations) and 632 mapped dependencies (626 static, 6 hypotheses). Those are not 1,289 finished skills.
- **Do not target an artificial count of blocks.** 500+ may emerge, but completeness and testable boundaries control the count.
- **Never assemble the whole agent automatically.** Maintain code, tests, dependencies, version provenance, permissions, evidence and acceptance state independently; the owner connects final blocks.
- Reuse canonical AST source IDs. SP-* IDs are **behavior aliases**, not duplicates. An alias may reference multiple source nodes; failed whole-skill acceptance stays RED even if one helper works.

## Block colors
- **GREEN** — this precise behavior passed a recorded independent acceptance test **in a specified environment**. Simulator GREEN is not Windows HP GREEN.
- **YELLOW** — source implementation located, no known contract mismatch, but independent acceptance not demonstrated.
- **RED** — known failure, unclear/ambiguous function, unsafe path, missing required subskill, or blocked acceptance. State the **specific reason** and repair action.
- **GRAY** — intended capability with no implementation identified; if it is required now and prevents the owner's intended behavior, show that composite owner block in RED.

## Source-grounded discovery
The v3.3.14 source at `spider/gui_live.py:203-209` animates the floating spider drifting horizontally when working; it **does not read cursor coordinates**. `SpiderDrawing.draw` renders a spider, not a cursor-following engine. Therefore SP-MOUSE-001 and SP-MOUSE-002 are RED, regardless of the fact that a different **Forge v0.4** candidate describes a follow feature. Keep variants separate until their code and environment-specific tests are reconciled.

The Chrome code has distinct **dedicated DevTools-profile** and **ordinary Chrome desktop/UIA** routes. `LocalChrome.start` is not proof of control of existing Chrome; `interact_regular_chrome_ui` describes **unsent draft staging**, not a verified AI message send. Keep the entire ordinary-Chrome owner outcome RED until tested.

## Priority owner blocks (source references validated against AST V2.2)
| Owner block | Required behavior | State | Linked AST source nodes |
|---|---|---|---:|
| SP-MOUSE-001 | Read the real cursor position without changing input | **RED** | 0 |
| SP-MOUSE-002 | Animated spider follows real cursor at chosen distance and rotates correctly without stealing clicks | **RED** | 4 |
| SP-CHROME-001 | Find and open Chrome without corrupting an existing profile | **RED** | 3 |
| SP-CHROME-002 | Detect existing Chrome, active window, browser/profile state | **RED** | 2 |
| SP-CHROME-003 | Inspect a selected Chrome tab without changing its contents | **RED** | 3 |
| SP-CHROME-004 | Propose and execute an owner-approved Chrome action with target/response verification | **RED** | 3 |
| SP-SAFE-001 | STOP promptly halts queued and in-flight actions and prevents stale responses from restarting them | **RED** | 3 |
| SP-SAFE-002 | Verify exact foreground HWND/control identity before any mouse/keyboard actuation | **RED** | 3 |
| SP-LEDGER-001 | Append a tamper-evident evidence receipt and verify chain integrity | **YELLOW** | 4 |

See the [machine-readable owner intent aliases](SPIDER_MILLENNIUM_PUZZLE_OWNER_INTENT_ALIASES_V1.json) for **exact** source-function IDs, acceptance tests, red reasons and repair instructions. All 25 source references were checked against the AST V2.2 inventory. They are static mappings, not runtime evidence.

## Example: refine one red block without creating more slop
```
[Cursor reader — RED: not yet mapped]
              |
              v
[Trailing-distance/motion rule — RED: not verified]
              |
              v
[SpiderDrawing.draw — YELLOW: source found, HP untested]
              |
              v
[User acceptance: follows cursor and does not steal clicks — RED]
```
Repair only the smallest failing meaningful subskill, re-run its test, add dated evidence, and **do not promote the parent to GREEN** until the complete owner acceptance passes. Color evidence can be grouped by code version, simulator/Windows HP environment, and date.

## Collaboration and publication
Gemini's private handoff should audit mappings, work on isolated RED/YELLOW units and return exact source IDs, minimal patches and independent reproducible results. Keep board layout and canonical ZIP unchanged until owner-authorized assembly. Gemini reviews are collaboration proposals until evidence is checked. This public file contains sanitized architecture and test criteria only, **not** the private relay, credentials, private contacts, local profile state or unpublished source code.
