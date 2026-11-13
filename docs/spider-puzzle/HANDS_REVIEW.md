# Spider Hands — isolated source-contract audit (v3.3.14)

**Status: ISOLATED-RED, not fixed; original Spider program remains unchanged.**
This review is an independently executable test artifact for the visual puzzle. It verifies *specific source-level behavior* of `spider/hands.py`, rather than inferring capability from method names.

**Source binding:** Spider v3.3.14 ZIP fingerprint `438c442a781b028b1ef8fc336585e540e14dfb5e3828a8d2e8ab35857e2dec24`.
**Evidence:** 4/4 synthetic probes reproduced behavior by compiling only selected method ASTs from the puzzle's embedded source and replacing all OS senders, timing and authority callbacks with mocks. **No Windows PC, actual mouse, keyboard, clipboard or browser was controlled.** These are not physical-HP tests. *The four tests are designed to PASS when a defect is reproduced; green unittest output is not a safety clearance.*

## Red reproduction records

| Puzzle skill | Source line | Trigger in a synthetic test | Observed code-path outcome | Safety implication |
|---|---:|---|---|---|
| `SpiderHands.drag` | 499–530 | STOP/interrupt after mouse-left-down | `LEFTUP` omitted, method reports simulated outcome | May leave a physical button logically held if the preceding Win32 left-down succeeded |
| `SpiderHands.drag` | 499–530 | One intermediate movement fails | Boolean short-circuit bypasses `LEFTUP` | Same unreleased-button risk |
| `SpiderHands.paste_via_clipboard` | 360–392 | Requested `target_window` focus fails, shortcut sender succeeds | Still issues Ctrl+V and can report completed | May paste into another active window |
| `SpiderHands.move_and_click` | 443–475 | Invalid `button='bogus'` | Issues left-click flags, receipt echoes invalid button | Unexpected physical click / inaccurate receipt |

## Reproduce safely

```sh
python docs/spider-puzzle/verify_board.py
python docs/spider-puzzle/probe_hands_contracts.py
```

Both programs use only the Python standard library. The second probe never imports or executes the full Spider package. It parses the static HTML source snapshot, uses synthetic call inputs, and intentionally demonstrates problematic method paths.

## Suggested isolated repairs (NOT applied)

1. **Drag cleanup:** after a successful or attempted LEFTDOWN, always *attempt* LEFTUP in a `finally` path, including STOP and failed/interrupted movement. Keep STOP latched; distinguish original failure from cleanup success/failure in the receipt. Do not let a cleanup click or move run.
2. **Focus-bound paste:** when `target_window` is specified, abort before Ctrl+V unless target HWND/window identity was successfully established, focused and rechecked immediately before actuation; do not rely solely on substring title matching. Apply the same binding discipline to copy operations.
3. **Button validation:** reject any input outside `left/right/middle` before any Win32 event; never silently map unknown buttons to left-click. Preserve truthful receipt status.
4. **Acceptance:** run failure-injection tests with a mock Win32 sender, then narrow physical HP tests with explicit owner consent, STOP and safe target windows. Test multi-monitor coordinates and loss of focus separately.

Do not connect these tiles to automatic Windows actuation solely because they exist in the code-skill graph. The public puzzle now marks the file and these three affected methods as `ISOLATED-RED`. Continue source-level repair on a *separate candidate* first.
