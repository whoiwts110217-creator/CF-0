# CF-0 — Source-Truth Reconstruction Protocol (TRUTH-001)

**Owner-directed scope:** November 9, 2026. **Status:** public-safe documentation protocol; not a recovered transcript archive, proof of historical completeness, new executor authority, or permission to publish private data.

**Parent:** [UCC-001](UNIVERSAL_CONTINUITY_CONTRACT.md), [master operator](../automation_200/MASTER_OPERATOR_PROMPT.md), [master continuity](../automation_200/MASTER_CONTINUITY_PROMPT.md), [Work prompt](../automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md).

## Purpose: test reality, not the assistant's recollection

The owner rejects a generic model memory summary as a replacement for the truth of conversations, archives, projects, individual words, calculations, work patterns, and outside public knowledge. Recover the actual source before paraphrasing it. Any inaccessible original remains `unavailable`, even if a later archive reconstructs its meaning.

**Mandatory precedence:** read the three current public master prompts from `main`, in their existing order, then [UCC-001](UNIVERSAL_CONTINUITY_CONTRACT.md), the [owner capability contract](../automation_200/OWNER_CAPABILITY_CONTRACT.json), relevant project sources, and this protocol. This document supplements—not overrides—user direction, tool permissions, existing capabilities, safety boundaries, or P0→P1→P2→P3 priorities.

## 1. Coverage ledger before any truth claim

For each searched surface, record `surface`, `account_or_repo`, `retrieval_method`, `source_id`, `original_or_secondary`, `read_scope`, `sha_or_version`, `observed_at`, `privacy`, `known_gaps`, and `access_failure`. Surfaces may include original ChatGPT exports, currently visible turns, authorized second-account exports, Library files, repository source and commit history, tests/CI, reports, original math notebooks, and independent public references.

Do not equate:
- a conversation title with its transcript; a summary with verbatim words; a quoted excerpt with the complete original;
- an archive's validated hash with the truth or completeness of its contents;
- a repository file with deployed HP capability; a CI test with authenticated physical-device evidence;
- a posted page or payment link with money received; a grant application with an award;
- a finite mathematical experiment with a universal theorem; a user instruction with a permanent behavioral trait.

## 2. Every word: original, derived, corrected, missing

Keep exact original conversation bytes privately when authorized and available, along with message IDs, roles, branches, timestamps, attachment references, and a content hash. Distinguish `user_verbatim`, `assistant_verbatim`, `tool_result`, `secondary_summary`, and `new_inference`. Do not place inferred words in quotation marks.

For any quoted instruction, preserve the correction chain: original wording → initial interpretation → owner correction → resulting decision → observed action/result. Preserve profanity, humor, ambiguity and rejected proposals as historic evidence; do not silently convert one-off wording into standing authorization. Mark missing messages `primary_source_missing`; never fabricate them.

## 3. Every project and archive: identities, versions, relationships

Follow [UCC-001](UNIVERSAL_CONTINUITY_CONTRACT.md): `continuity_id`, `parent_id`, `related_ids`, `owner_intent`, `source_ref`, `source_sha`, `status`, `evidence`, `authority`, `privacy`, `rollback`, `next_action`. Keep distinct projects distinct and avoid counting new subprojects as recovered historic originals.

Preserve all accessible source versions and their hashes; distinguish duplicate byte copies, independent sources saying the same thing, different versions, and logically conflicting claims. Record proposed project/source links separately from owner-accepted links. A new recovery ZIP must be verified by a fresh restore and must retain originals. Use the existing private `continuity/local_index.py` architecture where feasible; do not publish private SQLite, transcripts, manuscripts, credentials, finances, device identities or nonpublic third-party information.

## 4. Every calculation: make it executable and falsifiable

A calculation record must include `claim_id`, `source_version`, `exact_expression`, `notation_and_domains`, `assumptions`, `quantifiers`, `derivation`, `original_code`, `reproduction_command`, `test_inputs`, `observed_outputs`, `errors`, `counterexample_search`, `independent_reference`, and `open_obligation`.

