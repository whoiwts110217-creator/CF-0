# CF-SPIDER-001 — Spider/Sphere source-linked ChatGPT Work handoff
**Dated:** 2026-11-10. **Parent:** CF-LINK-VAULT-001 → CF-CORE / P1; related CF-MESH-001, CF-200, AUTO-08, UCC-001, FIN-09, CF-OWNER-HANDOFF-001.
**Stage:** source-coded in [draft PR #113](https://github.com/whoiwts110217-creator/CF-0/pull/113), not yet live/owner-device verified. Owner direction: animated robot plus true deduplicating internal Spider Core inside existing Sphere, with no replacement registry or dashboard.

## Mandatory new-chat/Work boot
Fetch [memory bootstrap](CHATGPT_MEMORY_BOOTSTRAP.md), then read complete current [Master Operator](../automation_200/MASTER_OPERATOR_PROMPT.md), [Master Continuity](../automation_200/MASTER_CONTINUITY_PROMPT.md), [Work Prompt](../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md) **in that order**. Only then read [Spider project prompt](SPIDER_SPHERE_PROJECT_CHAT_PROMPT.md), this handoff, [Source Gateway](CURRENT_SOURCE_GATEWAY.md), [project graph](PUBLIC_CONTEXT_GRAPH.json), [mission board](../automation_200/MASTER_MISSION_BOARD.md), [CF-200 registry](../automation_200/registry.json), and current branch/CI.
Initial session retrieved these actual Git blobs: memory 9c15c103015699a9b166bf8230d798b6a571d35a; Operator 5dad8c17b04a4eb744e5a1474b2ecfb9ddd0abe0; Continuity 77900acb1c3eb75f8dfd3cef245503d052971479; Work d090f82eaf89d9cd339e7eef248750ebef965e88; project 2f72ed6d4ac817ef558b02e984cdeae02755209a. Re-fetch moving main next session. CF-200 registry blob read 77d548b366ff5dc2070c74e30423a3495c6a73cb, 91/200 verified at read time; no task promotion.

## Working source links
- [Spider Core](../link-vault/spider-core.js): provenance-aware normalization, explicit same-project equivalence dedup, conflicts, project edges, optional actual registry-ID linking, stale/deadline assessment, exact source URLs, local-only action manifest validation.
- [Mechanical Spider Shell](../link-vault/spider-shell.js) and [original styles](../link-vault/owner-actions.css): eight-leg SVG; moves between actual action lanes, tap/keyboard focus/trace, reduced motion/static fallback.
- [Existing action rail](../link-vault/owner-actions.js) and [22 existing action records](../link-vault/owner-actions.json): source links, owner search, project IDs, dated snapshot and local-only manifest import.
- [Existing Link Vault](../link-vault/index.html), [v4 PWA](../link-vault/sw.js), [Website workflow](../.github/workflows/publish-website.yml): ordered JS imports and asset staging, preserving existing links/backup.
- [Mission Control](../automation_200/mission_control/dist/index.html) reciprocal navigation; [public context graph](PUBLIC_CONTEXT_GRAPH.json) includes CF-LINK-VAULT-001 and CF-SPIDER-001.
- [Node tests](../link-vault/tests/spider-core.test.mjs), [Python tests](../link-vault/tests/test_owner_actions.py), [Spider source acceptance CI](../.github/workflows/spider-sphere-ci.yml).

**Observed during coding:** 9 source-level V8 deterministic assertions passed for duplicate and link rules, plus 3 deadline/stale checks. Do not treat these as complete CI/Pages acceptance. Inspect actual [PR checks](https://github.com/whoiwts110217-creator/CF-0/pull/113/checks) and [Pages runs](https://github.com/whoiwts110217-creator/CF-0/actions/workflows/publish-website.yml).

## Source boundaries
The 22-row public view is derived, not the authoritative 200-task registry or full ChatGPT archive. A human local manifest import supports JSON schema cf0.spider.action_manifest.v1 and 1–100 LOCAL- ID records with stable original HTTPS links; it remains volatile browser memory, **never uploaded or synced**. Raw ChatGPT ZIP exports are not accepted. No private chats, contact workbook rows, account secrets, signed URLs, personal emails, payment credentials or unpublished manuscripts were committed. Missing original ~37-project inventory remains unresolved. Do not clone the existing sole private contact workbook. Spider cannot submit, spend, restart HP, message accounts or count checked-off actions as verified.

## Next three tasks and the owner gate
1. Re-read main and draft PR #113; inspect exact-commit Node/Python/graph CI; repair observed regressions before merge.
2. After authorized merge, inspect Pages exact release, verify site actually serves Core/Shell, inspect existing Sphere and Mission Control backlink. Browser/Pages reachability is not physical iPhone proof.
3. For an eventual owner-side iPhone test (REQUIRED_BEFORE_GATE only after deployment): open the existing Link Vault Home Screen app, refresh, see the robot move on node/lane selection, tap it to focus a sourced action and verify source/project links; optional private manifest and reduced-motion test. If cache is stale, reload Safari first; preserve personal backups.

**Later private ingestion:** only a separately authorized private connector/export adapter can extract authenticated conversation actions, with source coverage and local-only private storage. Never upload raw private chats to public GitHub.
**Rollback:** revert PR #113 bounded files and restore existing PWA v3/rail. No registry/events/HP schedule or external finance state changed. No independent paid customer/income evidence from this work.
