# CF-SKILL-FOUNDRY-001 — iPhone Skill Foundry

**Parent:** CF-CORE / Caveman Focus; related: AUTO-08, universal continuity UCC-001.

**Origin:** User asked for a real iPhone-compatible skill creator with contextual `?` controls; methodology references publicly available MIT-licensed Superpowers ZH and user-supplied case examples. This web app is a separate addition and does not modify Mission Control.

**Usage:** Once deployed, open `https://whoiwts110217-creator.github.io/CF-0/skill-foundry/` in iPhone Safari, then Share → Add to Home Screen. A URL alone does not mean the native iOS version is App Store distributed.

## ChatGPT installation handoff (v0.3)

The primary deliverable is now a **ChatGPT-ready, personal skill-plugin request**:

1. Forge the skill pack in Safari.
2. Tap **COPY CHATGPT INSTALL REQUEST**. This copies the complete SKILL.md definitions to the clipboard. An `INSTALL_IN_CHATGPT.md` file is also included in the ZIP.
3. In ChatGPT, open **Plugins**, add **Plugin Creator** if it is available to your account, and start a chat with it.
4. Paste the copied request. Review what Plugin Creator prepares, then approve creating/installing the personal skill-only plugin inside ChatGPT.
5. Verify by invoking the new plugin with `@` and asking it to complete a harmless evaluation task.

**Authority boundary:** The static Foundry website is not authenticated to your ChatGPT account, has no install endpoint, and **cannot** perform the final installation itself. Do not mistake copying the request for an installed skill. Direct Skills editor/upload is an alternate path only for eligible workspaces.

No paid API, subscription, or external runner is required by the Foundry itself. Plugin Creator's own availability and permissions are controlled by ChatGPT.

**Acceptance:** `node iphone-skill-foundry/tests/test_chatgpt_install.cjs` proves that the generated skill definitions and installation request are packaged; genuine activation requires a ChatGPT-side confirmation and an end-to-end plugin invocation.

**Function:** Local deterministic generator produces `SKILL.md`, `EVALS.json`, `SYNTHESIS_PROMPT.md` files and ZIPs; field descriptions are hidden until the adjacent `?` is tapped. Drafts stay in browser storage. No API requests, ChatGPT account control, finance actions, or agent background executor.

**Source evidence:** local generator tests 12/12 pass in Node. GitHub Pages deployment and physical-iPhone runtime should be confirmed separately.

**Privacy:** no secrets or personal accounts stored on GitHub. User-entered private draft text remains in that browser's localStorage unless explicitly exported/shared. Don't enter confidential material on shared devices.

**Rollback:** revert the isolated `iphone-skill-foundry/` addition and the single deployment copy step; no CF-200 registry progress is credited.
