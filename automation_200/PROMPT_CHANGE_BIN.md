# CF-0 — Prompt Change & Approval Bin

**Owner-governed queue, public-safe summary only.** This is the place to find proposed prompt changes, the decision needed, changes already made automatically under existing authority, and evidence. It is **not** a grant of permissions and **does not** itself execute anything.

**Owner direction (November 7, 2026):** Improve prompt efficiency when appropriate; keep an explicit bin of approval notes and an auditable record of automatic prompt revisions. The three canonical public prompts must still be fetched from current `main` in order: [Operator](MASTER_OPERATOR_PROMPT.md), [Continuity](MASTER_CONTINUITY_PROMPT.md), [Work](WORK_COPY_PASTE_AUTOMATION_PROMPT.md). This bin supplements them; it never supersedes them.

## 1. Changes requiring explicit owner approval

| Change ID | Proposal | Why approval is required | Status | How to decide |
|---|---|---|---|---|
| PCA-001 | Let an automatic agent edit master priorities, founder/ownership statements, or the owner capability contract | Changes authority and governance | **Needs owner approval** | Reply `Approve PCA-001` or `Reject PCA-001` with the exact limits |
| PCA-002 | Create or activate a cash micro-bounty for agents (even $1–$5) | Financial commitment; current proposal remains unfunded | **Needs owner approval and actual funds/terms** | Reply with approved budget, scope, review and payment terms; a reply alone does not establish funding |
| PCA-003 | Add new autonomous outbound posts, direct messages, or paid agent-network participation outside owner-authorized campaigns | Affects third parties, reputation and consent | **Needs campaign-specific authorization** | Approve named channels, messages and posting ceilings |
| PCA-004 | Expand the HP relay beyond `ping`, `hp_status`, and configured read-only `sidecar_verify` | New machine-access permission | **Needs explicit owner-local opt-in and tests** | Review narrow command, rollback and physical HP acceptance separately |
| PCA-005 | Promote a completed automation program into a new operating baseline (`vNext`) and retire or swap any existing scheduled worker | Consequential cutover could cause downtime or lose history | **Needs future owner cutover approval after readiness evidence** | Review the [restart-readiness audit](../docs/CF0_FRAMEWORK_AUDIT_AND_RESTART_PREP_2026-11-07.md), passed tests, private backup restore and rollback before authorizing any cutover |

**Important:** Nothing in this queue is pre-approved merely because it is listed. Existing separate approvals remain valid within their original scope.

## 2. Safe automatic changes permitted *within current authority*

A CF-0 operator may make bounded, public-safe **clarity/efficiency** changes during an authorized execution run, without another owner clipboard handoff, only if all apply:

1. It already read the complete three prompts from public `main`, read the relevant source, and respects current owner direction and source SHA.
2. Change is editorial or operationally clarifying: fix duplicate or stale instructions, broken links, ambiguous status language, unnecessary manual steps, or add pointers to verified existing artifacts. It **cannot** alter actual permission scope, founder control, financial obligations, operator identity, security boundaries, private/public protections or task completion evidence.
3. It writes an **append-only** event to [prompt change history](PROMPT_CHANGE_LOG.jsonl), and updates this bin's *applied* section with before/after scope, changed files, evidence and rollback commit. No silent changes.
4. It checks that the original source-to-source boot order, continuity requirements, owner priority order, HP allowlist, no-false-income and no-false-autonomy clauses remain in force. Run a test or CI check when available; disclose pending/failure.
5. If any condition fails, **draft a proposal here**, keep current source unchanged, and request the owner's decision only when truly needed. A rejected proposal is retained as history and may not be silently resurrected.

**One prompt efficiency goal:** reduce repeated manual data copying and repeated explanation, rather than simply compressing text until meaning is lost. Reuse current links, status feeds, source checks and existing schedules; do not create duplicate competing operators.

## 3. Applied changes and notes

