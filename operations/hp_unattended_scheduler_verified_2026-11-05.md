# CF-0 HP unattended relay — first successful scheduled execution

**Date:** November 5, 2026 (Eastern)
**Evidence:** User-supplied Windows status output in the live ChatGPT conversation.
**Attribution:** Kiara Lynn Rose Smith's Caveman Focus.

## Previously
- HP relay `processed: 3`
- Manual Task Scheduler invocation last run: `11:29:29 AM`
- Scheduled next run: `11:31:31 AM`
- New `hp_status` job committed via the connected GitHub account before the scheduled run.

## Subsequent HP status, without another manual relay invocation
```text
CF-0 relay local task status:
{"processed": 4, "queue": "whoiwts110217-creator/CF-0", "tokenless_read": true}
TaskName : CavemanFocusCF0Relay
State    : Ready
LastRunTime    : 11/5/2026 11:31:31 AM
LastTaskResult : 0
NextRunTime    : 11/5/2026 11:36:36 AM
```

## Supported conclusion
A new GitHub command was processed during a scheduled run, as reported by the user's actual Windows PC. This provides real owner-HP evidence for **scheduled, unattended one-way command execution** (phone/ChatGPT → CF-0 public queue → HP allowlisted Python action). Previous successful manual Task Scheduler execution was a separate milestone.

## Important limits
- Evidence is the owner's copied console output, not independent cryptographic machine attestation.
- `processed: 4` records local handling, not automatic result delivery to this chat.
- The relay is currently public, receives only restricted `ping`, `hp_status` and optional read-only `sidecar_verify` commands.
- **No automatic authenticated public reply path or general-purpose Windows command execution has been verified.**
- Schedule requires the HP to be on and its Windows user signed in.
- Next work: add a narrowly scoped secure write-back option for public-safe receipt summaries and verify a request/receipt pair. Do not embed tokens in GitHub or chat.

**Checkpoint note:** This is physical-HP evidence; link it from the CF-200 registry when its matching task and dependencies are validated. Do not increment an unrelated task or alter the 4-item checkpoint counter without evidence.