Classify each mathematical result as standard established identity, verified scoped derivation, conditional lemma, numerical diagnostic, conjecture, counterexample, or unresolved. Check normalization, units, convergence, precision, error bounds, and whether a finite/local statement was incorrectly generalized. Do not change the Riemann Hypothesis, its zeta function, or any target definition to make a test pass. A theorem claim requires a closed proof, not a positive suite of examples.

## 5. Every habit: observed workflow evidence, not personality speculation

An instruction pattern or workflow preference must link to actual messages and revisions. Record the count, denominator (number of truly examined messages or conversations), time window, source coverage, exceptions, and whether the owner explicitly adopted it. Without a complete enough original corpus, label patterns `qualitative_from_available_excerpts`, not statistical behavior.

For example, literal `continue` has a specific AUTO-08 automation contract only within that context: selected signed-in account, one reusable tab, keyboard-only navigation, no coordinate clicking or extra tab per chat, send exactly `continue`, wait for response completion, checkpoint and pause/resume. A source-stage runner does not establish a successful unattended sweep. More general conversational uses of “continue” are not automatically remote-execution grants.

## 6. Public knowledge and adversarial research

Verify external claims against dated, preferably original sources. Record author, publication/update date, retrieval date, original passage/page or result identifier, citation, and contrary evidence. Distinguish accepted external science from the owner's speculative extensions and from assistant-generated analogies. Present meaningful criticisms, failure cases and historical precedents. Do not claim originality, theorem proof, empirical efficacy or commercial demand without the corresponding evidence.

## 7. Existing known coverage limit (dated, not a live census)

The November 8 *Caveman Focus Review* documented a 20-title **secondary** review (initial 15 and five added titles), not 20 full indexed transcripts. It reported the v7 private archive with 27 source blobs, 141 project-source associations, 110 events and **zero** original conversation/message rows. It separately described a 70-section August reconstruction and ten November numbered summaries; these are not extra proven distinct original conversations.

The older ~37-item original project list remains missing. The 17 named rows, separate inconsistent 18-entry reference, and 62 reconstructed projects/workstreams are separate records. Full originals and source-based parent links are not demonstrated by the counts. The November 9 public [state](PUBLIC_CONTINUITY_STATE.json) reports **87/200** verified CF-200 work orders; always fetch [live registry source](../automation_200/registry.json) before quoting an updated count. The count is not 87 solved scientific projects, 87 active automations or 87 verified payments.

No complete original chat export, original ~37 list, RH proof, independent weeklong account autonomy, current live Notepad launch, or verified outside revenue is established by this protocol.

## 7A. Supplemental browser capture recovered — private v8 (November 9, 2026)

The owner-controlled Library now includes a **separate-account, browser-captured ZIP**, independently read and SHA-256 validated in a private assistant working environment. This later recovery supplements—not contradicts—the **dated November 8 v7 snapshot with zero indexed conversations**. The browser archive contains **95 named conversation records and 757 captured user/assistant message records**, with a self-declared scope of 78 visible conversation windows, 15 checked selected branches, and two partially rendered branches. The official full-account export and alternative branches are **not** established. These records must not be called 95 complete conversations.

A **new private v8 snapshot**, created as a separate artifact rather than replacing v7, indexes this browser capture: it preserves 62 reconstructed project records, 141 prior project-source links and 110 prior hash-linked events, and records two new bounded source/index events. A fresh offline restore and checks of original hashes, SQLite integrity, foreign keys and event hashes passed. This backup is **in the assistant's working artifact space, not verified installed on the HP or uploaded to the owner's persistent Library**. A verified source archive may still contain incomplete or mutually conflicting rendered views.

