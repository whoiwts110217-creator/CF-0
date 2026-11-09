# New agent skills surveyed — November 9, 2026

**Scope:** Public GitHub READMEs were read via a GitHub connector, plus a broader web discovery search and the ChatGPT installed skill catalog (65 available plugin skill entries). Neither popularity-list rankings nor self-reported performance numbers were independently benchmarked. No outside skill installed; no private data transmitted to any skill.

| Priority | Source | Tested/verified source property | Candidate use for CF-0 | Caution |
| --- | --- | --- | --- | --- |
| 1 | [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) | README describes durable `task_plan.md`, `findings.md`, `progress.md` plus context recovery hooks | Improve AUTO-08/CF-200 resumability and prevent lost work on long conversations | The durable files/hooks require a compatible signed-in execution environment. Do not claim ChatGPT account automation is already installed |
| 2 | [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt) | README describes held-out-gated text optimization; `SkillOpt-Sleep` offline replay added July 2026 | Next step beyond Darwin's qualitative review: automated held-out benchmarking of skill deltas | Requires actual agent runs and suitable API/harness. Do not start paid inference or nightly sessions unapproved |
| 3 | [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | README has reconnaissance/coverage ledger, independently validated findings, classified evidence | Audit account-master permissions, public/private HP handoffs, browser input trust | Security findings are not verified merely by generated narrative. Restrict to defensive CF-0 owned assets |
| 4 | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | README offers design critique/audit, deterministic rules, product-design context | Improve iPhone Skill Foundry/Mission Control UX, readable `?` descriptions, reduced clutter | Do not overwrite the user's visual identity or remove working UI; may need JS tooling |
| 5 | [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | README describes architecture/relationship graphing and visualization | Map Caveman Focus projects, dependencies, registries, capabilities and evidence links | Cloud offering may transmit code/data. Prefer local-only inspection; do not upload private archives |
| 6 | [mattpocock/skills](https://github.com/mattpocock/skills) | README promotes small composable engineering skills and issue-tracker integration | Tight, focused tools for task quality without another monolithic operator | Import specific practices, not everything; external installs require approval |

## Recommended adoption order, without new dependencies

1. **Immediately:** emulate Planning-with-Files' persistent triple-state pattern *within existing CF-0 mission board/continuity store*, avoiding a competing status source. Map: current queue ↔ task plan; source/provenance ↔ findings; immutable events/checkpoints ↔ progress.
2. **Now:** borrow Cloudflare's coverage ledger and independent verification distinction to make skill audits falsifiable. Require `confirmed / needs_validation / rejected` for security findings and preserve source/line evidence.
3. **Next:** use Impeccable-style narrow UI critique on the existing iPhone Skill Foundry, especially `?` help, clarity, export errors, offline state and Add to Home Screen instructions; test before changing existing UI.
4. **When actual executor tests are available:** try SkillOpt's held-out edit loop against the `CF0-SKILL-EVOL-001` evidence gate. Research is not deployment.
5. **Optional:** evaluate Graphify local mode on sanitized public code to visualize project relationship graph; do not mix private source identities into public visualizations.

**Key finding:** Most gains come from building a reliable experiment/evidence loop around existing capabilities rather than installing large collections. CF-0 already has the continuity spine, append-only events, regression tests and a phone-oriented skill creator; integrate narrowly, keep it source-verified, and test behavior separately.