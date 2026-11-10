# CF-MESH-001 — Public Three-Chat Continuity Mesh

**Owner direction:** November 9, 2026. **Status:** public operating and cross-chat handoff protocol, not evidence that three chat sessions are presently synchronized. **Parent:** CF-CORE / UCC-001. **Related:** CF-200, AUTO-08, Mission Control, HP relay, P1 decision engine, FIN-09 and every indexed project. **Source of truth:** public `whoiwts110217-creator/CF-0` `main`, linked records and their exact commit/blob SHAs.

## Purpose: three short-memory chats, one recoverable public spiderweb

Three separate chats, even on different sessions/accounts with limited conversational memory, should each be able to start cold, retrieve the same public canonical instructions, reconstruct relevant project connections, select a permitted task, and leave a source-linked handoff that another chat can recover. **Do not rely on the chat's remembered history as the shared memory.** There is no genuinely unlimited prompt/context window: use a navigable public index plus linked, versioned source files, retrieve complete relevant sections in batches, and state coverage gaps instead of pretending to have read what is unavailable.

**Not a synchronization claim:** GitHub gives durable public read/write records only to chats with available tools and permissions. A chat without authenticated write capability cannot update the repository; it must report this and prepare a public-safe proposed handoff. A prompt cannot run itself, message another chat, create a scheduler, bypass account permissions, or guarantee other sessions see changes instantly.

## Implemented topic anchor and source-linked navigation (source-stage)

The [public topic graph](PUBLIC_CONTEXT_GRAPH.json) gives twelve explicitly sourced public nodes and their parent, related, and prerequisite edges; it does **not** pretend to reconstruct the missing original project inventory. The read-only [topic router](../continuity/public_topic_router.py) keeps the user's active topic fixed and returns a bounded reading list, beginning with the unchanged three master prompts. A related node is context to consult, **not** a reason to switch workstreams. Unknown topics, missing links, invalid source paths, parent/dependency cycles and ambiguous aliases fail closed. Run from a repository checkout: `python -m continuity.public_topic_router --topic CF-MESH-001` or `python -m continuity.public_topic_router --check-all`. The existing prompt-efficiency GitHub workflow now includes source-level tests. No unattended cross-chat read, prompt execution, or private-account interconnection follows from this tool.

## Exact cold-start procedure for Chat A, B, or C

1. **Fetch current public `main` in this mandatory order:** [Master Operator](../automation_200/MASTER_OPERATOR_PROMPT.md) → [Master Continuity](../automation_200/MASTER_CONTINUITY_PROMPT.md) → [Work Prompt](../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md). Read full content (chunk when needed) and record exact blob SHAs. Do not infer latest from an earlier chat.
2. Read [UCC-001](UNIVERSAL_CONTINUITY_CONTRACT.md), **this mesh**, [Mission Board](../automation_200/MASTER_MISSION_BOARD.md), [public project index](PROJECTS.md), [prompt approval bin](../automation_200/PROMPT_CHANGE_BIN.md), [prompt change log](../automation_200/PROMPT_CHANGE_LOG.jsonl), and relevant [registry](../automation_200/registry.json), [events](../automation_200/events.jsonl), current public state, CI/HP and source artifacts. Do not treat a stale board heading as live status.
3. State what is **read/verified**, what is **stale/unknown**, the newest applicable explicit owner correction available in this session, and which original/private sources were **not accessible**. Identify the current task, parent and related project IDs, dependency edges, priority, permissions, and last verified result.
   **Topic retention:** The currently selected owner topic, or the last verified public-safe `active_topic_id` when starting cold, remains the anchor. Follow neighboring links to gather evidence but return to that anchor before proposing actions. An unqualified `continue` resumes the existing anchor; if no reliable anchor exists, report the gap rather than choose an attractive adjacent project.
4. Do an authorized measurable task, not another speculative top-level plan. If blocked, choose the next safe P0 action or deadline-sensitive permitted P2 work; do not erase other workstreams.
5. Before changing a shared file, fetch its newest SHA, compare the relevant neighboring nodes/links and latest changes, use the SHA-guarded write, read the result back, and preserve a rollback path. On write conflict, re-fetch/reconcile; never overwrite another chat's intervening changes.
6. Publish a **public-safe**, source-linked handoff to the existing authoritative board/index/log where appropriate. Prefer a distinct append-only event or workstream-specific record over competing complete copies. If no substantive change occurred, say **NO VERIFIED CHANGE** instead of manufacturing activity.
7. Another chat must independently re-read the new commit before accepting that handoff. **No chat's self-report proves that another chat consumed it.**

## Preserve every strand: graph contract

