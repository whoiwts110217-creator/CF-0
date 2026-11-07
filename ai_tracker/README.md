# AI Tracker — CF-0 experimental branch

Goal: auditably measure independent AI-agent discovery, outreach, replies, and verified contributions. No paid services, secrets, autonomous posting, or HP access.

## State machine

`discovered → drafted → posted → responded → verified`; rejection can occur before verification. Every state change requires a ledger entry. **Posted** requires a public posting URL; **responded** requires a public reply URL; **verified** requires a public evidence URL plus a reproducible test. A discovery is never counted as contact.

## Usage

```sh
python -m ai_tracker.tracker --ledger ai_tracker/local-events.jsonl record --event discover --target "Example network" --evidence "https://example.org" --operator "CF-0"
python -m ai_tracker.tracker --ledger ai_tracker/local-events.jsonl report
python -m unittest discover -s ai_tracker/tests -v
```

`local-events.jsonl` is local working data; review and redact before any public commit. Public event evidence must not include private conversations, API tokens, account details, or personally identifying information.

The [open agent challenge](https://github.com/whoiwts110217-creator/CF-0/issues/16) is unpaid. The [pioneer reward draft](../docs/FAIR_PLAY_FAIR_PAY_PIONEER_DRAFT.md) is unfunded, nonbinding, and not an active bounty. No claims of verified external responses yet.

## Acceptance gates

- Standard-library unit tests pass on Windows/Linux.
- All events append-only and validated.
- Report distinguishes discovery, draft, post, reply, and independently verified contribution.
- A public URL is required before reporting an actual post or response.
- No secret storage or autonomous third-party posting.
