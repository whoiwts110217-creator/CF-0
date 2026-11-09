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

Missing, stale or fresh public HP reports must not block independent tests, code repairs or bounded finance/creative drafting. Failed tasks are not automatically retried forever, and no source patch counts as a verified real-HP work order.

## CF-119 — explicit HP authority proof boundary (source-level)

The [HP authority gate](hp_authority_gate.py) now supplies the cloud selector's hardware/owner-local holds and an explicit read-only `hp_proof_gate` result. It does **not** issue credentials or grant access. Even an owner-supplied public heartbeat, correctly matched public receipt, overlapping Windows scheduler timestamp, and unverified statement of approval cannot prove that the observed device is the authorized HP or that an HP action was authorized. All diagnostic inputs leave `hp_execution_authorized=false`.

The [decision engine](decision_engine.py) refuses physical-HP work, every HP-install stream entry, the enumerated owner-local tasks, and malformed physical-HP flags; selected ordinary work is always `propose_source_work_only`. Owner preference can reorder eligible source proposals but **never** turn a proposal into an HP command. Real owner-local opt-in, device/scheduler provenance, and capability rollback remain separate requirements. [Negative regression tests](tests/test_hp_authority_gate_cf119.py) cover forged confidence claims, malformed flags, and owner overrides without accessing a machine.

The existing [CF-118 retry journal](retry_evidence.py) remains the only local durable failure log; [its adapter](attempt_history_cf118.py) can generate a bounded *proposal* from reviewed local journal evidence. This does not silently activate the journal in a scheduled executor, establish independent failure provenance, or authorize a retry.

## Watchdog packet readback

For the existing Work executor, use the latest completed successful scheduled [Channel Evidence Watchdog run](https://github.com/whoiwts110217-creator/CF-0/actions/workflows/cf0-channel-watchdog.yml) on `main`. Read the full GitHub REST run and matching `audit` job metadata from `actions/runs/<run-id>` and `actions/jobs/<job-id>`. Obtain the decoded log for that same job through the existing GitHub connection. Use the following command in a checkout with those inputs.

```sh
python -m automation_200.watchdog_readback --run-metadata run.json --job-metadata job.json --job-log job.log
```

The readback records the run, attempt, job, source commit, and SHA-256 of the exact compact JSON payload after `CF0_WORK_HANDOFF=`. In the same saved Work result, cite that readback and separately record the actual selected or held task and its outcome. Check the current registry and owner gates before making a decision. Missing or ambiguous evidence leaves consumption unverified. A manual readback demonstrates retrieval. A scheduled handoff needs a matching result from an actual scheduled Work run. HP origin and execution authority require their own evidence.

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
