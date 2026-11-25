# CF-0 free-browser promotion monitoring — no TinyFish subscription

**Continuity ID:** CF-DONOR-001 / FIN-09-FREE-BROWSER-001  
**Date initiated:** November 9, 2026 ET.  
**Parent:** CF-0 / Donation Growth / FIN-09; **related:** CF-CORE Clarity Card, public First Drop, UCC-001, CF-MESH-001, public GitHub Actions, AUTO-08 (unchanged).  
**Owner direction:** "Find a replacement free" after the TinyFish wallet showed a negative balance and paid agent-step metering. Subsequent "continue" authorized a no-paid-service implementation, **not** spam, unrestricted posting, spending, or account control.

## What was built

- [Source: read-only Playwright monitor](../finance/donation_growth/free_browser_monitor.py)
- [Offline regression tests](../finance/donation_growth/tests/test_free_browser_monitor.py)
- [GitHub Actions workflow](../.github/workflows/cf0-free-browser-promotion.yml) · [browse scheduled/manual workflow runs](https://github.com/whoiwts110217-creator/CF-0/actions/workflows/cf0-free-browser-promotion.yml)

Uses **pinned Playwright for Python v1.57.0**, headless Chromium and standard `ubuntu-24.04` GitHub-hosted runners (pinned to support Playwright 1.57.0) for a **public** repository. GitHub's official documentation states that standard GitHub-hosted runners for public repositories are free; paid larger runners and private-repository usage can be different. The repository has not been moved private. No TinyFish, external metered automation API, credentials, GitHub token write permissions, paid subscription, or founder laptop resources are used.

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

**Status:** source, tests and workflow deployed. The first Actions run [42747989485](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42747989485) passed the offline test step but **failed before browser navigation** because the then-default Ubuntu 26.04 runner cannot install Chromium under the repository's pinned Playwright 1.57.0. Only this new workflow was changed to the supported standard `ubuntu-24.04` runner (commit [7024d49](https://github.com/whoiwts110217-creator/CF-0/commit/7024d4923f841734b7a13d53490e45bd956c293e)). Its corrected run is subject to separate verification; never count the failed run as live monitoring. The scheduled check is a real GitHub workflow configuration, not a guarantee the site is always reachable or that the run always executes on time.

**Rollback:** revert only the new files named above and the links added to campaign documentation. No prior workflow was deleted or modified; no new ChatGPT automation consumed a scarce task slot. Before any future follow-up, re-read the current public three-prompt boot and this record, reconcile latest GitHub Actions run and original campaign records. **Next permitted action:** inspect real run output, repair any CI failure, and accurately update the public campaign status. Do not pay TinyFish.

## November 10, 2026 — first verified daily schedule-event run

**New evidence superseding only the older “no schedule-event run yet” status below.** GitHub's native Actions record for [run 42834628771](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42834628771) states `event=schedule`, completed `success`; [job 129893459380](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42834628771/job/129893459380) completed offline tests, Chromium installation, four live public GET navigations and the public capability summary. Actual `CF0_PROMO_BROWSER_JSON` in its log, checked at **2026-11-10 14:31:14 UTC**, reported: Clarity Card **HTTP 200**, First Drop **HTTP 200**, support campaign **HTTP 200**; Hype Star profile **HTTP 404**, `not_public_as_checked`. PromoteIndex ticket #097 remained unverified. The JSON explicitly records **0 created posts**, **0 submitted directory entries** and `financial_transactions_checked=false`.

A second **manually dispatched** run [42842578711](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42842578711) succeeded with matching statuses checked at **2026-11-10 15:18:06 UTC**. This validates **one actually executed daily GitHub-hosted check** and another manually requested check; it does not prove permanent scheduling, site visitors, social publication, accepted directory listings, donations, an account/HP session, or revenue. No new subscription, credential or private contact registry was used.

**Continuity:** CF-DONOR-001 / FIN-09 / UCC-001. The original source, tests, and schedule remain unchanged. Next: use existing authorized social account connections or owner-initiated sharing for genuine distribution; do not spam or resubmit the 404 listing blindly. Rollback: revert only this evidence paragraph if subsequent proof shows it materially inaccurate; retain the historical run and older observations.

## First verified real-browser run — November 9, 2026 ET

**PASS:** [GitHub Actions run #42748168761](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42748168761) at source commit `7024d4923f841734b7a13d53490e45bd956c293e`, after pinning Ubuntu 24.04. Steps **offline safety tests**, **Chromium installation**, and **live public navigation** all succeeded. A genuine headless Chromium checked all four allowlisted URLs with no account credentials, posting, payment or paid TinyFish use.

The verified job log printed a structured `CF0_PROMO_BROWSER_JSON=` record dated **2026-11-10T03:15:20Z**:

| Site | Real-browser result | Interpretation |
|---|---|---|
| Clarity Card | HTTP 200, `reachable` | Free tool page served expected heading |
| First Drop | HTTP 200, `reachable` | Public invitation served expected heading |
| Support campaign | HTTP 200, `reachable` | Public appeal displayed Caveman Focus |
| Hype Star listing | HTTP 404, `not_public_as_checked` | Previously submitted listing not visible when checked |
| PromoteIndex ticket #097 | `unverified` | Historical queued submission, not re-queried or resubmitted |

**Status now:** source **implemented**, offline tests **passed**, first manual/push-triggered browser run **verified successful**. **Daily unattended scheduling is configured but has not yet had a recorded `schedule`-event run.** That distinction matters. It does not perform outreach, and no donor, payment, click or accepted directory listing follows from the CI result.

The first pre-fix workflow [#42747989485](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42747989485) remains recorded as a **failed** compatibility attempt; it was not erased or mislabeled. Rollback remains a narrowly scoped Git revert.



## November 10 bootstrap: successful owner run and read-only safeguards

**Owner instruction:** “Bootstrap,” following an owner-triggered GitHub Actions **Run workflow** request on November 10. Current public `main` three-prompt read order was honored: [Master Operator](../automation_200/MASTER_OPERATOR_PROMPT.md) blob `5dad8c17b04a4eb744e5a1474b2ecfb9ddd0abe0`, [Master Continuity](../automation_200/MASTER_CONTINUITY_PROMPT.md) blob `77900acb1c3eb75f8dfd3cef245503d052971479`, and [Work Prompt](../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md) blob `d090f82eaf89d9cd339e7eef248750ebef965e88`. Current [UCC-001](UNIVERSAL_CONTINUITY_CONTRACT.md), [CF-MESH-001](PUBLIC_THREE_CHAT_CONTINUITY_MESH.md), [owner handoff](OWNER_ACTION_HANDOFF_PROTOCOL.md), [capability contract](../automation_200/OWNER_CAPABILITY_CONTRACT.json), relevant source and registry were also consulted. **No new authority, account, fee, API, browser identity or HP action was acquired.**

**Verified owner-triggered run:** [#42842578711](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42842578711), `workflow_dispatch`, completed **success** on November 10 at 15:18 UTC. GitHub-native job evidence confirms offline tests, Chromium installation and browser navigation all passed. Actual structured browser log at `2026-11-10T15:18:06Z` reported HTTP 200 on the Clarity Card, First Drop and support campaign; Hype Star HTTP 404, not public at that time; PromoteIndex #097 still only an unverified historical queue ticket. No visitor, external post, cash receipt, charitable status or donation was established.

**Verified independently scheduled run:** [#42834628771](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42834628771), `schedule`, completed success on November 10, also with a real browser check of all four public URLs. This confirms at least one actual automatic scheduled execution, **not** perpetual availability, hourly operation, account automation or outreach.

**Hardening implemented after the owner run:**

- [Source monitor](../finance/donation_growth/free_browser_monitor.py) now guards browser network requests to **GET/HEAD only**, aborting POST/PUT/PATCH/DELETE requests initiated by untrusted webpage scripts (commit [8241eaf](https://github.com/whoiwts110217-creator/CF-0/commit/8241eaf2f15b5bb9cf4742fffaacb59a5da0ec24)); it also blocks service workers in the isolated browser context (commit [d5b4d1d](https://github.com/whoiwts110217-creator/CF-0/commit/d5b4d1d971e8527036e8ff28dc359731729abbec)). It still uses an unauthenticated, ephemeral browser with no clicks, payments, forms or external posting.
- The browser now checks whether *both* funding pages visibly link to the already-published public Cash App destination **without navigating to it**. This establishes **HTML link presence only**, not that Cash App payments work or that anyone sent money. The initial post-change real browser run [#42854387839](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42854387839) completed success and observed `expected_cash_app_anchor_present=true` on First Drop and the support campaign, while all three campaign pages returned HTTP 200 and the directory listing still returned HTTP 404.
- [Unit tests](../finance/donation_growth/tests/test_free_browser_monitor.py) now exercise the request-method allowlist and reject wrong payment-host impostors (test source commit [24ba40e](https://github.com/whoiwts110217-creator/CF-0/commit/24ba40e48ba16e23c83da633987640823f5d847b)); service-worker enforcement added to the test contract by [16894d9](https://github.com/whoiwts110217-creator/CF-0/commit/16894d96fa8d3b9f6e67bcb7a3d8a555401a3b9e). **Final hardening verified:** [run #42854587700](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42854587700) completed **success**, with **9 offline tests passing**, headless Chromium installation and actual HTTP/DOM navigation passing. Its structured browser log at 2026-11-10T16:27:31Z showed HTTP 200 on the free tool and both fundraising pages, `expected_cash_app_anchor_present=true` on both fundraising pages, and HTTP 404 for Hype Star (still not publicly visible). No payment or third-party post was made. Intermediate successful run [#42854456484](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42854456484) confirmed initial 9-test guard and live browser. The service-worker-specific run is separate.

**System continuity:** CF-200 source registry `automation_200/registry.json` blob `77d548b366ff5dc2070c74e30423a3495c6a73cb` records **91 of 200** source-accepted work orders at the time of this bootstrap, unrelated to the number of browser checks and not evidence of 91 external posts, HP tasks or supporters. Existing CF-200, AUTO-08, HP relay, payment destination and campaign platforms were not changed. No new ChatGPT Scheduled Task was created. Human gate: `NONE` for this read-only monitoring. Rollback: revert only the hardening commits and their matching tests if a verified regression appears; preserve original artifacts and failed-run history.

**Next check:** Inspect the actual final Playwright CI after the service-worker test, then any subsequent `schedule` event; Hype Star remains pending editorial approval until its public page becomes independently visible. Outside posting still requires legitimate site access; this monitor is **not** a free general-purpose TinyFish replacement for authenticated form submissions.
