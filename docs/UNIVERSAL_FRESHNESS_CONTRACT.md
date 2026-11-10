# CF-FRESH-001 — Universal freshness and latest-source contract

**Owner directive, November 10, 2026:** Apply the Jungle Map's **old → current** logic to **everything** in Caveman Focus: projects, project subbranches, 200 tasks, automations, source code, stories, experiments, mathematical claims, business/funding work, decisions, habits, archived records, and future artifacts.

**Parent:** [UCC-001](UNIVERSAL_CONTINUITY_CONTRACT.md) / CF-CORE. **Consumers:** [Jungle Map](OWNER_JUNGLE_MAP.md), [current source gateway](CURRENT_SOURCE_GATEWAY.md), [public project index](PROJECTS.md), [three-chat mesh](mesh/START_HERE.md), [Mission Control](https://whoiwts110217-creator.github.io/CF-0/mission-control/), and all future source-linked CF-0 work. This is a public, read-only navigation policy. It grants no login, local HP, new scheduler, publication, financial, or agent authority.

## The rule: an old fact must know where to find its successor

For **every** artifact, preserve these fields in its own metadata, the existing UCC-001 handoff, or the central public-safe index:

| Field | Meaning |
|---|---|
| Stable identity / family | Existing project/task/feature identity; do not invent another project merely to give it a freshness record |
| Evidence/source type | Primary original, secondary reconstruction, public code, test, owner observation, provider record, external money receipt, or unverified hypothesis |
| Snapshot origin / checked time | Date of the **actual inspection** plus source commit/blob or private source version when authorized. Never infer a source check from the current clock |
| Freshness status | `same_source_bytes_in_this_checkout`, `stale_source_snapshot`, `snapshot_age_unknown`, `unverifiable_snapshot_id`, or `private_origin_not_visible` as applicable; runtime `running/paused` is a **separate** provider question |
| Latest authoritative route | A moving **`main` link** to the actual public source and/or a provider-authenticated current view. Do not point only to a dated previous SHA. |
| Next action / owner gate | Current useful step; owner needed only when permission, private source, payment, login, or device control is necessary |
| Provenance / rollback | Preserve historical source and explanations when a newer version supersedes it. Do not silently overwrite original evidence |

An artifact can be the **newest version** of a historical narrative without its historical facts becoming today's operational state. A current source file is not proof its content describes a running system. A job's source-level schedule is not evidence it actually ran. A grant application is not a grant award; a donation page is not a confirmed payment; a simulation is not a physical device receipt. Privacy is independent of freshness.

## What is actually implemented now

- [Universal catalog](FRESHNESS_CATALOG.json): 13 existing topic-graph identities and additional public-safe lane/family anchors. The catalog stores **routes**, never duplicates task status or payment totals.
- [Generic read-only freshness resolver](../continuity/public_freshness.py): for **any present public repository file** (not just the 29 catalog entries), produce its moving `main` URL and compare an optional recorded Git blob to the current checkout. Unknown recorded blobs stay explicitly **unknown**. The optional `git ls-files` inventory lets an operator enumerate *all* public tracked paths without opening their content.
- [Current Source Gateway](CURRENT_SOURCE_GATEWAY.md): one bookmarked destination that shows the newest public routes across P0–P3 and the distinction between current GitHub, private storage, and external provider evidence.
- The **existing** Mission Control already fetches the registry from GitHub and labels its source commit / fallback state. It is the live source-attempt surface; this policy does **not** duplicate or replace it.
- [Windows/source tests](../continuity/tests/test_public_freshness.py) verify 13 known topic graph routes, cross-project family routing, private/unknown status, invalid paths, stale byte detection, and new public-file fallback. The existing full Windows CI runs these tests; no new scheduled task is added.

**Example (local checkout, source-only):**

```sh
python -m continuity.public_freshness
python -m continuity.public_freshness --path docs/OWNER_JUNGLE_MAP.md --snapshot-blob c48adffd6da0f429dc05a5a108a82001b36a9609
```

The checker reports *matching this local checkout*, **not** proof that the checkout is currently GitHub main or that an account/device/provider actually ran. Always open its moving `main` source link to refresh.

## Scope: literally every class, without pretending to read every private byte

| Class | Where to discover newer evidence | Historical/unknown fallback |
|---|---|---|
| Public tasks, code, tests and policies | Current `main` [registry](../automation_200/registry.json), [public status](PUBLIC_CONTINUITY_STATE.json), [GitHub tree](https://github.com/whoiwts110217-creator/CF-0/tree/main) and linked CI | Dated snapshots retain SHA, link to current source; unknown if not checked |
| Missions, automations, agents and UI | [Mission Control](https://whoiwts110217-creator.github.io/CF-0/mission-control/), original run/receipt records and **account-native** provider state when connected | `source_only` / `provider_unverified`; do not turn on HP schedules or invent an active switch |
| Grants, customers, donations and revenue | Public aggregate [status](PUBLIC_CONTINUITY_STATE.json), approved offers, real owner/provider receipts when available | `not_independently_verified` absent an actual payment/award/delivery |
| Private original books, chat exports, contacts, calculations and unpublished artwork | Existing **private** master/Library or authorized private source, with a public-safe summary pointer | `private_origin_not_visible` / `original_not_recovered`; **never post original URLs or bytes to public GitHub** |
| Scientific ideas, mathematics and experiments | Latest source definitions, proofs/obligations, test logs, [research overview](RESEARCH.md) | Finite data remains experimental; no automatic upgrade to theorem/proof |
| New future ideas, UI screens, jokes, models, games and projects | Existing UCC-001 ID, nearest public topic graph node, checked source/version, current route | `unmapped_or_unreviewed` until incorporated; never silently omit or merge identities |

**'All' means the rule and fallback apply universally. It does NOT mean all external accounts, 638+ public files, unpublished works, and missing original conversations were live-audited in one session.** The catalog provides 29 known routes today; generic public-file routing covers new files without requiring an extra table row. Deeper source-specific verification is incremental and must be reported honestly.

## Mandatory authoring / handoff behavior from here forward

When opening, editing or presenting **any** Caveman Focus source:

1. Recover the existing identity and canonical source rather than creating a second registry.
2. If reading a dated report, compare its recorded blob/source with current `main` and mark **CURRENT SOURCE / STALE SNAPSHOT / UNKNOWN AGE**. A date label alone is not a current check.
3. Show or carry a **Latest/current source** link, even in stories, original games and science; for private artifacts provide only a private-safe pointer, never their raw private URL.
4. Keep original history, proofs, drafts and owner decisions intact. Mark missing originals and assumptions openly.
5. Update dependent views/handoffs when actual source status changes; use existing CF-200 executor and GitHub CI, **not** a new scheduler.
6. If source/provider is unreachable, label the result **unknown** and link to the last verified record—never manufacture an update.

**Next engineering acceptance:** integrate this read-only freshness route more deeply into the existing Mission Control owner checklist for all workstreams. This contract and source tests alone are not proof of an always-on, authenticated cross-account monitor. Existing private contact registry stays private; do not duplicate or export it. **Rollback:** revert only this policy, catalog, resolver/tests and navigation pointers after reviewing impact; preserve original files and task/event ledgers.
