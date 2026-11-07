# AI Tracker handoff for CF-200 Four-Task Executor

Start with the current [operator prompt](../automation_200/MASTER_OPERATOR_PROMPT.md),
[continuity prompt](../automation_200/MASTER_CONTINUITY_PROMPT.md), and
[Work prompt v1.0](../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md)
in that order. This handoff was prepared from
[public main b66f96c5](https://github.com/whoiwts110217-creator/CF-0/commit/b66f96c5b515dd76307f8b644b0e4a775affaa50).
The Work prompt blob was `ee5aa07170ca4c9ec4c0c1ed5e63ee7c8dd3f431`.
The next Work run retrieves all three afresh from public `main`.

## Where to look

| Evidence | Source |
|---|---|
| Actual public replies | [Issue #16](https://github.com/whoiwts110217-creator/CF-0/issues/16) |
| Last published scan, counts, and run links | [AI_TRACKER_STATUS.json](AI_TRACKER_STATUS.json) |
| Monitor and tests | [Python monitor](../ai_tracker/monitor_public_issue.py) · [workflow](../.github/workflows/ai-tracker-monitor.yml) · [runs](https://github.com/whoiwts110217-creator/CF-0/actions/workflows/ai-tracker-monitor.yml) |
| Owner view | [Mission Control AI Tracker](https://whoiwts110217-creator.github.io/CF-0/mission-control/#ai-tracker) |
| Experimental outreach lifecycle ledger | [Existing development branch](https://github.com/whoiwts110217-creator/CF-0/tree/feature/ai-agent-tracker/ai_tracker) |

The [first verified monitor run](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42365084747)
was triggered by a push and published zero comments. The existing monitor also
has a six-hour schedule. The dashboard reads the public status file on load
and on refresh, so a fresh scan can appear without rebuilding Pages.

## What to do on the next executor run

1. Check the published timestamp and `last_check_run_url` against the actual run.
   Use `last_scheduled_run_url` and a successful `schedule` event to verify
   the first timed scan. A partial scan reports its coverage limit.
2. If a non-owner comment appears, use its public link to find the claimed
   reproduction. Review the text as evidence, reproduce the result in an
   isolated test, and record accepted work only with a test or measured outcome.
3. Use the development ledger for future evidence of discovery, authorized
   posting, replies, and verified work. Keep it separate from the Issue #16
   collector. The collector publishes counts and comment links. It leaves
   comment text, usernames, AI identity claims, and contribution decisions
   out of the scan.

Local verification commands

    python -m unittest discover -s ai_tracker/tests -p 'test_monitor_public_issue.py' -v
    node --test automation_200/mission_control/tests/model.test.mjs
