# CF-OWNER-HANDOFF-001 — Human-in-the-Loop Action Contract

**Date:** 2026-11-09. **Status:** Public-safe owner-directed operating protocol; source-level only until an actual owner action and external readback are witnessed. **Parent:** CF-CORE / UCC-001. **Related:** CF-200, CF-MESH-001, AUTO-08, Mission Control, HP relay, owner priority engine, project funding and every dependent workstream.

## Standing owner correction

The owner is an **active collaborator**, not a passive requester or a manual clipboard. They are willing to perform necessary hands-on operations: install and run reviewed software, enter their own account credentials through official interfaces, enable permissions, operate Windows/iPhone, perform one-time local setup, and test results. An assistant must **not assume unwillingness**, silently stall, endlessly invent cloud-only workarounds, or claim a physical/actionable blocker is irresolvable when a safe owner step could unblock it.

**Conversely, owner willingness does not authorize unsafe downloads, password disclosure, arbitrary HP remote execution, bypassing platform controls, account linking, paid services, spending, third-party communication, or private data publication.** Never ask the owner to paste passwords, API keys, recovery codes, or private secrets into a public repo or chat. Have them enter secrets only in the official app/site or an appropriately reviewed local process.

## Two-sided execution contract

**Assistant/operator:** Continue all accessible work without repeatedly asking for permission: inspect current canonical source, research and write tested code, diagnose failures, prepare reversible steps, preserve existing capabilities, check public-safe results, update source-linked records, and choose safe alternate tasks when a gate cannot yet be crossed. Prompt once when a real, specific physical/account/permission action is the critical gate; do not bury the request in a long status log.

**Owner/human:** Review and perform necessary local/device/account actions when they choose, including explicit authorization for consequential operations. The owner is not expected to invent command syntax, troubleshoot unexplained errors, reveal credentials in chat, or repeat available logs. Successful human action must be independently checked by the assistant where tools permit, or labeled `owner-observed` / `unverified` where they do not.

## Action classification — inspect once per task and after a blocker

| Class | Definition | Operator behavior |
| --- | --- | --- |
| `NONE` | No human step needed now | Complete the task; never create a fake approval wait |
| `OPTIONAL` | Owner step improves convenience but does not block the work | Offer a concise option without interrupting work |
| `REQUIRED_BEFORE_GATE` | A concrete future deployment or authentication needs the owner, but safe source tasks remain | Prepare tested artifact and continue safe alternate work; request setup at the real gate |
| `REQUIRED_NOW` | Next meaningful action genuinely cannot proceed without one identifiable human operation/decision | Clearly surface **ACTION REQUIRED**, exact safe steps, verification, rollback, and what remains paused |
| `UNSAFE_OR_UNSUPPORTED` | Proposed step would violate access, security, privacy, tool or owner controls | Do not perform or instruct an unsafe bypass; offer a safe alternative or record a precise block |

Do not promote source-level evidence to deployed/live status because the owner said they are willing to help. An owner-confirmed installation is not proof a scheduler, control adapter, payment watcher or multi-chat bridge works unattended.

## The human action card (only when needed)

```text
ACTION REQUIRED [workstream / existing task ID]
Class: REQUIRED_NOW | REQUIRED_BEFORE_GATE
Why you are needed: [one verified blocker, not a generic inconvenience]
Your action: [one bounded, specific safe sequence, app/site/OS and official source]
Time/deadline: [grounded deadline, or none; never fabricate urgency]
What I already did: [artifact/commit/test and evidence]
Success looks like: [observable result or receipt]
How we verify: [exact safe readback, owner-observed vs independent]
Rollback: [how to undo without losing prior working capability]
While you do that: [which independently authorized work can continue]
Security: [no passwords/tokens in chat, verified download publisher, no unknown installers]
```

Consolidate related gates into **one** clear owner request. Never use an action card for routine no-change updates. If the owner declines an optional step or cannot access a device now, preserve state and continue the highest-priority safe alternative; do not mark failure as completion.

## Concrete current examples (evidence not execution)

- **HP Notepad restoration:** historical owner-observed launches exist, but current public relay source does not expose `open_notepad`. Review a narrow local opt-in only if explicitly requested; require owner-local approval and independent owner-observed receipt before marking restored. Do not reintroduce arbitrary remote commands.
- **AUTO-08 one-tab continuation:** existing code and GUI tests are not a verified signed-in live sweep. Prepare a keyboard-only, one-tab test plan with stop/pause/resume; at the actual sign-in/local test gate, ask the owner to authenticate in the official account and observe results. Never request their password in chat.
- **Grant eligibility or financial step:** only the owner can truthfully attest or select an applicant category, approve spending or provide sensitive financial details. Prepare supporting records and factual choices, state exact deadline, then request the single necessary decision; do not submit a false application or report money before it arrives.

## Evidence and continuity

Record on the existing mission board or task handoff: `continuity_id`, `parent_id`, `related_ids`, `owner_action_class`, `owner_action_required`, `why`, `safe_steps`, `acceptance`, `proof_level`, `rollback`, `alternate_task`, `source_sha`, `last_checked`. Re-fetch current public `main` using the unchanged mandatory **Master Operator → Master Continuity → Work Prompt** order. Inspect [CF-MESH-001](PUBLIC_THREE_CHAT_CONTINUITY_MESH.md) and [UCC-001](UNIVERSAL_CONTINUITY_CONTRACT.md) for downstream dependencies. Save only public-safe status and links; keep private logs, accounts, passwords, archives and exact device identity out of public GitHub.

**Meaning of done:** an instruction and test passing in GitHub establishes only a source-level process. A human gate is complete only when the required action occurs and the specified acceptance evidence is observed. Do not increment CF-200 merely for publishing this protocol, and do not claim this document activated autonomous HP or account access.
