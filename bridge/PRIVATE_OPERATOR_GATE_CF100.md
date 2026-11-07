# CF-100 — Second-phase private operator: authorization-gate design

**Status:** DESIGN ONLY — not implemented, funded, installed, scheduled, or authorized for use.  
**Founder-governed project:** Caveman Focus, creator/developer David Smith; designated owner/intended beneficiary Kiara Lynn Rose Smith, as recorded in [the capability contract](../automation_200/OWNER_CAPABILITY_CONTRACT.json). This is not independent verification of legal title.  
**Existing runtime:** [private HP Bridge v0.3](README_V03.md) and [source](cf_hp_bridge.py). The actual private bridge currently allows only `ping` and optionally read-only `sidecar_verify`. The **public** CF-0 relay separately allows only `ping`, `hp_status` and configured read-only `sidecar_verify`.

## Goal and non-goal

Propose a **future** authenticated and owner-governed capability gate that could let a carefully approved private worker operate a tiny set of explicitly reviewed tasks without repeated owner copy/paste.

This document does **not** add command handlers, a credential, a repository, an API endpoint, a scheduler, an account connection, a permission, or a bypass. It does not promise autonomous HP execution. No new action can be authorized by a public GitHub issue, external AI message, model-written prompt, or this design itself.

## Boundary architecture

1. **Transport:** an owner-controlled **PRIVATE** GitHub mailbox or equivalently audited channel, distinct from public CF-0. Public repository inputs may suggest *tasks*, never supply execution authority. The current Bridge v0.3 transport is separate from the public relay and must not be silently merged with it.
2. **Capability manifest (future):** pinned version, exact action name, expected arguments schema, allowed local resources, output schema, maximum time/bytes, idempotency, rollback, and permitted data classification. Default deny, no wildcard action names, and never an arbitrary shell or executable path.
3. **Authorization:** owner reviews an exact manifest hash and scope, approves or rejects it in the [approval bin PCA-004](../automation_200/PROMPT_CHANGE_BIN.md), and separately performs an **explicit owner-local opt-in** on the physical HP. Chat-generated or remote data cannot approve itself; revocation is local and immediately affects future admissions.
4. **Admission check:** for each future request check authorized origin, current manifest/version/hash, exact action and argument types, expiration, unique request ID, owner approval reference, local runtime enable flag, and safe output schema **before** any side effect. An unknown or unverifiable condition rejects the request.
5. **Execution:** a fixed reviewed handler only, under the signed-in user's limited privileges, with bounded resource use, fail-closed errors, and durable *started* marker. Work with third-party accounts, payments, messages, private creative files or machine configuration requires its own separate specifically authorized workflow; none are implied by this plan.
6. **Evidence and rollback:** write durable local status and strictly redacted evidence. A timed-out or interrupted operation becomes `uncertain`, never automatically replayed. Provide a locally operable stop switch, and rollback to the preserved prior working version if the candidate fails.

## Proposed request contract — non-operative illustration

These are **design fields only**, not a new accepted schema:
`request_id`, `manifest_sha256`, `approval_id`, `action`, `arguments`, `issued_utc`, `expires_utc`, `idempotency_key`, `requested_output_class`.

The **approval record** would tie one reviewed manifest hash to exact authorized actions, device-local constraints, owner identity verification process, an expiry/review date, and revocation instructions. The current public messages and private mailbox alone do **not** establish this approval.

## Minimum acceptance gates for any subsequent implementation

| Gate | Required evidence | Current result |
|---|---|---|
| Ownership/authority | Explicit scope-limited founder decision for PCA-004 plus separate physical HP opt-in | **not approved** |
| Private transport | Repository is confirmed private, fine-grained credentials separately stored using Windows-user encryption; identity checked before changes | source design exists; HP deployment **unverified** |
| No general command interpreter | Exact allowlist and strong schemas; unknown action and malicious parameters refused before execution | **not implemented** for phase two |
| No privilege increase | Existing-user limited task principal, no hidden SYSTEM/admin escalation, no remote reconfiguration | source guard exists; actual HP state **unverified** |
| Duplicate/crash protection | Durable begun/completed/uncertain states and strict nonretry on ambiguous outcomes | existing limited bridge tests, not proof for any new handlers |
| Local disable and rollback | Owner can stop scheduling, end an active task, revoke authorizations and restore original bytes/config without losing the ledger | [existing public relay stop guidance](../relay/URGENT_STOP_AND_RESUME.md); private-vNext rehearsal **not done** |
| Real execution provenance | Authenticated request/receipt matched to independently observed Windows scheduled instance, then repeated unattended trials | **unverified** |
| Security/reliability | Synthetic adversarial CI, resource caps, privacy, reviewed threat model, independent owner-controlled merge protections | **not complete** |

**No gate is auto-approved by a passing document test.** A production candidate requires the owner to review specific actions, implications, rollback, and source, then give the separate local permission. A future private worker must be able to fail safely if the owner cannot be reached.

## Threats to test before activation

- Repo or credential substitution; a public agent pretending to be the owner.
- Replayed UUID, changed request digest, stale or revoked approval, old manifest.
- Prompt injection embedded in job fields, filenames, GitHub issues or source comments.
- Arbitrary path traversal, shell flags, process command injection or access to private home folders.
- Privilege escalation, unsafely stored tokens, logging credentials or local usernames to public receipts.
- Network timeout after an action succeeds, double execution, partial crash, concurrent workers.
- Competing automated conversations modifying approval documents and claiming their changes are authority.

## Safe development and review sequence

Design -> owner review of PCA-004 proposal -> offline synthetic/negative tests -> separate private test repo + least-privilege access if owner authorizes -> owner-local test install -> direct observed receipt and rollback drill -> limited real pilot only within approved scope.

**Current verdict:** remain on the existing allowlisted public and private workers. Do not activate any phase-two handler, change `ALLOWED_ACTIONS`, create duplicate schedules, or require a new token merely because this design exists.

**Preserve:** the 200-work-order CF-200 registry and receipts, local SQLite history, previous allowed functionality and the documented historical Notepad regression, original creative materials, financial proof standards, and existing owner/creator distinctions.