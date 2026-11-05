# Phone → ChatGPT → HP: Conversational Mission Control

**Priority #1** for Kiara Lynn Rose Smith's Caveman Focus. Date: November 5, 2026.

## Owner interaction contract
The owner speaks or types in their **usual ChatGPT account**, including on an iPhone. Example:
- "HP, report health."
- "HP, check my Sidecar audit."
- "HP, run the approved automation review."
- "HP, show what's blocked."
- "HP, pause the worker."

The assistant interprets the instruction, verifies it fits the owner's current authority and available actions, and submits a structured job through its **connected, authorized GitHub app** into a **separate private mailbox repository**. A Python worker on the physical HP polls that private queue, validates the exact job schema and performs an allowed local action; it writes a correlation ID, digest and result back to the private mailbox. The assistant reads results when invoked or through a supported scheduled follow-up. This is **conversation-mediated PC control**, not a native always-on ChatGPT chat event stream.

```text
iPhone voice/text → same ChatGPT account → authorized GitHub action
              → PRIVATE mailbox queue → Python on HP
              → approved local workflow → receipt in PRIVATE mailbox
              → ChatGPT reads/uses result at next permitted turn/check
```

**Response preference:** The owner requests ACTION WITHOUT CHATTER. When a message is a control command, perform the supported action and keep user-visible output minimal; explain only a blocker, safety-relevant issue, requested report, or result that truly requires attention. The platform might still show tool status, or a minimal response. **Do not claim that silent dispatch is guaranteed by the platform.**

## Current verified reality
- CF-0 contains public Python HP Bridge v0.3 code and Windows CI tests.
- The connected GitHub account currently exposes only public `CF-0`; no linked private mailbox has been found.
- Existing worker allows `ping` and optionally configured read-only `sidecar_verify`. It does **not** yet support arbitrary Windows commands, research tasks, file mutations or chat-triggered automatic execution.
- The owner HP has not demonstrated live private mailbox connectivity in this chat.
- A public GitHub repository is for code and public work reports, **not** a channel for secret credentials or private instructions.

## Upgrade path
1. Create **one owner-controlled PRIVATE mailbox** and authorize its connection to ChatGPT GitHub app. Never post the repo token in chat or public source.
2. Install Bridge v0.3 on HP with local encrypted credential setup; prove one real ping round trip and duplicate suppression.
3. Add a **capability manifest** on HP listing allowed local task/workflow IDs, required arguments, resource ceilings, expected outputs, read/write permissions and stop controls.
4. Add natural-language → structured-job translation in ChatGPT. Only valid job types may cross the mailbox.
5. Support non-destructive `hp_status`, `disk_check`, `sidecar_verify`, `automation_status` first; later allow reviewed file organization, scheduled research, registry updates and business reporting with correct source/rights checks.
6. Verify real HP logs, latency, restart recovery, sender provenance, corruption handling, audit and owner-approved revocation.
7. Expose sanitized task/finance/research results in public CF-0 per publication policy; keep protected account data in the private channel.

**User's declared priority:** AI in charge of the HP, through the same ChatGPT account, with no unsolicited narrative replies. Full control is a roadmap goal, not an accomplished capability. Untrusted files and websites cannot self-authorize code execution.
