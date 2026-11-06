# CF-200 — Founder-governed decision proposals

**Owner:** Kiara Lynn Rose Smith's Caveman Focus  
**Implementation:** [decision_engine.py](decision_engine.py)  
**Authoritative task records:** [registry.json](registry.json) and [events.jsonl](events.jsonl)

The public cloud can now produce a testable **proposal** for which eligible CF-200 tasks to advance, under the founder's P0 automation → P1 priority governance → P2 legitimate income → P3 other projects order. This is **not** an autonomous task executor or a grant of new HP permissions. No registry status, evidence, checkpoint, HP settings, GitHub files or payment records are modified by the proposal.

## How decisions work

1. Read the existing registry. A task whose dependencies are unverified is deferred.
2. Defer every task marked `physical_hp_required` and **every HP installation task**, even those previously tagged `physical_hp_required=false`: a public heartbeat never proves installation, a scheduler launch, device identity or owner approval.
3. Defer explicitly blocked tasks. For an operator-provided record of previous failures, apply a 5-minute delay after the first failure, 10 minutes after the second, and owner-review ceiling after the third. Counts and timestamps must be valid task-specific integers.
4. Use the existing [priority selector](priority_selector.py) for eligible work. An explicit owner priority may move an eligible task earlier but cannot bypass a dependency, failed-retry ceiling or HP gate.
5. Output at most four ready proposals, per-task reasoning and counts of held tasks. No selected task is auto-executed. A scheduled executor must inspect the source and perform only work separately authorized by its operating rules.

The latest missing HP report should not block independent tests, code repairs or bounded finance/creative drafting. Failed tasks are not automatically retried forever, and no source patch counts as a verified real-HP work order.

## Reproducible commands

From the CF-0 repository root:

```powershell
python -m automation_200.decision_engine --health-state not_published --limit 4
python -m automation_200.decision_engine --live --limit 4
python -m automation_200.decision_engine --owner-preference CF-183 --blocked CF-027
python -m automation_200.decision_engine --attempts-json '{"CF-069":{"failures":2,"failed_at":1793978000}}'
python -m unittest discover -s automation_200/tests -p test_decision_engine.py -v
```

`--live` fetches only the fixed public HP health file via the existing read-only monitor; no communication with the HP occurs. If GitHub is unavailable, the returned state is `unavailable` and the decision engine retains the hardware gate.

**Important:** Failure records supplied with `--attempts-json` are read-only per-invocation inputs, not a persistence mechanism. Until a separately reviewed append-only attempt ledger is connected, a scheduled invocation with no attempt records has no knowledge of previous task failures. Do not claim durable autonomous retries yet.

## Verification and limitations

Offline tests cover real-registry eligibility, immutable input, founder overrides, failed-dependency exclusion, cooldown and retry limits, absent/fresh HP health, and conflicting owner priorities. The existing five-minute GitHub watchdog runs the tests and publishes its **read-only proposal in the job log**. Passing that workflow validates the cloud plan, not the HP installation.

The next engineering step is to persist bounded attempt outcomes with an append-only, reviewable evidence trail, then have the scheduled CF-200 operator actually complete source-level work, validate it, and record the outcome. No public web content, workflow output or task description can broaden user-approved authority.
