#!/usr/bin/env python3
"""EXP-SN004-04: blinded missing-intervention-pathway diagnostic (synthetic surrogate).

Important provenance boundary:
The recovered SDU atlas is a state-assignment atlas, and EXP-SN004-03 is a toy
function-class diagnostic. Neither defines an intervention-pathway semantics or
contains an executable missing-intervention scaffold. This experiment therefore
operationalizes a new, explicitly synthetic surrogate; it is NOT a reproduction
of an undocumented prior missing-intervention condition.

Protocol:
- seed 20261020; 10,000 trials sampled without replacement from atlas IDs in the
  held-out final 30% of the contiguous atlas index range.
- 2,000 restored, 4,000 one-pathway missing, 4,000 multiply missing (2 or 3).
- seven pathway handles correspond to the seven atlas dimensions. Each handle's
  presence record includes its path ID and a deterministic state-bound response.
- learner receives no defect/group label; it applies generic set-difference and
  response-validation rules. Because path IDs are visible, this is a transparent
  diagnostic benchmark, not a hard latent-cause inference task.
- commit all decisions and proposed repairs before writing outcome ledger.
- compare with a newly defined transparent reference scaffold and chance baselines.
- never alter baseline files; record their hashes before and after.
"""
import csv, hashlib, json, platform, random, sys, math
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path('/mnt/data')
OUT = ROOT / 'exp_sn004_04_run_20261020'
SEED = 20261020
TRIALS = 10_000
RESTORED_N = 2_000
SINGLE_N = 4_000
MULTI_N = 4_000
THEORIES = [
    'T1_ShadowUniverse', 'T2_FutureFingerprints', 'T3_ObserverHiddenVar',
    'T4_NoFinalModel', 'T5_MeaningOfNumber', 'T6_BranchingPoint', 'T7_SingleDot'
]
ALL_PATHS = list(range(7))
ATLAS_TOTAL = 7**7
HOLDOUT_START = math.floor(ATLAS_TOTAL * 0.70)
BASELINES = [
    ROOT/'sdu_atlas_823543_csv_batches.zip', ROOT/'sdu_atlas_manifest.json', ROOT/'sdu_generator.py',
    ROOT/'exp_sn004_03_run_20261020'/'commitments.jsonl',
    ROOT/'exp_sn004_03_run_20261020'/'append_only_results_ledger.jsonl',
    ROOT/'exp_sn004_03_run_20261020'/'results.csv',
    ROOT/'exp_sn004_03_run_20261020'/'summary.json'
]