| ID | Change and reason | Outcome | Evidence |
|---|---|---|---|
| PCE-001 | Established this review bin and an append-only prompt-change log. | **Applied under the owner's November 7 request**; no authority or payments changed. | [Create commit](https://github.com/whoiwts110217-creator/CF-0/commit/884090251f2d6c3cb9437f400bfba6d38102dddc) |
| PCE-002 | Added bounded efficiency edits and approval routing to the operating master. | **Applied; [prompt guard passed](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42368403593), including Windows line-ending regression test.** | [Operator commit](https://github.com/whoiwts110217-creator/CF-0/commit/766e53b3e149c7acceb79509e16df94cdeaf7612) |
| PCE-003 | Added approval-bin preflight and prompt-change logging to Work handoffs. | **Applied; [Windows suite passed](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42368403589), with no expanded tool or HP authority.** | [Work commit](https://github.com/whoiwts110217-creator/CF-0/commit/c28db8482d23607cda2bc5cfd10b93228599ed9c) |
| PCE-004 | Preserved original-prompt provenance and reversible change evidence in continuity master. | **Applied; existing project/owner history preserved.** | [Continuity commit](https://github.com/whoiwts110217-creator/CF-0/commit/59d415ad0da67960dda4a2e4dcea44eb5c0fd027) |

## 4. Next operator / Work handoff

- **FIRST** read [MASTER_OPERATOR_PROMPT.md](MASTER_OPERATOR_PROMPT.md), **NEXT** read [MASTER_CONTINUITY_PROMPT.md](MASTER_CONTINUITY_PROMPT.md), **THEN** [WORK_COPY_PASTE_AUTOMATION_PROMPT.md](WORK_COPY_PASTE_AUTOMATION_PROMPT.md) from the current public `main` before decisions, **THEN** read this bin and [the log](PROMPT_CHANGE_LOG.jsonl).
- During every run: check this queue; act on items explicitly approved by the owner where tools and guards permit; make eligible tiny prompt improvements as normal work; append a record for each change; keep all unapproved proposals pending. Link commits and test evidence, rather than assuming a GitHub edit is a fully deployed capability.
- **CF-200 remains distinct:** editing a prompt is not an independently verified CF-200 work order. Do not change the 200-task registry or increment completion for editorial work.
- Preserve unrecovered archive gaps and keep private originals off public GitHub.

## Creator attribution correction (November 7)

| ID | Specific owner-directed edit | Boundary | Evidence |
|---|---|---|---|
| **PCE-005** | Correct two outdated operator-prompt attribution statements: David Smith creator/developer; Kiara Lynn Rose Smith designated owner/beneficiary | Owner authorized this specific factual reconciliation; PCA-001 **remains pending** for future automatic authority/ownership edits | [Master operator](MASTER_OPERATOR_PROMPT.md) · [append-only revision log](PROMPT_CHANGE_LOG.jsonl) · [source reconciliation](../docs/CONTINUITY_RECONCILIATION_2026-11-07_DREAMKILLER.md) |

## November 9 · Master Controller scope correction

| ID | Owner-authorized scope clarification | Result and boundary | Evidence / rollback |
|---|---|---|---|
| **PCE-006** | Narrow the existing **Master Operating Prompt** to a full four-surface controller audit: ChatGPT automations, every GitHub workflow (not only cron), owner-local Windows tasks, and keyboard-only one-tab AUTO-08. Distinguish public source from live control and staged research shutdown from actual pause. | **Applied as an editorial P0 acceptance clarification**, not a priority reorder or permission grant; all existing functionality, P0–P3 hierarchy, owner credit, privacy boundaries and HP allowlist preserved. No real task changed state. | [Operator scope commit](https://github.com/whoiwts110217-creator/CF-0/commit/ac917ce08cee9f5348d95f6fd52507d6c18b4cda) · [harsh audit](../docs/MASTER_CONTROLLER_AUDIT_2026-11-09.md) · [append-only event](PROMPT_CHANGE_LOG.jsonl) · rollback: revert operator commit with review. CI guard to verify. |