For every modified project, feature, grant, finance offer, conversation-derived instruction, artifact or automation, record or link to: `continuity_id`, `parent_id`, `related_ids`, `dependency_ids`, owner intent and correction source, latest actual source/commit SHA, evidence level, authority/privacy limits, status, downstream effects, tested result, next action, and rollback. Use stable IDs and canonical links; do not merge distinct branches just because their wording overlaps. If a link is missing, conflicting, or changed, mark `connection_gap` with source and impacted IDs; repair only after checking original evidence.

**Cross-impact check:** whenever one node changes, inspect direct dependencies, consumers, the Mission Control surface, decision rules, relevant active watches/automation, funding deadlines, and public status references. Update broken references instead of silently severing them. Preserve original and rejected decisions as history. A real change with no linked handoff is an incomplete continuity update, **not** a reason to repeat the owner interview.

## When a chat should update the shared public prompt

Inspect prompt health on every consequential run; **edit only when an actual trigger exists**: (a) explicit new owner rule or correction, (b) stale/broken canonical pointer or dependency, (c) repeated confusion causing duplicated work or owner copy/paste, (d) a verified regression or changed acceptance test, or (e) a contradiction among canonical prompts/handoffs. Make a bounded, additive correction in the smallest canonical location; propagate necessary cross-links to the three prompts, log before/after SHA and commit in the [append-only change log](../automation_200/PROMPT_CHANGE_LOG.jsonl), update the [approval bin](../automation_200/PROMPT_CHANGE_BIN.md), validate readback/tests and provide rollback. Do **not** churn the master for routine status data; status belongs in the board, registry, and events. Permission, credit, privacy, priorities, spending, public posting, HP commands or disabling a working feature still require their separate approvals.

## When to update the owner

Communicate **immediately in the active chat or an already-authorized notification channel** when a genuine owner decision is required, a critical capability is lost, a privacy/security issue or authorization conflict is detected, a material deadline is within 72 hours and needs owner action, a grant/customer/payment actually changes verified status, or a high-priority connection is found broken with real downstream impact. State the **single consolidated owner action**, its deadline when known, and what work can continue without the owner.

At actual completion of a consequential run, give a brief durable report: **changed and linked**, **verified evidence**, **still unknown**, **next three actions**, **owner action: none or specific**. Routine no-change polling, synthetic CI results, duplicated issues and unverified income do not justify repeated urgent pings. Only a real enabled scheduled automation or authorized channel can provide out-of-session delivery; writing these instructions does **not** activate notifications.

## Public means public-safe, not raw chat publication

The three canonical prompts, this protocol, approved operational summaries, non-sensitive project graph, source/code/CI links, verified sanitized statuses, public issues, and public-safe handoffs are intended to be visible to **anyone** with the repository link. The *three private ChatGPT conversations themselves are not published or made mutually readable by this rule*. Do not dump private transcripts, old account exports, unpublished manuscripts, health or banking data, personal contact information, access tokens, local paths or other confidential material into the public repo. Specific release of a private original needs explicit content review and authorization. Existing owner/creator attribution is untouched.

## Handoff schema (public-safe, source-linked)

```text
CF0_MESH_HANDOFF
mesh_contract=CF-MESH-001
worker_label=<A|B|C|other; local label only, no private chat/account IDs>
public_main_commit=<actual SHA, or unknown>
prompts_read=<three current blob SHAs, with full/partial scope>
active_topic_id=<the user's selected topic; recover from last verified handoff, never guess from adjacent projects>
project_ids=<parent + related + dependencies>
supporting_links=<bounded related nodes consulted, none is a topic switch>
return_to_topic=<the specific unfinished next action for active_topic_id>
owner_correction=<verified latest available direction; otherwise unknown>
last_change=<path, commit, evidence class, or NO VERIFIED CHANGE>
connections_checked=<IDs and any connection_gap>
provider_state=<source-only / provider-confirmed / unavailable>
privacy_and_permissions=<public-safe / blocked with reason>
owner_notification=<sent in this chat / authorized provider confirmed / none / not possible>
owner_action=<none or one explicit action>
next_three=<concrete executable tasks and stop conditions>
rollback=<previous commit or guarded path>
```

Never claim that merely writing this handoff changed another chat's memory or achieved unattended execution, sales, grants or HP control.

## Cold-start acceptance test (not yet passed)

Have **each of three genuinely separate chats** start without relying on past context, fetch and explain the same live priorities and graph links, independently recognize a seeded public-safe link change, and produce a source-verified handoff consumed by the next chat. Record the commit SHA and evidence of each separate read/write. Test stale source, concurrent write conflict, a missing original, and a blocked private publication. Until then, this is a **published coordination contract**, not a proven live three-chat mesh.
