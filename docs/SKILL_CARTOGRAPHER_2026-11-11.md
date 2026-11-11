# CF-0 Skill Cartographer — first-pass audit (2026-11-11)

**Related project:** existing Caveman Focus Skill Foundry; **continuity ID:** CF-SKILL-CARTOGRAPHER-001. Creator/developer: David Smith; designated owner/intended beneficiary: Kiara Lynn Rose Smith (not independent legal-transfer evidence).

## Actual changes and evidence

- The installed skill catalog returned **165 skill URI descriptions across 30 plugin groups**. All metadata records were inspected. This is a current visible catalog snapshot, **not** proof all full skill instructions were read, authenticated, or behavior-tested.
- Added `skill-cartographer` to the **existing private** Caveman Focus Skill Foundry plugin as release **0.3.1**. Connected plugin source readback confirmed the new `SKILL.md` and eight unrun evaluation cases, and all seven original skills remained. No new plugin, subscription, permission, device access or public private-plugin archive was created.
- Packaged a zero-dependency offline JSON catalog helper. Python syntax check succeeded. A two-entry synthetic sample was processed correctly (2 entries, 1 group); this is **not** validation against 165 live skill behaviors.
- The installed skill now defines: complete metadata enumeration, deeper relevant instruction reads, a typed prerequisite/alternative graph, tool and authentication verification, outcome-first routing, test evidence and rollback.
- Explicit full-instruction findings: `base44-cli` initializes a new project before `base44-sdk` works on it; browser skill separates Chat read-only tab tools from Work UI control; `airtable-cli` has local authentication prerequisites; `firecrawl/get-started` checks connection before claims of use.
- Candidate links still requiring full-text verification: Product Design context/QA chain, Drive Docs/Sheets/Slides specialization, vidIQ private-channel setup, and create-vs-update Plugin Creator routing. Research and media skills overlap, but similarity alone does not establish redundancy.

## Priority next use

**P0 Spider:** inspect present source and tests -> select a narrow failure -> `continuity-guardian` + `root-cause-debugging` + `skill-evaluation-lab` and applicable verified browser/tool capability -> test a supervised end-to-end outcome. Skill text never grants a GUI or HP connection.

**P2 income:** select a no-new-fee research-to-real-offer-to-verified-payment route. Do not equate a draft, link or application with paid revenue; no subscription, ad spend, outreach or financial action without authorized gates.

**Verification:** Private release **installed/read back**; the new skill's eight **behavioral evals NOT RUN**; full-instruction coverage of 165 **partial**; external accounts and physical HP **not verified**. No existing skills removed.

## Continuity and rollback

For consequential future runs re-read the live public main [Master Operator](../automation_200/MASTER_OPERATOR_PROMPT.md), [Master Continuity](../automation_200/MASTER_CONTINUITY_PROMPT.md), then [Work Prompt](../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md), plus applicable registry and originals. Preserve private records; do not duplicate task ledgers. Rollback by restoring the prior private skill plugin release **0.3.0** using its legitimate edit/release mechanism. Next test: one real narrow Spider workflow with exact before/after receipts.

## Activation follow-up (same-session observation)

Immediately after the private plugin 0.3.1 source readback, a new `skills__list` call in the **same ChatGPT conversation** still returned **165 entries**, and the new `skill-cartographer` URI was not discoverable there. A direct skill read by that URI returned `Resource not found`. Therefore the plugin update is **saved and source-verified**, but **skill-host activation in this conversation remains UNVERIFIED**. A later fresh conversation/plugin refresh should re-enumerate before claiming availability. No unsupported forced refresh or manual installation was performed.
