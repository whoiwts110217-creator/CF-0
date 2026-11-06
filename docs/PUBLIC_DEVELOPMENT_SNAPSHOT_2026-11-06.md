# CF-0 Public Development Snapshot — 2026-11-06

**Status: PUBLIC DEVELOPMENT SNAPSHOT — NOT A STABLE OR FULLY VERIFIED RELEASE.**

This document is the public entry point to the work available today. It does **not** claim all modules are production-ready, that the HP can run unattended for seven days, or that revenue has been generated. Repository files may change after this snapshot; use the linked commit history to inspect changes.

## Start here
- [Project home](../README.md)
- [Master plan and workflow chart](CAVEMAN_FOCUS_MASTER_PLAN.md)
- [Start here](START_HERE.md)
- [Public mission board](../automation_200/MASTER_MISSION_BOARD.md)
- [Master operator prompt](../automation_200/MASTER_OPERATOR_PROMPT.md)
- [Automation overview](AUTOMATION.md)
- [Public outreach ledger](PUBLIC_OUTREACH_LEDGER.md)

## Available source areas
- [CF-200 automation engine](../automation_200/) — task registry, selector and operating instructions.
- [Windows HP relay](../relay/) — allowlisted command bridge and installation components; use only after reviewing scripts and permissions.
- [Phone-to-HP bridge](../bridge/) — experimental integration and setup materials.
- [Abund.ai integration](../integrations/abund_ai/) — scheduled posting and read-only discovery scripts, capability declaration and tests.
- [GitHub workflows](../.github/workflows/) — automation schedules and CI; some workflows need repository secrets or variables.
- [Experiments](../experiments/README.md), [Research](RESEARCH.md), [Projects](PROJECTS.md) — published research and archival material.
- [Business](BUSINESS.md) and [public finance](../finance/README.md) — plans and records, not a claim of verified profit.

## Verification distinctions
- Public GitHub source and documentation: **available**.
- Prior CI and allowlisted HP connection demonstrations: **reported and evidenced in project records**; inspect receipts before treating any capability as verified.
- Full unattended HP operation, seven-day autonomy, generic desktop control, and public outsider installation: **not verified**.
- Abund.ai discovery: prior successful run exists; later modifications and capability registration still need fresh verification.
- Commercial revenue, customers, and donations: **do not assume verified**.

## How to try it
1. Read [START_HERE](START_HERE.md), [the rulebook](../CAVEMAN_FOCUS_RULEBOOK_v0.1.md) and relevant component README before running any script.
2. Clone the public repository: `git clone https://github.com/whoiwts110217-creator/CF-0.git`.
3. Review the component's prerequisites and code. Start with offline or read-only tests rather than the HP relay or any account-linked workflow.
4. Never copy another person's secrets, personal files, payment credentials or local configuration into a public issue or commit.
5. File reproducible bug reports with redacted logs and exact version/commit identifiers.

## Release limitations
No completed fresh-user installation test or general software security audit is asserted here. No standalone binary, GitHub Release tag, stable version, formal support promise or license grant is asserted by this snapshot. **Public source visibility does not itself grant reuse rights**; check the repository's license before redistribution or commercial reuse. This document is a publication index, not a claim that every private archive or account record has been made public.

## What comes next
Finish and verify the automation; publish a usable versioned public release; then begin **Day One** of a public follow-along using the same automation available to everyone. Track real costs, customer activity, collected revenue, profit, failures and improvements. See the [master plan](CAVEMAN_FOCUS_MASTER_PLAN.md).
