# CF-SKILL-FOUNDRY-001 — iPhone Skill Foundry

**Parent:** CF-CORE / Caveman Focus; related: AUTO-08, universal continuity UCC-001.

**Origin:** User asked for a real iPhone-compatible skill creator with contextual `?` controls; methodology references publicly available MIT-licensed Superpowers ZH and user-supplied case examples. This web app is a separate addition and does not modify Mission Control.

**Usage:** Once deployed, open `https://whoiwts110217-creator.github.io/CF-0/skill-foundry/` in iPhone Safari, then Share → Add to Home Screen. A URL alone does not mean the native iOS version is App Store distributed.

**Function:** Local deterministic generator produces `SKILL.md`, `EVALS.json`, `SYNTHESIS_PROMPT.md` files and ZIPs; field descriptions are hidden until the adjacent `?` is tapped. Drafts stay in browser storage. No API requests, ChatGPT account control, finance actions, or agent background executor.

**Source evidence:** local generator tests 12/12 pass in Node. GitHub Pages deployment and physical-iPhone runtime should be confirmed separately.

**Privacy:** no secrets or personal accounts stored on GitHub. User-entered private draft text remains in that browser's localStorage unless explicitly exported/shared. Don't enter confidential material on shared devices.

**Rollback:** revert the isolated `iphone-skill-foundry/` addition and the single deployment copy step; no CF-200 registry progress is credited.
