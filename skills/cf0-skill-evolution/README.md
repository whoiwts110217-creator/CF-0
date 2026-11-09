# CF0 Skill Evolution v0.1 — usable now, offline

**Identity:** `CF0-SKILL-EVOL-001` · Parent `CF-CORE` · Related `UCC-001`, `CF-SKILL-FOUNDRY-001`, `AUTO-08`, `cf0-hp-control`.

**What it is:** a skill instruction package and deterministic source/evidence gate that prevents false skill upgrades. **What it is not:** model retraining, an installed ChatGPT plugin, native iPhone app, live account control, or verified agent execution.

## iPhone instructions — no computer required just to read/build

1. Open the existing [iPhone Skill Foundry](https://whoiwts110217-creator.github.io/CF-0/skill-foundry/) in Safari. For home-screen access, choose **Share → Add to Home Screen**. The web app's accessibility on a physical iPhone is separately unverified; it is not an App Store app.
2. Use the app to create or export skill drafts; it generates `SKILL.md`, `EVALS.json` and a synthesis prompt. This ZIP is readable in iPhone Files, but iOS Safari does **not** execute this package's Python gate.
3. Use `SKILL.md` in the exported folder as the reusable skill/evaluation method. Keep source/version and evidence before claiming skill improvement.
4. If an approved PC/CI/Python environment is available, run the gate there. The optional Python runtime uses only the standard library and no external network services.

## Offline Python example (Windows/macOS/Linux)

Create separate actual `before/SKILL.md`, `after/SKILL.md`, and a real `evidence.json` with observed full-test outputs and independent review votes. An entirely synthetic example is in `evidence/example.json` and **does not establish an agent performance gain**.

```shell
python scripts/darwin_gate.py before/SKILL.md after/SKILL.md evidence.json --out gate-report.json
python -m unittest discover -s tests -v
```

Exit status 0 means **eligible for owner review**, not approved or deployed. Exit status 2 means rejected/needs evidence; exit status 3 means invalid files or input. A report path is create-only to avoid accidental history overwrite.

## Integrity and evidence standard

- Before and after skill files must be genuinely different and independently versioned.
- `test_runs`: at least three distinct IDs spanning normal, ambiguous and failure; `mode=full_test`; both `*_pass` booleans and `*_output_ref` references to actual results.
- `judges`: odd number ≥3 unique real reviewers, with both candidate-first and baseline-first order represented; explicit majority of `better` votes. Synthetic identities are not real independent reviewers.
- Four hard gates must be `true`: `owner_authority_unchanged`, `privacy_preserved`, `capabilities_preserved`, `continuity_complete`. A single explicit `false` forces rejection.
- Positive verdict: `owner_review_required`. The script does **not** validate underlying evidence authenticity, independent identity, privacy of file contents, or signed-in execution. That remains an operator's responsibility.

**Background:** adapted from Darwin Skill v2.1 by alchaincyf (花叔) under an MIT-licensed publicly available source (https://github.com/alchaincyf/darwin-skill). Uses original implementation/text; reference is not an installation or endorsement. The original authors retain their attribution.

**Source preflight reviewed 2026-11-09:** CF-0 operator blob `22ae58c3bc1a7513ef45e4c8267ea011a56bb357`; continuity blob `6d0cf4ac809172d0525de288d87a340d1f01537c`; Work blob `150c6629ba1496c2b05d9f4afb31929ad142357e`; UCC-001 blob `8a19cabe65c3d35e99cdf4a256154771da33d03c`. Re-fetch current main next time.

**Roll back:** Remove this isolated, non-authoritative addition. No existing CF-0 files, account state, public relay permissions or registry counts need changing.