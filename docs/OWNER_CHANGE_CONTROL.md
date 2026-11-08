# CF-0 owner-change controls — source tests vs enforceable protection

**Mission:** keep Caveman Focus's previously approved abilities, assets and projects
available under the designated owner's decisions. Short-term CI and revenue
metrics must not replace sustainable generational wealth or the master archive.

**Creator/developer:** David Smith. **Designated owner/beneficiary:** Kiara Lynn
Rose Smith. Neither phrase proves legal title or that a GitHub login represents
either person.

## Current actual status

- **Source checks implemented:** `automation_200/capability_guard.py` fails on
  missing baseline capabilities, changes to their expected status/source,
  untracked relay actions, false Notepad restoration, mission/priority changes,
  and stale R1 Library pointer. The Windows CI also checks a fail-closed legacy
  Notepad installer. It runs on pull requests as well as selected pushes.
- **Owner review unverified.** On November 7, 2026, GitHub reported
  `protected: false` for `main`, and the connected issuer held repository
  write access. The detailed rules endpoint was unavailable through the
  connection. A successful source push or green CI establishes technical
  access or test results. An independent owner review requires separate
  evidence. [GitHub branch metadata](https://api.github.com/repos/whoiwts110217-creator/CF-0/branches/main)
- **Notepad NOT restored:** current public relay accepts `ping`,
  `hp_status`, `sidecar_verify` only. The old Notepad installer could print
  successful installation while leaving an unusable command path. The revised
  legacy installer is an explicit **no-side-effects refusal** with exit code 2;
  Git history preserves the original. This changes its misleading behavior, not
  the already-missing Notepad relay capability.
- **Real HP status:** a public ping has a matching receipt; the independent
  Windows task origin, installed script version and optional health publisher
  are still not attested by that receipt.
- **Private provenance:** the 62-entry reconstructed project atlas in ChatGPT
  Library contains mixed projects/subprojects and lacks per-item original
  source references. It does not replace the missing original ~37-project list.

## Verified destructive-operation branch protection — November 8, 2026

The earlier November 7 note that protection was unverified remains historical. A repository-level ruleset was subsequently inspected through GitHub's REST API: [CF-0 Main — Continuity Protection](https://github.com/whoiwts110217-creator/CF-0/rules/26799223). It is `active`, explicitly includes `refs/heads/main`, and requires `deletion` and `non_fast_forward` protection. Its empty bypass list does not prove an independent review gate. The inspected rules did **not** include required pull requests, status checks, or update restrictions; ordinary automation writes are not blocked by this ruleset.

The reproducible [read-only branch audit](../automation_200/branch_rules_audit.py), with [offline fail-closed tests](../automation_200/tests/test_branch_rules_audit.py), checks this exact baseline against live GitHub ruleset data when run with network access. It does not grant administrator authority, test rejected writes, validate the person empowered to approve changes, or prove GitHub plan enforcement on a different repository. **Independent owner-review enforcement is still open**, separate from deletion/force-push protection. No HP health reporting opt-in is required for CF-0 source work or this check; the owner deferred that optional activation.

## Required owner-controlled settings (not performed by ChatGPT)

An authorized GitHub repository administrator, together with the designated
owner or her explicitly appointed representative, must confirm the **actual**
GitHub handle of the person empowered to review and approve. Do not infer
that authorization from the repository's username.

Then, in **GitHub repository Settings → Rules → Rulesets** (or the supported
branch-protection UI):

1. Create/enable a branch ruleset targeting `main`. Require a pull request
   before merging, a review from the verified authorized approver, and the
   status check `CF-0 Public Relay Windows Tests / relay` (verify the exact
   check label presented by GitHub). Require conversation resolution and block
   force pushes/deletion. Ensure the ruleset is active.
2. Restrict direct pushes and bypass privileges as far as the plan/permissions
   allow; explicitly verify whether automation accounts can bypass. If
   unavailable on the current plan, document this as an **open blocker**
   rather than pretending enforcement exists.
3. For any change to `relay/**`, `automation_200/**`, scheduled workflows,
   finance channels or owner-controlled files, require a PR impact statement:
   baseline capability → new behavior, owner decision/date/source, risk,
   previous behavior regression tests, and rollback commit.
4. If a change removes/pauses capability, do not merge without a separate,
   explicit owner-approved decision. If safety requires immediate suspension,
   disclose it, limit blast radius, and seek owner review; do not quietly
   label the capability obsolete.
5. Verify with a **real test PR** attempting to remove an approved command:
   CI should fail and repository permissions should prevent merging without
   the authorized review. Record its URL and outcome.

Until those five steps are observed, record `OWNER_ENFORCEMENT=UNVERIFIED`.

## Recommended Notepad restoration acceptance

- Separate owner-local explicit opt-in; default deny.
- Fixed `open_notepad` handler, no general shell or arbitrary command args.
- Pinned, reviewed source file hash and rollback copy before modifying HP.
- Bounded launch count (1–3), fresh signed-in interactive session.
- Unique command IDs, receipts and no reruns after ambiguous execution.
- Windows CI tests **and** a genuine on-HP visible launch/receipt proof.
- Explicitly record the current working source baseline before each deploy.

The protected capability contract itself and its guard are public-source
documents; neither is an immutable root of trust. This is a documented limit,
not an invitation to reinterpret a passing source test as consent.
