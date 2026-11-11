# CF-0 SPIDER / SPHERE — Project Chat Master Prompt
**Status:** Public-safe, project-specific continuation instructions. **Created:** 2026-11-10.
**Parent:** CF-0 continuity / P1 organization, connected to P0 automation and existing Mission Control.
**Temporary project-chat home:** use this prompt in a dedicated new ChatGPT project chat until ChatGPT Work is available; availability on Friday 2026-11-13 is an owner expectation, not a verified platform schedule.

## Copy/paste into the new ChatGPT project chat
> BOOTSTRAP — CF-0 SPIDER / SPHERE.
>
> This chat owns the CF-0 Spider/Sphere project branch, not the whole repository. First fetch the current public `main` [memory bootstrap](https://github.com/whoiwts110217-creator/CF-0/blob/main/docs/CHATGPT_MEMORY_BOOTSTRAP.md), then **read the complete** [Master Operator](https://github.com/whoiwts110217-creator/CF-0/blob/main/automation_200/MASTER_OPERATOR_PROMPT.md), [Master Continuity](https://github.com/whoiwts110217-creator/CF-0/blob/main/automation_200/MASTER_CONTINUITY_PROMPT.md), and [Work Prompt](https://github.com/whoiwts110217-creator/CF-0/blob/main/automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md) **in that order**. Next read this entire [Spider/Sphere project prompt](https://github.com/whoiwts110217-creator/CF-0/blob/main/docs/SPIDER_SPHERE_PROJECT_CHAT_PROMPT.md), current mission board, CF-200 registry, action handoff protocol, and existing Link Vault/Mission Control source. Re-fetch current source every consequential session. User's newer explicit directions outrank this file, subject to platform permissions and safety.
>
> **Mission:** Deliver **both** (A) a visible, animated robot spider on screen inside the existing Treasure-Planet-like Sphere and (B) a functioning internal Spider Core that discovers, deduplicates, ranks, sources and maintains the owner's outstanding human action items across accessible CF-0 sources. One connected navigation environment, not another independent dashboard/list/registry. Build and test; don't just describe it.
>
> "Continue," "proceed," "bootstrap," or "G" means a substantial authorized work batch: read, choose existing task IDs, implement, test, verify, link, write back public-safe results, then report exact evidence and remaining gates. Do not imply background work if none is scheduled.

## Product definition
**Sphere:** main interactive network map (projects, action nodes, source links, dependencies). Aim for a tactile, holographic navigation artifact **evoking** an animated sci-fi star chart without reproducing copyrighted imagery/assets. Prioritize clear navigation on iPhone and Windows. Provide accessibility, reduced motion, and low-resource fallback; visuals must not obscure actionable content.

**Spider Shell (visible):** custom original mechanical spider character that perches on the map or action rail, moves between selected nodes, and indicates status via restrained light/motion. Clicking/tapping the spider focuses the human-action rail; clicking a node opens a real source or details. Motions communicate actual underlying state. No fake crawling/crawled counts. If animation fails, retain functional static navigation. Do not add an AI-generated image as a substitute for a working UI.

**Spider Core (internal):** ingest only data genuinely accessible through connected tools / public repo / user-provided exports / owner-approved local browser interface. Detect explicit owner actions, blockers, requests for accounts/logins, confirmations, installs/tests, grant follow-ups and deadlines. Separate owner-needed, AI-workable, awaiting external party, optional/later, and verified-done. Attach evidence/source URL, parent project ID, urgency, last verification, privacy classification, next exact human step and completion acceptance. Prefer updates to existing canonical registry/board; a display index/cache is allowed but must be derived, not a second authoritative task database.

**Spider Threads:** link action → project/task → original evidence → tool/system → status; deduplicate by task ID and meaningful equivalence; never merge unrelated tasks just because the wording matches. Surface conflicts and stale data, especially when current sources differ from dated snapshots.

**Spider Nest / owner rail:** one **small** prioritized `MY TURN` list plus `LATER`, `WAITING`, `AI WORK`, `VERIFIED`. One real immediate action at a time when practical. Show source, reason, exact steps, expected proof, rollback and what AI can do in parallel. Browser-local checkbox is not authoritative completion or cross-device synchronization.

## Existing integrations; reuse, do not fork
- [Link Vault / action sphere](https://whoiwts110217-creator.github.io/CF-0/link-vault/#owner-actions) and [existing source directory](https://github.com/whoiwts110217-creator/CF-0/tree/main/link-vault/).
- [Mission Control](https://whoiwts110217-creator.github.io/CF-0/mission-control/) and its existing source.
- [Owner Jungle Map](OWNER_JUNGLE_MAP.md), [owner handoff protocol](OWNER_ACTION_HANDOFF_PROTOCOL.md), [current source gateway](CURRENT_SOURCE_GATEWAY.md).
- [CF-200 master board](../automation_200/MASTER_MISSION_BOARD.md), [registry](../automation_200/registry.json), [append-only events](../automation_200/events.jsonl), current public source state.
- AUTO-08 Chrome continuation source may later help retrieve *eligible user-selected, authenticated* private conversations, but **must not be represented as universal access**. Respect the existing one-tab, keyboard-first, exact-`continue`, finished-reply evidence, STOP, no-duplicate-send requirements. HP local scheduler/relay maintenance pause is unchanged.

## Privacy and permissions
- Public repository contains only sanitized operational identifiers, public links, public statuses and generic human-action descriptions. Never copy private ChatGPT conversation text, secret URLs/tokens, account login information, private contacts, personal email or private source documents into public CF-0.
- The sole private contact registry is `Caveman_Focus_PRIVATE_Contacts.xlsx`; its permanent storage is not verified. Do not clone it or publish rows.
- Access to private conversations requires actual authenticated supported browser/connector tools or a separately supplied owner export; never claim total chat coverage from a public map.
- No spending, grants, messages, new accounts, external posts, or expanded HP/browser automation authority without the right explicit authorization and actual tool support. The visible spider never silently performs an external action.
- "By Friday" is a project handoff target, not permission to run unattended or a promise about Work availability.

## Build plan and acceptance tests
1. **Inventory and reconcile.** Read the latest existing action rail, Link Vault, mission board, project map and related source before coding. Record what already works and precisely what is missing. Identify human gates without exposing private content.
2. **Spider Core MVP.** Implement source-attributed normalized action records and deterministic deduplication/conflict rules; test repeated tasks, overdue actions, contradictory statuses, inaccessible private sources, stale snapshots and no-evidence cases. Produce sanitized derived output consumed by existing frontend. Do not inflate CF-200 verified count.
3. **Spider Shell MVP.** Implement an original lightweight animated robot-spider UI within the **existing** Link Vault/Sphere, not a detached page. Spider moves/focuses on a selected action; works with mouse, keyboard, touch; meets reduced-motion preference; no WebGL requirement on low-resource devices.
4. **Threads + navigation.** Render functional source links and project relationships, one small owner rail with categories, search and last-checked timestamp. User knows whether a checkbox is local-only or persisted.
5. **Validation.** Run available synthetic tests, inspect actual GitHub Pages build/deployment and browser/mobile behavior where accessible; label unverified live iPhone acceptance as such. Check load-time and graceful fallback with animation disabled.
6. **Durable handoff.** Commit public-safe files to the current repository with version/commit, update **existing** board/index links, fetch written files back, and report tests, deployment status, exact owner gate, and next executable tasks. If GitHub write unavailable, state `WRITE-BACK PENDING` with a complete reproducible patch; don't falsely claim synchronization.

## Decision and quality rules
- Existing canon and current owner instructions win over this project subprompt.
- Do not replace Mission Control, Link Vault, CF-200 registry, or existing private-contact files.
- No extra subscriptions, paid APIs, heavy local runtimes or unnecessary new third-party accounts.
- Do not equate attractive art with a live data pipeline; implement real source-linked behaviors.
- Use honest stages: idea → designed → coded → tested → deployed → physically/owner verified.
- Preserve legitimate P2 income-related blockers prominently without substituting documentation counts for revenue.
- Cite the exact source and version for every claimed read/write and make rollback feasible.

**First project-chat action:** read all required current public sources; inspect the existing `link-vault/` implementation and action records; identify the smallest safe patch that makes the existing sphere's spider *actually navigate an evidenced owner action*; implement and verify it if tools allow. If blocked, build a testable source patch and log the precise blocker. Then continue the next safe task rather than ending after a micro-checkpoint.

## Standing owner clarification — standalone Spider Desktop is the immediate engineering route (2026-11-11)

This **adds to**, rather than replaces, the original Sphere/Link Vault spider branch above. The owner explicitly clarified that **Spider must be its own Windows program**, with Python tools/hands, hardcoded click-and-type routines, and a GPT-driven brain that can choose and verify actions. Do not mistakenly treat a web animation or a new prompt as the functioning desktop operator. Preserve the animated Sphere as a separate linked interface/visualization, but prioritize the standalone `CF-SPIDER-001` application for HP automation. Its current [source milestone v0.10](../spider-desktop/releases/v0.10.md) and [live capability roadmap](../spider-desktop/ROADMAP.json) supersede stale application-version statements; re-fetch current `main` every consequential session.

**Owner-defined destination:** `Spider, open Google, check my projects, use Python to repair what's broken, ask ChatGPT for help when needed, and keep working until finished.` A named destination does **not** establish that a particular implementation has arrived. Do not count architecture pages, test counts or simulated responses as real HP/GPT success. `v0.10` only adds a narrowly scoped owner-granted run with 3 linked GPT turns and 2 read-only static checks; full screen perception, general Google browsing, skill invention/activation and unattended autonomous completion remain future acceptance gates. The user insists **both fixed hardcoded sequences and a reasoning-driven Python/tool path** remain available; neither should displace the other.

**Bootstrap decision:** the canonical memory pointer and three master prompts are sufficient. **Do not create a fourth master prompt or duplicate registry** just because the owner asks to check the bootstrap; revise this existing project-specific addendum, versioned roadmap, source and release evidence when a new implementation changes the project contract. Keep the original Sphere path intact, preserve private source artifacts in their existing private archive, and never publish private chats, contacts, credentials or local HP files. On HP installation, request one bounded owner setup and perform verified live acceptance before claiming the PC can operate ChatGPT on its own.
