# CF-0 — Working-system operating practices, original adaptation pilot

**Continuity ID:** AUTO-08 (P0 single-tab conversation continuation); parent CF-CORE; related CF-GOV, AUTO-02, AUTO-03, FIN-01, FIN-04, UCC-001.
**Owner instruction:** November 9, 2026 — study comparable projects and real operating businesses, learn their practices without copying their code, and turn Caveman Focus into an actually working system.
**Source baseline:** CF-0 main commit `305a3ad1a03f158df1e614c4e84d08814ffc8edb` at review, with current three operating prompts read in the canonical order. New code is proposed on `improve/auto08-durable-exact-ack-20261109` and must not be called deployed without actual account/device evidence.
**Classification:** public-safe source change + operational acceptance contract; NOT a production launch, authenticated account session, physical-HP attestation, grant award, or verified income.

## Real systems studied: mechanisms, not code

| Working reference | Practice observed | CF-0 adaptation and boundary |
| --- | --- | --- |
| [Temporal activity error handling](https://github.com/temporalio/documentation/blob/main/docs/develop/python/best-practices/error-handling.mdx) and [design patterns](https://docs.temporal.io/design-patterns) | Distinguish durable workflow state from activities whose side effects can repeat after a worker crash | Persist a command-attempt state *before* the keyboard effect; if outcome is uncertain, do not resend automatically |
| [LangGraph durable execution and idempotency](https://github.com/langchain-ai/docs/blob/main/src/oss/langgraph/functional-api.mdx) | Persist checkpoints, replay known results, and use idempotency keys or external verification for actions with side effects | Require a new, specific observed user command and a stable assistant reply before recording completion; preserve uncertain outcomes |
| [Browser Harness](https://github.com/browser-use/browser-harness) | Real browser session control is a separately authorized activity; no claim of login without the real owner browser | Keep one preexisting Chrome ChatGPT tab, no new browser, no mouse coordinates or session export to GitHub |
| [Activepieces workflow integrations](https://www.activepieces.com/pieces/webhook) | An integration has an explicit trigger/action contract and a separately connected account | Do not enable the master dashboard's provider controls merely because a public integration description exists |

These references informed the *acceptance criteria*. **No third-party code, dependencies, services, paid APIs or licenses were imported into CF-0.**

## Small, tested source deliverable

**Observed original gap:** AUTO-08 recognized an increased user-message count as proof of send. That can be confused by an unrelated new user message. Its in-flight attempt was persisted even before navigation, so an interrupted pre-send attempt could be treated as an uncertain external side effect.

**Proposed patch:**
- Preserve current Chrome-extension architecture and exact `continue` keyboard send.
- Persist `pre_send` while the worker navigates/focuses the selected tab. Before sending any keyboard side effect, persist `maybe_sent`. Crash or interruption after that boundary requires human review; never mark an uncertain send as completed or auto-retry it.
- Verify the *exactly one newly visible user turn* is literal `continue` without storing any other user text. Only a later stable assistant reply may complete the checkpoint.
- Preserve older unknown `in_flight` states as uncertain. Failing DOM checks stop safely rather than inventing success.

**Explicit limitation:** `primary` / `secondary` are still user-selected labels, **not authenticated account identities**. The first real signed-in browser test remains a separate owner-local acceptance gate. DOM layouts may change.

## What a functioning business must demonstrate

The framework can only claim its business outcome after a sequence of independently observable events:

| Stage | Required evidence | False success to reject |
| --- | --- | --- |
| Value | One stranger completes the free 60-second clarity exercise and records an optional, consented result | A published exercise link |
| Delivery | One user receives the offered file/service, can open it on the promised device, and confirms useful output | A generated file or a passing unit test |
| Payment | A provider-origin donation or customer payment is confirmed and recorded privately once | A cash tag, grant submission, price or checkout page |
| Reliability | The same approved task can be restarted after simulated failure without duplicate external action | A running animation or optimistic button |
| Trust | Every public claim links to the evidence at the correct level; no private chats, secrets or person-level finances appear in public GitHub | Counts of files, tasks or mock operations |

**Economic acceptance (not accomplished here):** first independently verified outside payment and completed delivery; then a repeatable no-extra-subscription process. Do not claim revenue, customer retention or sustained operations from this document.

## Safe release path and rollback

1. **Source:** Node mock tests pass for exact user-turn acknowledgement, pre-send cancellation, unknown send and restart uncertainty, and strict one-tab rule. GitHub Actions PR run must be confirmed before merge.
2. **Human/device:** Opt-in owner performs a one-chat, correct-account Chrome test. Check the literal `continue`, the assistant's actual response, and zero additional tabs; deliberately exercise an interruption, requiring no automatic duplicate. Keep credentials local.
3. **System:** Separately verify authenticated account identity, external provider confirmation receipts, Windows origin and global STOP coverage. None is granted by this patch.
4. **Business:** Test one no-pressure value/delivery/payment loop with actual external evidence before public claims of earnings or success.

**Do not replace or silently stop:** the public relay's three-action allowlist, HP schedules, Notepad history/regression, master dashboard, donor pages, grant watch, creative/research branches or private archives.

**Rollback:** revert this feature branch's AUTO-08 source/tests/docs; do not erase unknown-sent attempts or silently enable resend. Keep the prior commit and operation history in Git.

**Next verifiable action:** obtain PR CI results, then a single explicitly authorized signed-in browser acceptance test. No automation was started or account was contacted by this source change.
