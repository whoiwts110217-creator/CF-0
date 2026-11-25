# Spider puzzle → assembled program

The owner requested that the 500-piece puzzle become a real Spider program on
November 15, 2026. This authorizes a **separate assembled source candidate** for
this task, superseding the earlier instruction to keep every piece disassembled.
The original atlas, visual arrangements, private packages and installed HP remain
unchanged.

The first 500 tiles contain nested functions/classes and only 32 complete files;
they stop partway through `spider/operator.py`. Joining their text would duplicate
definitions and leave out dependencies. The builder instead restores **all 94
complete original files** from the same public atlas, including 42 test files.

## Download and start

The [full puzzle page](https://whoiwts110217-creator.github.io/CF-0/spider-puzzle/full.html)
links to `CF0-Spider-Assembled-v1.zip` once this change is deployed. The existing
Pages workflow builds the ZIP from the checked source; no separately maintained
binary is committed. Pull-request checks also attach the built ZIP as an Actions
artifact.

With a checkout and Python 3.10 or newer, build the identical package yourself:

```sh
python spider-puzzle/assemble.py --output CF0-Spider-Assembled-v1.zip
```

Extract it into a **new folder**. On Windows, open
`START_ASSEMBLED_SPIDER.cmd`. It checks integrity before launching the actual
desktop with automatic Chrome startup off. It does not install, make shortcuts,
resume scheduled workers or replace a previous Spider. See the package's own
instructions for the portable check command and desktop launch.
The 94 original files live in `runtime/`; the new launcher stays outside that
folder so the original strict preflight and upgrade manifests remain valid.

## Evidence and limits

- The source atlas records ZIP fingerprint
  `438c442a781b028b1ef8fc336585e540e14dfb5e3828a8d2e8ab35857e2dec24`.
  This is historical provenance, not a claim that the rebuilt ZIP is byte-identical
  to that original archive.
- Independently checked: **1,289/1,289** excerpt hashes, **93/93** original
  full-file manifest hashes and **80** Python files compiling. All **298** bundled
  tests passed in Linux with local test servers; these are source/synthetic tests.
- The first clean-package CI run caught ten failures because new launcher files
  shared the original source directory. The corrected `runtime/` boundary keeps
  the original strict inventory unchanged; no original test or manifest was relaxed.
- The added launcher exercises the real source ledger and STOP/resume components.
  It rejects a missing real Tk display instead of allowing the old GUI's silent
  stub fallback to count as a launch.
- Known [Hands defects](../../docs/spider-puzzle/HANDS_REVIEW.md) are preserved and
  disclosed, not silently labeled repaired. A separate repair proposal has its own
  mock tests and is not integrated into this exact-source restoration.
- Cursor following, exact-window input binding, ordinary signed-in Chrome and
  physical Windows HP behavior still require their own acceptance. The assembled
  program is **source-tested**, not a completed autonomous computer operator.

## Continuity and rollback

`continuity_id=CF-SPIDER-001`; related CF-MESH-001, UCC-001, the standalone
[Spider Desktop](../spider-desktop/README.md), the
[source atlas](../../docs/spider-puzzle/README.md) and existing Sphere/Link Vault.
Creator/developer: David Smith. Intended owner/beneficiary: Kiara Lynn Rose Smith;
no legal transfer claim.

Source inspected: public `main` commit
`13e00e779280904476bc1573fa227dc481f0e350`; atlas Git blob
`2dfb49780673663efc27b4aae646325dcbe0d09b`. Three required prompt blobs:
Operator `5dad8c17b04a4eb744e5a1474b2ecfb9ddd0abe0`, Continuity
`77900acb1c3eb75f8dfd3cef245503d052971479`, Work
`d090f82eaf89d9cd339e7eef248750ebef965e88`. Future sessions must fetch the
[three current prompts](../../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md)
again. Private original archives were unavailable and were not reconstructed or
published. No CF-200 status, relay command, schedule or machine permission changes.

Rollback: revert this bounded source change; remove only the new extracted folder
if it is no longer needed, preserving any user-created runtime data separately.
Next: test the clean package on Windows, integrate and retest isolated Hands
repairs in a separately versioned candidate, then run an owner-supervised HP
launch/STOP drill before making live-operation claims.
