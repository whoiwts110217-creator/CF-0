# CF-0 free-browser promotion monitoring — no TinyFish subscription

**Continuity ID:** CF-DONOR-001 / FIN-09-FREE-BROWSER-001  
**Date initiated:** November 9, 2026 ET.  
**Parent:** CF-0 / Donation Growth / FIN-09; **related:** CF-CORE Clarity Card, public First Drop, UCC-001, CF-MESH-001, public GitHub Actions, AUTO-08 (unchanged).  
**Owner direction:** "Find a replacement free" after the TinyFish wallet showed a negative balance and paid agent-step metering. Subsequent "continue" authorized a no-paid-service implementation, **not** spam, unrestricted posting, spending, or account control.

## What was built

- [Source: read-only Playwright monitor](../finance/donation_growth/free_browser_monitor.py)
- [Offline regression tests](../finance/donation_growth/tests/test_free_browser_monitor.py)
- [GitHub Actions workflow](../.github/workflows/cf0-free-browser-promotion.yml) · [browse scheduled/manual workflow runs](https://github.com/whoiwts110217-creator/CF-0/actions/workflows/cf0-free-browser-promotion.yml)

Uses **pinned Playwright for Python v1.57.0**, headless Chromium and standard `ubuntu-latest` GitHub-hosted runners for a **public** repository. GitHub's official documentation states that standard GitHub-hosted runners for public repositories are free; paid larger runners and private-repository usage can be different. The repository has not been moved private. No TinyFish, external metered automation API, credentials, GitHub token write permissions, paid subscription, or founder laptop resources are used.

Runs read-only on push to its own source/tests/workflow, manually through **Run workflow**, or **once daily at 13:37 UTC** (off peak; roughly 08:37 EST / 09:37 EDT). The user can operate this on iPhone through the GitHub website. This schedule is a GitHub Actions runner, **not** a new ChatGPT Scheduled Task or an additional AUTO-08 browser tab. GitHub may delay scheduled workflows or auto-disable them after prolonged public repository inactivity.

## Monitored evidence

| Target | What a result means | What it never means |
|---|---|---|
| [Clarity Card](https://whoiwts110217-creator.github.io/CF-0/clarity-card/) | Page returned HTTP 200 and its known headline appeared | A visitor, sale, or useful outcome |
| [First Drop](https://whoiwts110217-creator.github.io/CF-0/first-drop/) | Page returned HTTP 200 and its known headline appeared | A new donor, conversion or referral |
| [Support site](https://caveman-focus-support.whoiwts110217.chatgpt.site/) | HTTP 200 and Caveman Focus text appeared | Cash App integration, funds or receipt |
| [Hype Star](https://hypestar.org/project/caveman-focus) | Public listing only if HTTP 200, title names Caveman Focus and it visibly links to canonical Clarity Card; HTTP 404 means **not publicly visible when checked** | Directory approval after 404, visitor traffic or revenue |
| PromoteIndex ticket #097 | **Unverified historical queue ticket only**; no automated re-submission or query of a rate-limited API | An accepted listing or confirmed publication |

All statuses are recorded in the job's publicly accessible GitHub Actions step summary. Its browser test uses GET navigations only, does not click payment links, does not fill forms, sign in, post, vote, send DMs or inspect personal content. A directory CAPTCHA/403/429/error becomes `unverified`, not a bypass or a rejection. The checker does not claim the identity of a human visitor.

## Reproducible acceptance and failure states

1. Run `python -m unittest discover -s finance/donation_growth/tests -p test_free_browser_monitor.py -v` to check offline status classification, absence of POST/form functionality, and no fabricated donor claims.
2. In GitHub Actions open **CF-0 Free Browser Promotion Check** and inspect a real run's `Test no-cost...`, `Install...`, and `Verify live...` steps. A successful automated test is evidence of source integrity; the actual web results appear separately in `CF-DONOR-001` step summary and `CF0_PROMO_BROWSER_JSON=` log.
3. Verify each observed status in its named source, not from a conversational guess. A failed Playwright install or a blocked public site is a reported limitation; it should not be silently relabeled success.
4. Do not infer this system can access ChatGPT conversations, control the owner's HP, watch payments, publish to Reddit, send an email, or operate a cloud browser session in Work. Those are distinct components/permissions.

## Owner actions and future expansion

**None required** for the read-only workflow after GitHub Actions validates it. If the founder later wants to use an authenticated browser for a site requiring login, prefer the existing ChatGPT Work cloud browser when available in their account; the owner handles the login and any platform-required verification. That is not an extension of this unauthenticated GitHub runner, and provider restrictions still apply.

A future *posting* adapter would require a platform-specific, reviewed authorizing workflow, a legitimate account, anti-spam rules, secrets stored outside the public repository, a no-cost provider check, and explicit public posting scopes; do **not** convert this status checker into account automation by adding credentials or scraping personal profiles. The request to keep promotion active does not authorize automating votes, repeated promotion or unsolicited messages.

## Provenance, privacy, change impact, rollback

Mandatory preflight public main was read in the order:
- operator Git blob `3ee3c9dc7b684064ed45cd75535f0108845119db`;
- continuity Git blob `ed113356205925eb9c0039e74355ba44d4f3369d`;
- Work prompt Git blob `67d6d0e90b9866ed18f043868a7f2f067fb05c0b`.

Public owner capability contract and UCC-001/CF-MESH-001 were checked; original task permissions, owner credit and the existing HP, AUTO-08, CF-200 and funding systems are unchanged. Repository files are intentionally public-safe and contain no login identity, private browser session, tokens, bank accounts or personal messages.

**Status:** source and tests added; first actual GitHub Actions run must be inspected before claiming operational unattended monitoring. The scheduled check is a real GitHub workflow configuration, not a guarantee the site is always reachable or that the run always executes on time.

**Rollback:** revert only the new files named above and the links added to campaign documentation. No prior workflow was deleted or modified; no new ChatGPT automation consumed a scarce task slot. Before any future follow-up, re-read the current public three-prompt boot and this record, reconcile latest GitHub Actions run and original campaign records. **Next permitted action:** inspect real run output, repair any CI failure, and accurately update the public campaign status. Do not pay TinyFish.