def canon(o): return json.dumps(o, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
def sha(b): return hashlib.sha256(b).hexdigest()
def file_hash(p): return sha(p.read_bytes())
def config_id(i): return f'SDU-CFG-{i:07d}'
def decode_config(i):
    vals = [0]*7
    for j in range(6,-1,-1):
        vals[j] = i % 7
        i //= 7
    return vals

def response_token(trial_id, path_id, state, nonce):
    return sha(f'{trial_id}|path={path_id}|state={state}|nonce={nonce}'.encode())

def learner_decision(config_states, observed_handles, nonce):
    # Generic schema validation; deliberately no group/defect label is passed in.
    expected = set(ALL_PATHS)
    seen = {int(h['path_id']) for h in observed_handles}
    missing = sorted(expected - seen)
    unexpected = sorted(seen - expected)
    bad_responses = []
    for h in observed_handles:
        p = int(h['path_id'])
        if p not in expected or h['response'] != response_token(h['trial_id'], p, config_states[p], nonce):
            bad_responses.append(p)
    detected = bool(missing or unexpected or bad_responses)
    # Discovery is the inferred missing pathway set. Repair proposes only the missing
    # handles; the evaluator later validates them with an independent nonce.
    return {
        'detection': 'MISSING_OR_INVALID_PATHWAY' if detected else 'ALL_PATHWAYS_PRESENT',
        'discovered_missing_paths': missing,
        'unexpected_paths': unexpected,
        'invalid_response_paths': sorted(set(bad_responses)),
        'repair_proposal_paths': missing,
        'action': 'propose_repair' if detected else 'no_repair'
    }

def reference_scaffold(config_states, observed_handles, nonce):
    # Explicitly defined reference comparator, not claimed to be a recovered original.
    return learner_decision(config_states, observed_handles, nonce)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # Verify and snapshot baseline hashes before any experiment artifacts are written.
    before = {str(p.relative_to(ROOT)): {'sha256': file_hash(p), 'size_bytes': p.stat().st_size} for p in BASELINES}
    manifest = json.loads((ROOT/'sdu_atlas_manifest.json').read_text())
    assert manifest['verification']['generated_data_rows'] == ATLAS_TOTAL
    assert manifest['verification']['batch_file_count'] == 83
    assert manifest['verification']['all_checks_passed'] is True
    assert len(before) == len(BASELINES)

    rng = random.Random(SEED)
    truth_rng = random.Random(SEED ^ 0x534E3034)
    holdout_indices = rng.sample(range(HOLDOUT_START, ATLAS_TOTAL), TRIALS)
    trial_specs = []
    kinds = ['restored']*RESTORED_N + ['single_missing']*SINGLE_N + ['multiple_missing']*MULTI_N
    rng.shuffle(kinds)
    for idx, kind in zip(holdout_indices, kinds):
        cid = config_id(idx)
        states = decode_config(idx)
        # All trial conditions are privately assigned; learner never receives this label.
        if kind == 'restored':
            missing = []
        elif kind == 'single_missing':
            missing = [truth_rng.choice(ALL_PATHS)]
        else:
            k = truth_rng.choice([2,3])
            missing = sorted(truth_rng.sample(ALL_PATHS, k))
        nonce = sha(f'{SEED}|{cid}|{truth_rng.getrandbits(128)}'.encode())[:24]
        trial_id = f'EXP-SN004-04-{len(trial_specs)+1:05d}'
        observed = []
        for p in ALL_PATHS:
            if p not in missing:
                observed.append({'trial_id': trial_id, 'path_id': p,
                                 'response': response_token(trial_id,p,states[p],nonce)})
        # Learner input includes configuration states and observed handle records only.
        # Hidden truth kind and missing path set are kept outside the precommit payload.
        learner = learner_decision(states, observed, nonce)
        scaffold = reference_scaffold(states, observed, nonce)
        # Independent repair check uses a different nonce; repaired records are synthesized
        # from the declared pathway/state contract and evaluated only after commitment.
        repair_nonce = sha(f'{SEED}|independent-repair|{trial_id}'.encode())[:24]
        pre = {
            'trial_id': trial_id, 'atlas_config_id': cid, 'atlas_index': idx,
            'config_states': states, 'nonce': nonce, 'observed_handles': observed,
            'learner_decision': learner, 'reference_scaffold_decision': scaffold,
            'proposed_repair_paths': learner['repair_proposal_paths'],
            'independent_repair_nonce': repair_nonce,
            'input_contract': 'no_condition_label_or_hidden_missing_path_set'
        }
        trial_specs.append({'precommit': pre, 'hidden': {'condition':kind,'missing_paths':missing}})

    # Immutable-by-convention outputs are new files, separate from baseline outputs.
    commitments_path = OUT/'commitments.jsonl'
    ledger_path = OUT/'append_only_results_ledger.jsonl'
    if commitments_path.exists() or ledger_path.exists():
        raise RuntimeError('Refusing to overwrite an existing EXP-SN004-04 run artifact')
    commitment_rows = []
    with commitments_path.open('x', encoding='utf-8') as f:
        for spec in trial_specs:
            pre = spec['precommit']; digest = sha(canon(pre))
            row = {'precommit':pre, 'sha256':digest}
            commitment_rows.append(row)
            f.write(json.dumps(row, sort_keys=True, separators=(',',':'))+'\n')

    counts = Counter(); by_condition = defaultdict(Counter); class_counts = Counter()
    with ledger_path.open('x', encoding='utf-8') as f:
        for spec, crow in zip(trial_specs, commitment_rows):
            pre, hidden = spec['precommit'], spec['hidden']
            actual_missing = hidden['missing_paths']
            found = pre['learner_decision']['discovered_missing_paths']
            scaf_found = pre['reference_scaffold_decision']['discovered_missing_paths']
            detected_true = bool(actual_missing)
            detected_pred = pre['learner_decision']['detection'] != 'ALL_PATHWAYS_PRESENT'
            detection_correct = detected_pred == detected_true
            discovery_correct = found == actual_missing
            scaffold_discovery_correct = scaf_found == actual_missing
            # Simulate the repair action; validate all expected path/state signatures with
            # independent nonce. It only tests the declared synthetic contract.
            repaired_paths = sorted(set(h['path_id'] for h in pre['observed_handles']) | set(pre['proposed_repair_paths']))
            repaired_records = [{'path_id':p, 'response':response_token(pre['trial_id'],p,pre['config_states'][p],pre['independent_repair_nonce'])} for p in repaired_paths]
            repair_ok = (repaired_paths == ALL_PATHS and len(repaired_records)==7 and
                         all(r['response']==response_token(pre['trial_id'],r['path_id'],pre['config_states'][r['path_id']],pre['independent_repair_nonce']) for r in repaired_records))
            # Chance baseline: correct restored/missing status under the benchmark's 20/80 mix;
            # uniform pathway-set guess chance is exact combinatorial probability.
            k = len(actual_missing)
            chance_discovery = 1.0 if k == 0 else (1/7 if k == 1 else 1/math.comb(7,k))
            result = {
                'trial_id':pre['trial_id'], 'commitment_sha256':crow['sha256'],
                'revealed_condition':hidden['condition'], 'revealed_missing_paths':actual_missing,
                'detection_correct':detection_correct, 'discovery_correct':discovery_correct,
                'reference_scaffold_discovery_correct':scaffold_discovery_correct,
                'repair_proposed':bool(pre['proposed_repair_paths']), 'synthetic_independent_repair_pass':repair_ok,
                'chance_exact_set_guess_probability':chance_discovery,
                'protocol':'commitment_written_before_outcome_ledger'
            }
            f.write(json.dumps(result, sort_keys=True, separators=(',',':'))+'\n')
            counts['trials'] += 1
            counts['detection_correct'] += int(detection_correct)
            counts['discovery_correct'] += int(discovery_correct)
            counts['scaffold_discovery_correct'] += int(scaffold_discovery_correct)
            counts['repair_pass'] += int(repair_ok)
            counts['chance_exact_set_guess_probability_sum'] += chance_discovery
            by_condition[hidden['condition']]['trials'] += 1
            for key, val in [('detection_correct',detection_correct),('discovery_correct',discovery_correct),('repair_pass',repair_ok)]:
                by_condition[hidden['condition']][key] += int(val)
            by_condition[hidden['condition']][f'missing_count_{k}'] += 1
            class_counts[hidden['condition']] += 1

    # Integrity and baseline preservation verification.
    reread_commit = [json.loads(x) for x in commitments_path.read_text().splitlines()]
    reread_ledger = [json.loads(x) for x in ledger_path.read_text().splitlines()]
    hashes_valid = all(sha(canon(r['precommit'])) == r['sha256'] for r in reread_commit)
    linked = all(a['precommit']['trial_id']==b['trial_id'] and a['sha256']==b['commitment_sha256'] for a,b in zip(reread_commit,reread_ledger))
    ids_unique = len({r['precommit']['trial_id'] for r in reread_commit}) == TRIALS
    after = {str(p.relative_to(ROOT)): {'sha256':file_hash(p),'size_bytes':p.stat().st_size} for p in BASELINES}
    baseline_unchanged = before == after
    assert len(reread_commit)==TRIALS and len(reread_ledger)==TRIALS
    assert counts['trials']==TRIALS
    assert hashes_valid and linked and ids_unique and baseline_unchanged

    # Flat trial CSV, produced after reveal; separate from precommit file.
    csv_path = OUT/'results.csv'
    with csv_path.open('x',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['trial_id','atlas_config_id','atlas_index','condition','missing_paths','observed_path_ids','learner_detection','learner_discovered_missing','discovery_correct','repair_pass','chance_exact_set_guess_probability'])
        for pre,r in zip([x['precommit'] for x in trial_specs],reread_ledger):
            w.writerow([r['trial_id'],pre['atlas_config_id'],pre['atlas_index'],r['revealed_condition'],json.dumps(r['revealed_missing_paths']),json.dumps([h['path_id'] for h in pre['observed_handles']]),pre['learner_decision']['detection'],json.dumps(pre['learner_decision']['discovered_missing_paths']),r['discovery_correct'],r['synthetic_independent_repair_pass'],r['chance_exact_set_guess_probability']])

    summary = {
      'experiment':'EXP-SN004-04','status':'COMPLETED_SYNTHETIC_SURROGATE','run_date':'2026-10-20','seed':SEED,
      'trials_requested':TRIALS,'trials_executed':counts['trials'],
      'condition_distribution':dict(class_counts),
      'atlas':{'expected_rows':ATLAS_TOTAL,'manifest_rows_verified':manifest['verification']['generated_data_rows'],'batch_count':manifest['verification']['batch_file_count'],'holdout_index_start_inclusive':HOLDOUT_START,'holdout_index_end_exclusive':ATLAS_TOTAL,'holdout_fraction_by_index':0.30,'sampled_unique_holdout_configs':len({s['precommit']['atlas_config_id'] for s in trial_specs})},
      'metrics':{
        'detection_accuracy':counts['detection_correct']/TRIALS,
        'discovery_exact_set_accuracy':counts['discovery_correct']/TRIALS,
        'reference_scaffold_exact_set_accuracy':counts['scaffold_discovery_correct']/TRIALS,
        'synthetic_independent_repair_pass_rate':counts['repair_pass']/TRIALS,
        'mean_exact_set_chance_probability':counts['chance_exact_set_guess_probability_sum']/TRIALS,
        'by_condition':{k:dict(v) for k,v in by_condition.items()},
        'chance_baselines':{'majority_detection_accuracy_if_always_predict_missing':0.80,'uniform_single_missing_path_guess':1/7,'uniform_two_missing_set_guess':1/math.comb(7,2),'uniform_three_missing_set_guess':1/math.comb(7,3)}
      },
      'integrity_checks':{'all_commitment_hashes_recomputed_valid':hashes_valid,'commitments_link_to_revealed_results':linked,'unique_trial_ids':ids_unique,'commitments_written_before_outcome_ledger':True,'baseline_files_hash_identical_before_after':baseline_unchanged,'all_checks_passed':all([hashes_valid,linked,ids_unique,baseline_unchanged])},
      'baseline_reproduction_status':'NOT_POSSIBLE_FROM_RECOVERED_ARTIFACTS: no prior intervention-pathway semantics or executable missing-intervention scaffold was found. This run is a newly operationalized synthetic surrogate, not a reproduction of an undocumented condition.',
      'learner_scope':'Generic set-difference over visible pathway IDs and validation of state-bound response tokens; defect/condition labels and true missing-path set are not supplied to learner.',
      'reference_scaffold_scope':'Newly defined transparent set-difference comparator; not claimed to be the original diagnostic scaffold.',
      'repair_scope':'Synthetic reconstruction of absent handles under the declared contract, checked using an independent nonce; not a physical or real-world intervention repair.',
      'limitations':['Visible pathway IDs make exact discovery structurally easy once a handle is absent.','This tests the declared synthetic contract, not full SDU dynamics or latent causal inference.','The atlas labels 0..6 remain placeholders and do not have intrinsic intervention semantics.','Holdout is a deterministic index-range split, not a claim of semantic generalization across a validated causal model.'],
      'baseline_hashes_before':before,'baseline_hashes_after':after,
      'artifacts':{'commitments':'commitments.jsonl','ledger':'append_only_results_ledger.jsonl','csv':'results.csv','script':'exp_sn004_04_missing_intervention.py'},
      'environment':{'python':sys.version.split()[0],'platform':platform.platform()}
    }
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    # Hash manifest includes every run output except itself to avoid recursive hashing.
    manifest_out={p.name:{'sha256':file_hash(p),'size_bytes':p.stat().st_size} for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='manifest_sha256.json'}
    (OUT/'manifest_sha256.json').write_text(json.dumps(manifest_out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=='__main__': main()