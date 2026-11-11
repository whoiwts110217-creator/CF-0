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


---

## Complete cost/no-third-party-memory metadata audit — 2026-11-11

**Owner constraints, effective immediately:** $0 spending; no automatic charges, credit-card gates, upgrades, ad buys, paid API keys, subscriptions, trials that could renew, billable add-ons, or purchases; no third-party knowledge/memory/backup databases or new storage services. Free credits only when they cannot cause card charges or overages. Existing owner-controlled local files and public-safe CF-0 code source are preferred. This does not authorize deletion of user data or existing capabilities.

**Scope/evidence:** 166 installed skill descriptions returned from `skills__list` across 30 groups. All metadata classified by plugin family and narrow overrides; full skill instructions were read only for selected high-priority examples. Service pricing comes from linked public official pricing pages; **no user's plan, credit balance, payment method, subscriptions, billing or runtime was inspected**. A plugin skill present does not mean its commercial endpoint is free, connected, available or already charged. Classification is conservative and not a legal license determination.

**Decision policy:** `KEEP` (no extra external cost found for local/guidance path), `FREE-CAPPED` (must verify no-card free usage and stop at hard cap), `LOCAL-ONLY`, `AVOID-STORAGE`, `BLOCK-*` (don't invoke for current $0 mission), `FREE-ONLY-VERIFY` and `WORK-GATED` (not generally available in this chat). Never auto-uninstall on inferred redundancy; exact target and data-retention consequences must be approved.

### Group coverage and cost exposure

| Skill family | Skills | Risk/routing | Why |
|---|---:|---|---|
| openai-templates | 20 | KEEP | Template instructions; no separate metered provider identified |
| app-6a314a73f8ac819195b0d55e36b9c609 | 19 | FREE-CAPPED | Firecrawl: published 1,000 credits/month; no card on Free |
| sales | 18 | KEEP-CONTEXT | Sales guidance included as skills; connected CRM costs/rights unverified |
| app-69dd11f3e50c8191b1ca48d03cf7e2ad | 14 | FREE-CAPPED | vidIQ Free: 150 AI credits/month |
| ads-manager | 14 | BLOCK-ACTIVE | Ads campaign spending if launched; US minimum daily budget $25 per official help |
| agentbroko | 11 | LOCAL-PREFERRED | Video Forge is MIT-licensed local-first; FFmpeg/Python required |
| product-design | 10 | WORK-GATED | Work/Sites mode requirements; pricing for downstream external builders unknown |
| caveman-focus-skill-forge | 8 | KEEP | Existing private skill instructions, no new external fee identified |
| app-69312da8e4dc81919370cb86fd172b6c | 7 | FREE-ONLY-VERIFY | Adobe Express has limited Free; Photoshop/premium products subscribed |
| google-drive | 5 | AVOID-STORAGE | External hosted file storage and docs |
| base44 | 5 | AVOID-STORAGE | Free builder 25 message and 100 integration credits/month, hosted database/storage |
| app-69f0dc45f6048191876c14c1016fe778 | 5 | FREE-CAPPED | Descript Free: 1 media hour/month, 100 one-time AI credits (pricing examples vary) |
| app-69fb9378663481919a68e8a2109644e5 | 4 | BLOCK-BILLING-RISK | Parallel $5 monthly promo requires card in published offer; excess billed |
| plugin-creator | 3 | KEEP | Local plugin package/host tool use; separate meter not established |
| airtable | 3 | AVOID-STORAGE | Cloud database with free tier and paid seats |
| app-6a2aa7768fe881919ad20644669ca2fe | 3 | LOCAL-ONLY | Scopture Free offers offline drawings and local Python; cloud plans paid |
| shopify | 2 | BLOCK-SUBSCRIPTION | Store trial; selling requires paid plan and transaction fees |
| mockflow | 2 | BLOCK-COMMERCIAL | Free Basic: personal/nonprofit only, commercial requires paid plan |
| app-6a8759c2dba48191b391f3915cc0ee5f | 2 | BLOCK-METERED | UserTold billed per recorded interview minute; prepaid balance |
| writing-style | 1 | KEEP-CONTEXT | Writing skill; third-party storage not required for current task |
| app-69ea4ed2cf7c8191b742ef3622479ddd | 1 | FREE-CAPPED | Exa Starter: $10 credits/month + onboarding; no payment method required |
| browser | 1 | KEEP | Read-only Chat browser; Work control depends on runtime |
| app-6a8f2681f7ec8191957fe2883676c9d2 | 1 | FREE-CAPPED | StewAI Free: 500 credits/month; runs consume credits |
| app-6ab55e5b36708191aaba731d3e039444 | 1 | BLOCK-MEMORY-PAID | Pickaxe paid Gold+ plans and hosted knowledge/memory tools |
| template-creator | 1 | KEEP | Template instructions; no extra usage price verified |
| presentations-router | 1 | KEEP | Presentation router; triggers only on explicit selection |
| pdf-router | 1 | KEEP | PDF router; triggers only on explicit selection |
| documents-router | 1 | KEEP | Document router; triggers only on explicit selection |
| plugin-management | 1 | KEEP | Installed plugin management tool; no separate fee observed |
| spreadsheets-router | 1 | KEEP | Spreadsheet router; triggers only on explicit selection |

### Individual routing classification (all 166 installed descriptions)

| Skill URI suffix | Policy | Guardrail |
|---|---|---|
| `ads-manager/ads-manager-account-admin` | BLOCK-ACTIVE | No campaign publishing or paid ads; informational reading only |
| `ads-manager/ads-manager-actionable-review` | BLOCK-ACTIVE | No campaign publishing or paid ads; informational reading only |
| `ads-manager/ads-manager-ad-creation` | BLOCK-ACTIVE | No campaign publishing or paid ads; informational reading only |
| `ads-manager/ads-manager-business-agent-setup` | BLOCK-ACTIVE | No campaign publishing or paid ads; informational reading only |
| `ads-manager/ads-manager-delivery-recovery` | BLOCK-ACTIVE | No campaign publishing or paid ads; informational reading only |
| `ads-manager/ads-manager-entity-management` | BLOCK-ACTIVE | No campaign publishing or paid ads; informational reading only |
| `ads-manager/ads-manager-help` | BLOCK-ACTIVE | No campaign publishing or paid ads; informational reading only |
| `ads-manager/ads-manager-insights` | BLOCK-ACTIVE | No campaign publishing or paid ads; informational reading only |
| `ads-manager/ads-manager-onboarding` | BLOCK-ACTIVE | No campaign publishing or paid ads; informational reading only |
| `ads-manager/ads-manager-review` | BLOCK-ACTIVE | No campaign publishing or paid ads; informational reading only |
| `ads-manager/ads-manager-setup` | BLOCK-ACTIVE | No campaign publishing or paid ads; informational reading only |
| `ads-manager/ads-manager-start-agent` | BLOCK-ACTIVE | No campaign publishing or paid ads; informational reading only |
| `ads-manager/ads-manager-starter-campaign` | BLOCK-ACTIVE | No campaign publishing or paid ads; informational reading only |
| `ads-manager/draft-business-agent` | BLOCK-ACTIVE | No campaign publishing or paid ads; informational reading only |
| `agentbroko/audio-mixer` | LOCAL-PREFERRED | Run only in bounded local environment; optional integrations excluded |
| `agentbroko/caption-translator` | LOCAL-PREFERRED | Run only in bounded local environment; optional integrations excluded |
| `agentbroko/content-series-planner` | LOCAL-PREFERRED | Run only in bounded local environment; optional integrations excluded |
| `agentbroko/pdf-playbook` | LOCAL-PREFERRED | Run only in bounded local environment; optional integrations excluded |
| `agentbroko/pdf-tools` | LOCAL-PREFERRED | Run only in bounded local environment; optional integrations excluded |
| `agentbroko/script-storyboard-writer` | LOCAL-PREFERRED | Run only in bounded local environment; optional integrations excluded |
| `agentbroko/seo-metadata-writer` | LOCAL-PREFERRED | Run only in bounded local environment; optional integrations excluded |
| `agentbroko/social-exporter` | LOCAL-PREFERRED | Run only in bounded local environment; optional integrations excluded |
| `agentbroko/thumbnail-generator` | LOCAL-PREFERRED | Run only in bounded local environment; optional integrations excluded |
| `agentbroko/video-edit` | LOCAL-PREFERRED | Run only in bounded local environment; optional integrations excluded |
| `agentbroko/video-forge` | LOCAL-PREFERRED | Run only in bounded local environment; optional integrations excluded |
| `airtable/airtable-cli` | AVOID-STORAGE | Do not use as Caveman Focus storage/memory |
| `airtable/airtable-filters` | AVOID-STORAGE | Do not use as Caveman Focus storage/memory |
| `airtable/airtable-overview` | AVOID-STORAGE | Do not use as Caveman Focus storage/memory |
| `app-69312da8e4dc81919370cb86fd172b6c/adobe-batch-edit-photos` | FREE-ONLY-VERIFY | Only no-charge features; no free trials that renew |
| `app-69312da8e4dc81919370cb86fd172b6c/adobe-create-mockups` | FREE-ONLY-VERIFY | Only no-charge features; no free trials that renew |
| `app-69312da8e4dc81919370cb86fd172b6c/adobe-create-social-variations` | FREE-ONLY-VERIFY | Only no-charge features; no free trials that renew |
| `app-69312da8e4dc81919370cb86fd172b6c/adobe-design-from-template` | FREE-ONLY-VERIFY | Only no-charge features; no free trials that renew |
| `app-69312da8e4dc81919370cb86fd172b6c/adobe-fonts` | FREE-ONLY-VERIFY | Only no-charge features; no free trials that renew |
| `app-69312da8e4dc81919370cb86fd172b6c/adobe-retouch-portraits` | FREE-ONLY-VERIFY | Only no-charge features; no free trials that renew |
| `app-69312da8e4dc81919370cb86fd172b6c/adobe-edit-quick-cut` | FREE-ONLY-VERIFY | Only no-charge features; no free trials that renew |
| `app-69dd11f3e50c8191b1ca48d03cf7e2ad/vidiq-channel-audit` | FREE-CAPPED | No Boost/MAX upgrade; feature-level access unverified |
| `app-69dd11f3e50c8191b1ca48d03cf7e2ad/vidiq-comment-insights` | FREE-CAPPED | No Boost/MAX upgrade; feature-level access unverified |
| `app-69dd11f3e50c8191b1ca48d03cf7e2ad/vidiq-competitor-watchlist` | FREE-CAPPED | No Boost/MAX upgrade; feature-level access unverified |
| `app-69dd11f3e50c8191b1ca48d03cf7e2ad/vidiq-get-started` | FREE-CAPPED | No Boost/MAX upgrade; feature-level access unverified |
| `app-69dd11f3e50c8191b1ca48d03cf7e2ad/vidiq-new-upload-review` | FREE-CAPPED | No Boost/MAX upgrade; feature-level access unverified |
| `app-69dd11f3e50c8191b1ca48d03cf7e2ad/vidiq-next-video-planner` | FREE-CAPPED | No Boost/MAX upgrade; feature-level access unverified |
| `app-69dd11f3e50c8191b1ca48d03cf7e2ad/vidiq-packaging-studio` | FREE-CAPPED | No Boost/MAX upgrade; feature-level access unverified |
| `app-69dd11f3e50c8191b1ca48d03cf7e2ad/vidiq-retention-analysis` | FREE-CAPPED | No Boost/MAX upgrade; feature-level access unverified |
| `app-69dd11f3e50c8191b1ca48d03cf7e2ad/vidiq-shorts-inspiration` | FREE-CAPPED | No Boost/MAX upgrade; feature-level access unverified |
| `app-69dd11f3e50c8191b1ca48d03cf7e2ad/vidiq-trend-radar` | FREE-CAPPED | No Boost/MAX upgrade; feature-level access unverified |
| `app-69dd11f3e50c8191b1ca48d03cf7e2ad/vidiq-video-breakdown` | FREE-CAPPED | No Boost/MAX upgrade; feature-level access unverified |
| `app-69dd11f3e50c8191b1ca48d03cf7e2ad/vidiq-video-ideas` | FREE-CAPPED | No Boost/MAX upgrade; feature-level access unverified |
| `app-69dd11f3e50c8191b1ca48d03cf7e2ad/vidiq-video-metadata` | FREE-CAPPED | No Boost/MAX upgrade; feature-level access unverified |
| `app-69dd11f3e50c8191b1ca48d03cf7e2ad/vidiq-youtube-seo` | FREE-CAPPED | No Boost/MAX upgrade; feature-level access unverified |
| `app-69ea4ed2cf7c8191b742ef3622479ddd/Search` | FREE-CAPPED | No Developer/PAYG activation |
| `app-69f0dc45f6048191876c14c1016fe778/create-video` | FREE-CAPPED | Avoid paid projects/top-ups; no cloud memory |
| `app-69f0dc45f6048191876c14c1016fe778/edit-project` | FREE-CAPPED | Avoid paid projects/top-ups; no cloud memory |
| `app-69f0dc45f6048191876c14c1016fe778/export-timeline` | FREE-CAPPED | Avoid paid projects/top-ups; no cloud memory |
| `app-69f0dc45f6048191876c14c1016fe778/export-transcript` | FREE-CAPPED | Avoid paid projects/top-ups; no cloud memory |
| `app-69f0dc45f6048191876c14c1016fe778/publish-project` | BLOCK-PUBLISH | No external publish without fresh authorization |
| `app-69fb9378663481919a68e8a2109644e5/parallel-deep-research` | BLOCK-BILLING-RISK | No card registration, no usage until automatic overages reliably disabled |
| `app-69fb9378663481919a68e8a2109644e5/parallel-search-setup` | BLOCK-BILLING-RISK | No card registration, no usage until automatic overages reliably disabled |
| `app-69fb9378663481919a68e8a2109644e5/parallel-web-extract` | BLOCK-BILLING-RISK | No card registration, no usage until automatic overages reliably disabled |
| `app-69fb9378663481919a68e8a2109644e5/parallel-web-search` | BLOCK-BILLING-RISK | No card registration, no usage until automatic overages reliably disabled |
| `app-6a2aa7768fe881919ad20644669ca2fe/duc` | LOCAL-PREFERRED | Local Python .duc operations |
| `app-6a2aa7768fe881919ad20644669ca2fe/scopture` | BLOCK-CLOUD | Remote drawing workspace unless an explicitly local path |
| `app-6a2aa7768fe881919ad20644669ca2fe/scopture-cli` | LOCAL-ONLY | Use only with local .duc files, no remote targets |
| `app-6a314a73f8ac819195b0d55e36b9c609/brand-identity` | FREE-CAPPED | Reject paid plan/PAYG; account balance not checked |
| `app-6a314a73f8ac819195b0d55e36b9c609/business-contact-research` | FREE-CAPPED | Reject paid plan/PAYG; account balance not checked |
| `app-6a314a73f8ac819195b0d55e36b9c609/design` | FREE-CAPPED | Reject paid plan/PAYG; account balance not checked |
| `app-6a314a73f8ac819195b0d55e36b9c609/enrich-lead` | FREE-CAPPED | Reject paid plan/PAYG; account balance not checked |
| `app-6a314a73f8ac819195b0d55e36b9c609/fantasy-sports` | FREE-CAPPED | Reject paid plan/PAYG; account balance not checked |
| `app-6a314a73f8ac819195b0d55e36b9c609/find-leads` | FREE-CAPPED | Reject paid plan/PAYG; account balance not checked |
| `app-6a314a73f8ac819195b0d55e36b9c609/firecrawl` | FREE-CAPPED | Reject paid plan/PAYG; account balance not checked |
| `app-6a314a73f8ac819195b0d55e36b9c609/firecrawl-deep-research` | FREE-CAPPED | Reject paid plan/PAYG; account balance not checked |
| `app-6a314a73f8ac819195b0d55e36b9c609/flights-and-hotels` | FREE-CAPPED | Reject paid plan/PAYG; account balance not checked |
| `app-6a314a73f8ac819195b0d55e36b9c609/get-started` | FREE-CAPPED | Reject paid plan/PAYG; account balance not checked |
| `app-6a314a73f8ac819195b0d55e36b9c609/job-postings` | FREE-CAPPED | Reject paid plan/PAYG; account balance not checked |
| `app-6a314a73f8ac819195b0d55e36b9c609/local-businesses` | FREE-CAPPED | Reject paid plan/PAYG; account balance not checked |
| `app-6a314a73f8ac819195b0d55e36b9c609/markets-and-filings` | FREE-CAPPED | Reject paid plan/PAYG; account balance not checked |
| `app-6a314a73f8ac819195b0d55e36b9c609/news-coverage` | FREE-CAPPED | Reject paid plan/PAYG; account balance not checked |
| `app-6a314a73f8ac819195b0d55e36b9c609/prices-and-plans` | FREE-CAPPED | Reject paid plan/PAYG; account balance not checked |
| `app-6a314a73f8ac819195b0d55e36b9c609/property-listings` | FREE-CAPPED | Reject paid plan/PAYG; account balance not checked |
| `app-6a314a73f8ac819195b0d55e36b9c609/read-docs` | FREE-CAPPED | Reject paid plan/PAYG; account balance not checked |
| `app-6a314a73f8ac819195b0d55e36b9c609/seo-audit` | FREE-CAPPED | Reject paid plan/PAYG; account balance not checked |
| `app-6a314a73f8ac819195b0d55e36b9c609/video-transcripts` | FREE-CAPPED | Reject paid plan/PAYG; account balance not checked |
| `app-6a8759c2dba48191b391f3915cc0ee5f/usertold` | BLOCK-METERED | Do not run interviews; no top-ups |
| `app-6a8759c2dba48191b391f3915cc0ee5f/usertold-recruit-participants` | BLOCK-METERED | Do not run interviews; no top-ups |
| `app-6a8f2681f7ec8191957fe2883676c9d2/stewai-mcp` | FREE-CAPPED | No paid top-ups; remote recipes not used for memory |
| `app-6ab55e5b36708191aaba731d3e039444/pickaxe` | BLOCK-MEMORY-PAID | Do not use |
| `base44/base44-cli` | AVOID-STORAGE | Avoid as memory/backend; no paid plan |
| `base44/base44-remote-dev` | AVOID-STORAGE | Avoid as memory/backend; no paid plan |
| `base44/base44-sandbox` | AVOID-STORAGE | Avoid as memory/backend; no paid plan |
| `base44/base44-sdk` | AVOID-STORAGE | Avoid as memory/backend; no paid plan |
| `base44/base44-troubleshooter` | AVOID-STORAGE | Avoid as memory/backend; no paid plan |
| `browser/control-browser` | KEEP | No billable external services or unapproved purchases |
| `caveman-focus-skill-forge/continuity-guardian` | KEEP | Do not use external account-provisioning for storage |
| `caveman-focus-skill-forge/evidence-to-action` | KEEP | Do not use external account-provisioning for storage |
| `caveman-focus-skill-forge/forge-new-skills` | KEEP | Do not use external account-provisioning for storage |
| `caveman-focus-skill-forge/install-skills-in-chatgpt` | KEEP | Do not use external account-provisioning for storage |
| `caveman-focus-skill-forge/no-cost-account-provisioning` | AVOID-STORAGE | Skill includes external memory backups; do not invoke |
| `caveman-focus-skill-forge/root-cause-debugging` | KEEP | Do not use external account-provisioning for storage |
| `caveman-focus-skill-forge/skill-cartographer` | KEEP | Do not use external account-provisioning for storage |
| `caveman-focus-skill-forge/skill-evaluation-lab` | KEEP | Do not use external account-provisioning for storage |
| `documents-router/document` | KEEP | Use existing authorized local artifact tools |
| `google-drive/google-docs` | AVOID-STORAGE | Do not use as CF memory/storage; existing documents only if specifically requested |
| `google-drive/google-drive` | AVOID-STORAGE | Do not use as CF memory/storage; existing documents only if specifically requested |
| `google-drive/google-drive-comments` | AVOID-STORAGE | Do not use as CF memory/storage; existing documents only if specifically requested |
| `google-drive/google-sheets` | AVOID-STORAGE | Do not use as CF memory/storage; existing documents only if specifically requested |
| `google-drive/google-slides` | AVOID-STORAGE | Do not use as CF memory/storage; existing documents only if specifically requested |
| `mockflow/board-conventions` | BLOCK-COMMERCIAL | Do not route CF business/commercial work here |
| `mockflow/connect` | BLOCK-COMMERCIAL | Do not route CF business/commercial work here |
| `openai-templates/artifact-template-analytics-dashboard` | KEEP | Use existing artifact tooling only |
| `openai-templates/artifact-template-business-review` | KEEP | Use existing artifact tooling only |
| `openai-templates/artifact-template-design-report` | KEEP | Use existing artifact tooling only |
| `openai-templates/artifact-template-experiment-analysis` | KEEP | Use existing artifact tooling only |
| `openai-templates/artifact-template-financial-budget` | KEEP | Use existing artifact tooling only |
| `openai-templates/artifact-template-investment-committee-memo` | KEEP | Use existing artifact tooling only |
| `openai-templates/artifact-template-legal-memorandum` | KEEP | Use existing artifact tooling only |
| `openai-templates/artifact-template-market-trends-report` | KEEP | Use existing artifact tooling only |
| `openai-templates/artifact-template-minimal-letterhead` | KEEP | Use existing artifact tooling only |
| `openai-templates/artifact-template-operating-calendar` | KEEP | Use existing artifact tooling only |
| `openai-templates/artifact-template-operating-review` | KEEP | Use existing artifact tooling only |
| `openai-templates/artifact-template-project-kickoff` | KEEP | Use existing artifact tooling only |
| `openai-templates/artifact-template-project-tracker` | KEEP | Use existing artifact tooling only |
| `openai-templates/artifact-template-sales-pipeline` | KEEP | Use existing artifact tooling only |
| `openai-templates/artifact-template-simple-dark-mode` | KEEP | Use existing artifact tooling only |
| `openai-templates/artifact-template-simple-light-mode` | KEEP | Use existing artifact tooling only |
| `openai-templates/artifact-template-strategy-memorandum` | KEEP | Use existing artifact tooling only |
| `openai-templates/artifact-template-system-design` | KEEP | Use existing artifact tooling only |
| `openai-templates/artifact-template-team-alignment` | KEEP | Use existing artifact tooling only |
| `openai-templates/artifact-template-three-statement-forecast` | KEEP | Use existing artifact tooling only |
| `pdf-router/pdf` | KEEP | Use existing authorized local artifact tools |
| `plugin-creator/create-plugin` | KEEP | No new paid dependencies, no third-party store |
| `plugin-creator/prepare-plugin-submission` | KEEP | No new paid dependencies, no third-party store |
| `plugin-creator/update-plugin` | KEEP | No new paid dependencies, no third-party store |
| `plugin-management/plugin-management` | KEEP | No installs or uninstalls without exact owner permission |
| `presentations-router/presentation` | KEEP | Use existing authorized local artifact tools |
| `product-design/audit` | WORK-GATED | No cloud publish/paid service; skip user-context save |
| `product-design/design-qa` | WORK-GATED | No cloud publish/paid service; skip user-context save |
| `product-design/get-context` | WORK-GATED | No cloud publish/paid service; skip user-context save |
| `product-design/ideate` | WORK-GATED | No cloud publish/paid service; skip user-context save |
| `product-design/image-to-code` | WORK-GATED | No cloud publish/paid service; skip user-context save |
| `product-design/index` | WORK-GATED | No cloud publish/paid service; skip user-context save |
| `product-design/research` | WORK-GATED | No cloud publish/paid service; skip user-context save |
| `product-design/share` | WORK-GATED | No cloud publish/paid service; skip user-context save |
| `product-design/url-to-code` | WORK-GATED | No cloud publish/paid service; skip user-context save |
| `product-design/user-context` | AVOID-STORAGE | User-context persistence; do not invoke |
| `sales/analyze-account-signals` | KEEP-CONTEXT | Read/draft with existing access only |
| `sales/build-business-case` | KEEP-CONTEXT | Read/draft with existing access only |
| `sales/build-competitive-brief` | KEEP-CONTEXT | Read/draft with existing access only |
| `sales/demo-exec-and-seller-dash` | KEEP-CONTEXT | Read/draft with existing access only |
| `sales/enrich-company-and-contact-data` | KEEP-CONTEXT | Read/draft with existing access only |
| `sales/find-customer-quotes` | KEEP-CONTEXT | Read/draft with existing access only |
| `sales/find-key-internal-sources` | KEEP-CONTEXT | Read/draft with existing access only |
| `sales/follow-up-after-call` | KEEP-CONTEXT | Read/draft with existing access only |
| `sales/get-rep-call-feedback` | KEEP-CONTEXT | Read/draft with existing access only |
| `sales/index` | KEEP-CONTEXT | Read/draft with existing access only |
| `sales/plan-deal-strategy` | KEEP-CONTEXT | Read/draft with existing access only |
| `sales/prepare-for-meeting` | KEEP-CONTEXT | Read/draft with existing access only |
| `sales/review-forecast` | KEEP-CONTEXT | Read/draft with existing access only |
| `sales/review-rep-call-trends` | KEEP-CONTEXT | Read/draft with existing access only |
| `sales/sales-company-research` | KEEP-CONTEXT | Read/draft with existing access only |
| `sales/sales-leadership-dashboard` | KEEP-CONTEXT | Read/draft with existing access only |
| `sales/sales-presentations` | KEEP-CONTEXT | Read/draft with existing access only |
| `sales/seller-account-dashboard` | KEEP-CONTEXT | Read/draft with existing access only |
| `shopify/shopify` | BLOCK-SUBSCRIPTION | No store activation or orders |
| `shopify/ucp` | BLOCK-PURCHASE | Shopping/checkout purchase actions prohibited under $0 budget |
| `spreadsheets-router/spreadsheet` | KEEP | Use existing authorized local artifact tools |
| `template-creator/template-creator` | KEEP | Local/artifact only |
| `writing-style/write-like-me` | KEEP-CONTEXT | Do not create separate persistent style memory |

### Verified external pricing references (public offer, not this account)

- Firecrawl — https://www.firecrawl.dev/pricing (free monthly 1,000 credits; pay-as-you-go on paid plans only)
- vidIQ — https://vidiq.com/plans/ (Free monthly 150 AI credits; paid Boost/MAX)
- Exa — https://exa.ai/pricing (Starter free $10/month, no payment method; Developer PAYG)
- StewAI — https://www.stewai.com/ (Free 500 credits/month; paid credit use)
- Base44 — https://base44.com/pricing (Free monthly 25 message / 100 integration credits; hosted database)
- Parallel — https://parallel.ai/blog/free-tier-parallel (free monthly credits offered with a card; overages billed)
- UserTold — https://usertold.ai/pricing (prepaid, $0.25/min managed or $0.15/min BYOK plus model costs)
- Shopify — https://help.shopify.com/en/manual/intro-to-shopify/pricing-plans/free-trial (store trial and paid store activation)
- MockFlow — https://mockflow.com/docs/what-the-basic-plan-includes (Basic free only for personal and nonprofit work; commercial needs paid)
- Descript — https://www.descript.com/pricing (Free, limited monthly media and one-time AI credits)
- Adobe Express — https://www.adobe.com/express/pricing (limited Free); Photoshop — https://www.adobe.com/products/photoshop/plans.html (paid/trial)
- Pickaxe — https://pickaxe.co/pricing (listed plans start with paid Gold; memory/knowledge hosted)
- Scopture — https://site.scopture.com/pricing (Free local/offline; Pro cloud paid)
- Airtable — https://airtable.com/pricing (Free cloud plan; higher tiers paid)
- ChatGPT Ads — https://help.openai.com/en/articles/20001210-creating-campaigns-for-chatgpt-ads (US campaign $25/day minimum, billed for delivery)

### Priority route now

**P0 Spider:** `continuity-guardian → root-cause-debugging → skill-cartographer → skill-evaluation-lab` for source inspection, with actual native Python stdlib and local OS tooling only where installed and authorized. Use `agentbroko/video-forge` only for media tasks and after local FFmpeg/Python prerequisites are verified. **Avoid running paid connectors, third-party memory databases or cloud storage.**

**P2 income:** Use existing installed research/search and drafting tools with no card and no paid requests; favor existing public web search and local files over SaaS. Revenue = verified collected funds only. No paid ads or storefront subscriptions.

**Observed test:** Full catalog was enumerated, categorized and persisted; no provider charges, credentials, invoices or free credits inspected/consumed. **166 behavior tests NOT RUN**. Dependencies and billing mode still need account-specific non-billable validation before any service execution.


### Connected free balances — read-only verified, November 11, 2026

- **Firecrawl**: `remainingCredits=967`, `planCredits=1000`; billing period 2026-11-10 to 2026-12-10 UTC. This indicates 33 fewer credits than the stated plan amount but cannot by itself attribute them to any specific task, source, model, chat, card charge, or API usage. Call was `firecrawl_credit_usage(view=current)`; it did not launch paid research.
- **vidIQ**: `type=limited`, `totalCredits=150`, `renewableCredits=150`, `maxRenewableCredits=150`, `addOnCredits=0`, next reset 2026-12-03 UTC. The `vidiq_balance` tool declares a 0-credit call. This does not imply the user owns a paid vidIQ plan; the 150 cap matches the advertised Free tier.
- **Additional full skill instruction reads** (targeted examples): `ads-manager-ad-creation`, `parallel-deep-research`, `firecrawl-deep-research`, `vidiq-video-metadata`, `usertold`, `mockflow/connect`, `exa/Search`, `stewai-mcp`, `agentbroko/video-forge`, `agentbroko/video-edit`, `product-design/index`, `descript/create-video`, `base44/base44-remote-dev`, `pickaxe`, and `skill-cartographer`. The remaining 151 or fewer were classified from skill descriptions plus provider/group pricing; full instruction/behavior coverage is **not complete**. Broad full-text batch scan was blocked by per-call tool limits; it did not establish the missing reads.
- **Not in the skill count:** available connected memory/knowledge applications (including Crosswalk, DeerDawn, AnyDB, and Mori) may expose tools without an installed `SKILL.md` entry. Exclude them from CF-0 memory/storage workflows under the owner's current directive. Do not silently transfer existing files or private conversations into them. Gmail, calendar, and other work-specific integrations are separate from the user’s own persistent memory system.
- **Installation/uninstall:** No plugins or skills removed, no plan changed, no trials initiated, no purchase, no paid quota or payment/card information checked. To actually uninstall a plugin, the owner must specify the exact product and approve any data-loss implications.