**Outstanding ambiguities:** 44 captured message identifiers recur in different conversations; 12 have differing text hashes. One conversation has differing titles in its index and structured record. Preserve every occurrence and both title labels; do not deduplicate or silently choose a canonical version. The supplemental private crosswalk identifies 21 selected owner statements in eight threads with message IDs and exact captured wording; those proposed project links are not owner-approved atlas edges.

**Public boundary:** publish only these aggregate coverage and evidence limits. Never commit the original ZIP, readable transcripts, full private SQLite, private message index, hashed per-message comparison, or sensitive conversation content to CF-0. This update changes no account/HP authority, existing priority, cash claim, CF-200 registry, or accepted original-project count.

## 7B. Read-only v8.1 reconciliation — November 9, 2026

**Continuity:** UCC-001 → TRUTH-001. A **private, read-only** offline audit of the other-account browser-capture ZIP against the private v8 continuity ZIP and the older 20-title secondary review produced the following bounded findings. Exact original browser ZIP bytes were preserved inside the private backup. The browser ZIP passed its **193** SHA-256 listed-member checks; the backup passed **29** declared-member checks; SQLite integrity/foreign keys and **112** historical event-chain digests passed. **All 757 captured message IDs, roles and text bodies matched exactly** between browser source and SQLite. The separate account supplied **381 user** and **376 assistant** rendered messages.

**Critical new metadata distinction:** **659** indexed message timestamp values agreed with the captured source turn timestamps. For **98 assistant messages**, the SQLite `sent_at` is NULL even though the source **turn** has a timestamp. A turn time must not be silently promoted into an individual assistant-message send time. The source ZIP remains intact, so these source turn timestamps are recoverable without inventing message metadata.

**Identity reconciliation:** Of **20** historical conversation titles in a **different account's secondary review**, **zero exact titles matched** this other-account capture. This does not prove any original conversations missing from either account, and it authorizes **zero** cross-account project or conversation merges. The audit preserved **44** reused message-ID groups across conversation contexts, **12** with distinct text-body hashes; neither the repeats nor differences establish which captured wording is canon. **21** previously selected exact owner statements were reverified. A single index-vs-structured title mismatch also remains.

**Verification:** Three offline regression tests passed: original index/body comparison, altered archive member rejection and altered owner quotation rejection. All raw source files, conversation IDs, exact user words, conflict tables and test reports remain **private**; none were pushed to the public repository. This audit did not produce a new v9 backup, alter v8, verify CF-200 work orders, grant machine/account rights, verify income or finish the original ~37-project recovery.

**Next:** obtain official original account-separated exports when accessible. Match using source account and actual conversation/message IDs, preserving branch/attachment and timestamp uncertainty. **Rollback:** revert this documentation paragraph through reviewed Git history; no runtime functionality changed.

## 8. Required output and acceptance

Every audit run reports:

```text
TRUTH_RUN
main_commit=<actual current commit>
prompts=<paths, exact blob SHAs, full/partial read status>
source_scope=<surface and exact original/secondary coverage>
verbatim_messages=<actually indexed count, or unknown>
secondary_conversation_titles=<count and source>
projects_reconciled=<IDs and actual primary-source proofs, or none>
calculations_reproduced=<claim IDs, conditions, tests, exact results>
habits_measured=<sample size, window, exceptions, or qualitative only>
external_claims_checked=<primary sources, dates, disagreements>
contradictions=<open/resolved with source and owner authority>
privacy=<what stayed private, any approved public derivative>
source_changes=<paths, before/after commits, test/readback>
next_missing_source=<smallest real missing input>
```

An audit is **complete only for its declared, checked source scope**. Never claim “every word” across accounts that were not actually enumerated and indexed. This protocol does not authorize new public posts, account controls, HP actions, compensation, task promotions or private publication.

**Rollback:** preserve Git history; this protocol can be reverted without changing existing runtime, ledgers or protected capabilities. **Next action:** recover and index full original conversation exports privately, with account-separated provenance, then reconcile each exact message against the secondary crosswalk and the 62-entry reconstructed atlas.
