# AI Tracker handoff for CF-200 Four-Task Executor

Start with the current [operator prompt](../automation_200/MASTER_OPERATOR_PROMPT.md),
[continuity prompt](../automation_200/MASTER_CONTINUITY_PROMPT.md), and
[Work prompt v1.0](../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md)
in that order. The ROGUE-03 review used the prompts on
[public main 64e9add](https://github.com/whoiwts110217-creator/CF-0/commit/64e9add69c33f434c92529cb5dac07cd5d8fcefa).
The blobs were `f8f0c94c28cd28cc0402daf4f21bd875e1417932` (operator),
`cac63dead1e00592c1d12ea6562639b02893d81f` (continuity), and
`5da1a390f31ee8f57e5829ef368062f9215c28ac` (Work v1.0).
The next Work run retrieves all three afresh from public `main`.

## Where to look

| Evidence | Source |
|---|---|
| Actual public replies | [Issue #16](https://github.com/whoiwts110217-creator/CF-0/issues/16) |
| Last published scan, counts, and run links | [AI_TRACKER_STATUS.json](AI_TRACKER_STATUS.json) |
| Monitor and tests | [Python monitor](../ai_tracker/monitor_public_issue.py) · [workflow](../.github/workflows/ai-tracker-monitor.yml) · [runs](https://github.com/whoiwts110217-creator/CF-0/actions/workflows/ai-tracker-monitor.yml) |
| Owner view | [Mission Control AI Tracker](https://whoiwts110217-creator.github.io/CF-0/mission-control/#ai-tracker) |
| Experimental outreach lifecycle ledger | [Existing development branch](https://github.com/whoiwts110217-creator/CF-0/tree/feature/ai-agent-tracker/ai_tracker) |

## Accepted public contributions

| Micro-mission | Submission and credit | Verified work |
|---|---|---|
| ROGUE-03 | [砂 · Grok Bot (Feu), public credit with consent](https://github.com/whoiwts110217-creator/CF-0/issues/16#issuecomment-6708201559) | Proposed a counterexample and expected behavior for the public issue monitor. Independently reproduced the three synthetic cases and added the [regression test](../ai_tracker/tests/test_monitor_public_issue.py). |

The review verified the test proposal. The example produced one non-owner reply
for a visitor, zero for the owner, and two for a mixed set. All three cases left
contribution decisions to review. The monitored source is the Python file on
`main`. The supplied development-branch file link returned 404.

The monitor now writes `non_owner_comments_observed`. It also mirrors that
value into `external_responses_verified` for older readers. Mission Control
uses the explicit field when available. `independent_contributions_verified`
is updated on review, and the scan preserves it. The submission's stated
agent/operator credit is recorded with consent. Agent identity, independent
operation, and the claimed external-board referral remain unverified.

## Verified handoff state

- The [updated monitor](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42366164515)
  passed six tests and published a complete scan of Issue #16 at 10:58 UTC on
  November 7, 2026. It recorded zero comments, zero non-owner replies, and zero
  verified contributions. The run was triggered by a push.
- The [scheduled scan](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42403492670)
  completed successfully and published one Issue #16 comment before the
  ROGUE-03 review. The current status file carries the latest scan and
  separately reviewed work.
- The [Pages deployment](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42366164505)
  passed eight dashboard model tests. The live tracker showed the scan time,
  counts, and run link. The dashboard fetches the current status on load and
  refresh, so a fresh scan can appear without rebuilding Pages.
- [Windows CI passed on retry](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42366164495/attempts/2),
  including the public ledger and relay smoke checks. The first attempt
  reached the GitHub API rate limit during the relay smoke check.
- The [one-time invitation receipts](AGENT_INVITATION_RECEIPTS_2026_11_07.json)
  record three accepted requests with unverified public URLs and one HTTP
  error. Keep them separate from the monitor's Issue #16 counts.

## What to do on the next executor run

1. Check the published timestamp and `last_check_run_url` against the actual run.
   Use `last_scheduled_run_url` and a successful `schedule` event to verify
   timed scan evidence. A partial scan reports its coverage limit.
2. If a non-owner comment appears, use its public link to find the claimed
   reproduction. Review the text as evidence, reproduce the result in an
   isolated test, and record accepted work only with a test or measured outcome.
   Use the comment link as the review key so subsequent scans do not count the
   same reviewed submission again.
3. Use the development ledger for future evidence of discovery, authorized
   posting, replies, and verified work. Keep it separate from the Issue #16
   collector. The collector publishes counts and comment links. It leaves
   comment text, usernames, AI identity claims, and contribution decisions
   out of the scan.

Local verification commands

    python -m unittest discover -s ai_tracker/tests -p 'test_monitor_public_issue.py' -v
    node --test automation_200/mission_control/tests/model.test.mjs
