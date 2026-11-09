# CF-SKILL-FOUNDRY-001 — iPhone Skill Foundry

**Parent:** CF-CORE / Caveman Focus; related: AUTO-08, universal continuity UCC-001.

**Origin:** User asked for a real iPhone-compatible skill creator with contextual `?` controls; methodology references publicly available MIT-licensed Superpowers ZH and user-supplied case examples. This web app is a separate addition and does not modify Mission Control.

**Usage:** Once deployed, open `https://whoiwts110217-creator.github.io/CF-0/skill-foundry/` in iPhone Safari, then Share → Add to Home Screen. A URL alone does not mean the native iOS version is App Store distributed.

**Function:** Local deterministic generator produces `SKILL.md`, `EVALS.json`, `SYNTHESIS_PROMPT.md` files and ZIPs; field descriptions are hidden until the adjacent `?` is tapped. Drafts stay in browser storage. No API requests, ChatGPT account control, finance actions, or agent background executor.

**Source evidence:** local generator tests 12/12 pass in Node. GitHub Pages deployment and physical-iPhone runtime should be confirmed separately.

**Privacy:** no secrets or personal accounts stored on GitHub. User-entered private draft text remains in that browser's localStorage unless explicitly exported/shared. Don't enter confidential material on shared devices.

**Rollback:** revert the isolated `iphone-skill-foundry/` addition and the single deployment copy step; no CF-200 registry progress is credited.

## iPhone ZIP/File export recovery (source-stage hardening)

1. For a ZIP, tap **Share / Files**, choose **Save to Files** when iOS supports file sharing, and confirm its location in Files. A returned share action does not prove the file was saved.
2. If the Share Sheet is unavailable, the app **requests a browser download**. Check Safari's Downloads indicator and the Files app's Downloads folder. A download request is not a verified completed file.
3. If that fails, choose **Download selected file**, or use **Copy file** to preserve the currently selected SKILL.md / EVALS.json / prompt text. **Export editable project** backs up the editable form as JSON. Download errors are shown next to the controls.
4. On cancellation, nothing is silently downloaded; retry deliberately. Drafts stored in the current browser do not sync to other accounts or phones.

**Verification:** new zero-dependency Node simulated-browser interaction tests cover ZIP structure, blocked download, supported/unsupported/cancelled/failed share, selected file, and editable-project fallback. Existing Python package checks remain. Physical iPhone and installed-home-screen flows still require device-level confirmation.

**Continuity/permissions:** this narrow UI export improvement relates to CF-SKILL-FOUNDRY-001, UCC-001, and [CF0-SKILL-EVOL-001](https://github.com/whoiwts110217-creator/CF-0/pull/49) (draft PR; not merged into main). No remote API, new SDK, HP access, account control, financial action, background worker or automatic skill installation was added. Roll back by reverting the scoped export patch after review; preserve all existing draft data and functionality.
