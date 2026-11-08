# Caveman Focus — CF-0

**[START HERE — site, Mission Control, master prompts, HP commands, AI Tracker](docs/START_HERE.md)**

**[PUBLIC TASKS & ISSUES](docs/TASKS_AND_ISSUES.md) — what we're doing, what's blocked, and what needs your decision**

**[TRY CAVEMAN FOCUS — free 60-second clarity exercise and feedback](https://github.com/whoiwts110217-creator/CF-0/issues/21)** — a public experiment; participation and optional support are separate. No visitor, supporter, or income claims.


**Created and developed by David Smith; designated owner and intended generational beneficiary: Kiara Lynn Rose Smith.**

> Simplify complexity without losing the essentials. **Guess → hypothesis → evidence → proof.**

**Caveman Focus is an experimental automation and knowledge system** being built to coordinate AI-assisted work, make priorities follow its owner's decisions, and verify what actually happened. Its first practical target is a low-resource Windows PC: fewer manual commands, more useful automated work, and clear evidence for every result.

**Project stage: public developer preview (November 6, 2026).** The source is available, but there is no stable, independently reproduced end-user release yet.

**Executable archive continuity (source-only):** [local-first conversation and project index](continuity/README.md) now has an offline Python/SQLite importer, duplicate source origins, proposed claims and conflicting-claim detection. It is **not installed on the HP** and does **not** auto-retrieve other account histories. Originals and searchable chat text stay outside this public repo.

**Master continuity order:** [Read the public master operating prompt first](automation_200/MASTER_OPERATOR_PROMPT.md), then the [cross-archive, project and event continuity prompt](automation_200/MASTER_CONTINUITY_PROMPT.md) **before CF-0 decisions**. Work sessions then read the [current Work execution prompt](automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md) from public main. The public prompt describes how to recover and reconcile prior conversations, archives and workstreams without publishing private originals.

**Live task evidence:** The [public task and issue dashboard](docs/TASKS_AND_ISSUES.md) summarizes the current source-backed registry and open issues. For task-specific verification use [the project status](docs/PROJECT_STATUS.md) and [public continuity evidence](docs/CONTINUITY.md). The currently checked-in relay **does not support remote Notepad launch**; previously observed Windows Notepad launches are historical, and restoration remains open. The optional HP heartbeat and independent scheduler correlation are still unverified.

**[Filed concepts](concepts/README.md)** · **[Dreamkiller / BreachDungeon](concepts/dreamkiller/MASTER_CONCEPT_AND_CONTINUITY_PROMPT.md)** · **[November 7 cross-archive reconciliation](docs/CONTINUITY_RECONCILIATION_2026-11-07_DREAMKILLER.md)**

**[What works](#what-works-today)** · **[Try the source](#explore-or-test)** · **[Current status and evidence](docs/PROJECT_STATUS.md)** · **[Full project index](docs/PUBLIC_DEVELOPMENT_SNAPSHOT_2026-11-06.md)**

## The operating-environment thesis

**The goal is not to invent a second intelligence. It is to build the conditions in which existing AI reasoning can do useful work repeatedly.** Caveman Focus aims to provide persistent task context, owner-governed priorities, restricted tools, execution records, observations, and recovery so a reasoning model can plan → act → evaluate → revise.

The AI supplies reasoning; the environment supplies continuity, permissions, action and feedback. **This is the design hypothesis, not a claim that the full loop is operational.** [Architecture and acceptance gates](docs/CAVEMAN_FOCUS_MASTER_PLAN.md).

## What works today

The owner previously observed a bounded **ChatGPT → GitHub queue → Windows HP relay → public-safe receipt** pathway, including Notepad launches in the original November 5 milestone. Owner-provided Windows scheduler evidence also documents task starts. A later source regression removed `open_notepad`; the **current** public Python relay allows only `ping`, `hp_status`, and `sidecar_verify`. The legacy installer now refuses to claim that Notepad is working.

**Current supported evidence:** public matching ping request/receipt hashes, SQLite/source-level idempotence tests, and passing cloud Windows CI. **Not established:** physical HP-origin attestation for a given public ping, automatic health publication, current Notepad control, arbitrary computer control or seven-day autonomous operation. The [dated continuity record](docs/CONTINUITY.md) separates those states.

[See the November 5 HP demonstration and evidence](docs/CF0_FAST_LANE_MILESTONE_2026-11-05.md) · [See the November 6 continuity audit](automation_200/MASTER_MISSION_BOARD.md)

## What we're building next

**Remove the human copy-and-paste loop.** The owner should set goals and approve consequential actions, not repeatedly copy PowerShell diagnostics into ChatGPT. The next deliverable is automatic, privacy-minimized HP health reporting through the existing bounded relay.

The [read-only collector source](relay/cf_hp_health_snapshot.py) exists. **It is not yet deployed on the HP or publishing reports automatically.** Do not mistake a committed file for an installed capability.

After that, develop an owner-controlled priority engine, then legitimate financial operations. Creative and scientific work can progress concurrently when resources permit.

## Explore or test

- **New visitors:** [Start Here](docs/START_HERE.md) explains the project, its priorities and the evidence boundaries.
- **Developers:** inspect the [relay source](relay/), [CF-200 task engine](automation_200/), [tests](tests/) and [GitHub workflows](.github/workflows/). Start with offline, read-only tests. The public repository is **not** a turnkey remote-control installer.
- **Reviewers:** use the [current status and evidence](docs/PROJECT_STATUS.md), [mission board](automation_200/MASTER_MISSION_BOARD.md), and [task registry](automation_200/registry.json) to distinguish code, tests, owner-HP observations and unverified goals.
- **Broader work:** [project and research index](docs/PUBLIC_DEVELOPMENT_SNAPSHOT_2026-11-06.md), [master plan](docs/CAVEMAN_FOCUS_MASTER_PLAN.md), and [foundation](docs/FOUNDATION.md).

## Operating principles

1. **Automation first.** Build reliable execution, receipts, recovery and safe transport.
2. **Priority intelligence second.** Owner direction controls scheduling and overrides.
3. **Financial sustainability third.** Measure real customers and collected income; don't call plans revenue.
4. **Other projects concurrently.** Preserve and advance research, inventions and creative work without displacing higher priorities.

[Autonomous Operations Rulebook](CAVEMAN_FOCUS_RULEBOOK_v0.1.md) · [Master Operator Prompt](automation_200/MASTER_OPERATOR_PROMPT.md) · [Public release policy](docs/PUBLICATION_POLICY.md)

## Finances and voluntary support

Caveman Focus is developing legitimate, low-cost ways to sustain its automation and public work. **No sales, donations, or profit are claimed as verified here.** See [business plans](docs/BUSINESS.md) and [public finance records](finance/README.md) for context.

**[Support Caveman Focus — donation campaign](https://caveman-focus-support.whoiwts110217.chatgpt.site)** · [Direct optional support through Cash App](https://cash.app/$LAZYBLACKBEAN)

Contributions are voluntary support for an independent project, **not** tax-deductible charitable donations, purchases, or investments. No financial return is promised. The campaign was confirmed publicly accessible when published November 3, 2026; **its present live accessibility has not been independently reverified**.

## Important boundaries

This is a public, curated project archive—not a complete conversation export. The original approximately 37-project list remains unrecovered. No verified RH proof, new scientific law, seven-day independent HP operation, general-purpose desktop controller, or real income is claimed. Public GitHub is **not** a place for credentials, private account data, private creative source or other people's personal information. Review repository licensing before reuse; source visibility alone is not permission to redistribute.

**The test for progress is not how many plans we write. It is how much authorized work the system performs and verifies without making the owner do it manually.**

### Optional HP health reporting

A local, reversible opt-in is available for the existing HP relay: [one-click HP health reporting](relay/HEALTH_ONE_CLICK.md). This is source-only until the owner updates and activates it on the physical HP; CI is not HP evidence.

**Cross-project continuity:** The [private local continuity store](continuity/README.md) now has an offline [CF-200 work-order bridge](continuity/workorder_bridge.py) that can link source-verified task IDs to existing project records only after explicit review. Code/tests are public; private data, owner approval, live HP deployment and automatic cross-account source recovery are separate unfinished milestones.

**Continuity archival recovery v2 (Nov 6):** A private, restored-and-hash-audited continuity backup now preserves 18 source artifacts, 134 project-source links, 62 still-unverified reconstructed projects, and 91 events. [Public-safe evidence boundaries and exact-file CI test](docs/CONTINUITY.md). No original full conversation exports, deployed HP sync, verified revenue or lost original ~37-project list have been recovered by this milestone. The private backup is **not** in GitHub.
