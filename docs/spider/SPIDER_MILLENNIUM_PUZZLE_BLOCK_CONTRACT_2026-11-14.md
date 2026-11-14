# Spider Millennium Puzzle — Public Block Contract

Updated 2026-11-14. Creator: David Smith. Intended owner: Kiara Lynn Rose Smith. Caveman Focus / CF-0.

## Assembly boundary
Spider is **not assembled here**. The owner will manually connect independently reviewed pieces. No monolithic rewrite, unattended execution, or automatic merging. Split behavior only until it becomes a meaningful independently testable unit; never split a proven calculator into buttons merely to inflate the count.

## Evidence colors
- GREEN — independent behavior test passed with evidence and environment recorded.
- YELLOW — implementation located but behavior not verified.
- RED — failed test, unsafe design, blocker, or missing refinement.
- GRAY — intended capability with no verified implementation.

Static syntax/AST analysis is not runtime proof. Never promote a piece to GREEN solely because it compiles or appears in a source map.

## Required record for every block
ID, user intent, behavior contract, source file/symbol/line range, source hash, inputs, outputs, dependencies, side effects, permissions, test command, expected output, observed output, evidence date/environment, status, failure, and isolated repair plan.

## Initial isolated backlog (not verified)
| ID | Block | Starting status | Acceptance criterion |
|---|---|---|---|
| SP-MOUSE-001 | Read cursor position | YELLOW | Reports cursor movement without changing input |
| SP-MOUSE-002 | Animated spider follows cursor | RED | Visible motion follows cursor without stealing clicks |
| SP-CHROME-001 | Launch Chrome | YELLOW | Launches correct browser, reports failure clearly |
| SP-CHROME-002 | Detect Chrome/profile | YELLOW | Finds existing session without profile corruption |
| SP-CHROME-003 | Read active tab | YELLOW | Reports tab identity and visible UI read-only |
| SP-CHROME-004 | Authorized browser action | RED | Requires approval and verifies target before action |
| SP-SAFE-001 | STOP latch | YELLOW | Prevents further actions after STOP, including races |
| SP-SAFE-002 | Window identity guard | YELLOW | Rejects stale/changed target before action |
| SP-LEDGER-001 | Evidence receipt | YELLOW | Records immutable or tamper-evident test receipt |

Statuses above are conservative triage, not new test results. A RED may reflect an observed user-facing failure or unresolved safety issue rather than a newly executed regression test.

## Existing source inventory
AST V2.2 visual board reports v3.3.14 with 94 files, 1,007 functions, 181 classes, 7 JavaScript declarations, 632 dependency edges (626 static, 6 hypotheses). These are source-map counts, **not passing behavior tests**.

## Gemini peer-review handoff
Review one RED/YELLOW piece at a time. Return exact source provenance, minimal proposed patch, independent test, observed evidence, Windows-specific caveats, and whether status should change. Do not merge the whole agent or claim a test passed without execution. Private collaboration stays private.

## Public/private boundary
Public repository contains only sanitized specifications, reviewable code, and evidence safe for publication. Never post credentials, browser profiles, private relay messages, personal contacts, sensitive screenshots, or unreviewed control interfaces.
