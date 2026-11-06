# Caveman Focus — CF-0

**Kiara Lynn Rose Smith's Caveman Focus**

> Simplify complexity without losing the essentials. **Guess → hypothesis → evidence → proof.**

**Caveman Focus is an experimental automation and knowledge system** being built to coordinate AI-assisted work, make priorities follow its owner's decisions, and verify what actually happened. Its first practical target is a low-resource Windows PC: fewer manual commands, more useful automated work, and clear evidence for every result.

**Project stage: public developer preview (November 6, 2026).** The source is available, but there is no stable, independently reproduced end-user release yet.

**[What works](#what-works-today)** · **[Try the source](#explore-or-test)** · **[Current status and evidence](docs/PROJECT_STATUS.md)** · **[Full project index](docs/PUBLIC_DEVELOPMENT_SNAPSHOT_2026-11-06.md)**

## The operating-environment thesis

**The goal is not to invent a second intelligence. It is to build the conditions in which existing AI reasoning can do useful work repeatedly.** Caveman Focus aims to provide persistent task context, owner-governed priorities, restricted tools, execution records, observations, and recovery so a reasoning model can plan → act → evaluate → revise.

The AI supplies reasoning; the environment supplies continuity, permissions, action and feedback. **This is the design hypothesis, not a claim that the full loop is operational.** [Architecture and acceptance gates](docs/CAVEMAN_FOCUS_MASTER_PLAN.md).

## What works today

The owner has demonstrated a bounded **ChatGPT → GitHub queue → Windows HP relay → public-safe receipt** pathway, including owner-observed Notepad launches. The Windows Task Scheduler has also been observed launching the relay automatically. The system records receipts in SQLite and has tests for parts of the protocol.

**What this proves:** specific allowlisted commands can be transported, executed and recorded on the owner's HP. **What it does not prove:** arbitrary computer control, a complete unattended workday, a seven-day autonomous run, or that a particular scheduled invocation generated a particular public receipt.

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
