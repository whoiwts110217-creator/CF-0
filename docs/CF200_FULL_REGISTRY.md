# CF-200 — All 200 public work orders

**Canonical source:** [the complete live `registry.json`](../automation_200/registry.json) · [raw JSON for machines](https://raw.githubusercontent.com/whoiwts110217-creator/CF-0/main/automation_200/registry.json)

This is a *public reading guide*, not a second registry. The 200 IDs, descriptions, priority streams, dependencies, statuses and task-specific evidence are held in the canonical `automation_200/registry.json` on `main`. The number marked `verified` changes as independently checked work is accepted; consult the live file rather than treating an old screenshot, checkpoint or copied count as current.

## Ways to inspect the full list

- **Browse/filter:** [CF-0 Mission Control](https://whoiwts110217-creator.github.io/CF-0/mission-control/) reads a pinned public registry commit and includes a **Show restricted** control. Hidden rows remain in the source; the view's commit label indicates whether it is showing live data or its last bundled fallback.
- **Read all 200 entries:** [full registry JSON](../automation_200/registry.json). Each work order has a stable `CF-001` through `CF-200` ID, a title, workstream, dependencies, status, evidence and source-level authority annotation.
- **Verify progress:** [machine-readable continuity status](PUBLIC_CONTINUITY_STATE.json), [numbered checkpoints](../automation_200/checkpoints/) and the [human-readable mission board](../automation_200/MASTER_MISSION_BOARD.md). The registry itself is authoritative. A checkpoint is not proof of physical HP operation.
- **Understand present limits:** [owner capability contract](../automation_200/OWNER_CAPABILITY_CONTRACT.json), [decision-engine evidence boundaries](../automation_200/DECISION_ENGINE.md) and [public task/issues dashboard](TASKS_AND_ISSUES.md).

**Important distinctions:** `verified` means the specific work order has accepted evidence, often *source or CI tests*, **not** that the whole system is deployed, earning money, running unattended, or has ownership/HP permissions. `planned` includes dependency-held, device-local, and ordinary source-work candidates. Source-work selection never grants shell, browser, Notepad or payment authority. The public HP relay remains limited to `ping`, `hp_status`, and configured read-only `sidecar_verify`.

**Privacy:** This index deliberately does not embed private conversations, manuscripts, bank records, credential material or HP-local paths. Public metadata does not establish legal assignment of ownership. Preserve distinct creative project histories; the unrecovered approximately 37-project original inventory is not replaced by the CF-200 list or the separate 62-entry reconstructed atlas.

**Publication verification:** [offline registry and Mission Control coverage tests](../automation_200/tests/test_public_registry_cf120.py) check all canonical IDs, dependencies, continuity fingerprint, and the dashboard's complete unfiltered source snapshot. They do not claim a hosted page is currently reachable without an independent external fetch.
