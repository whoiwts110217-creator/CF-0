#!/usr/bin/env python3
"""EXP-SN004-03 blinded defect-type test bench (synthetic, reproducible).

Groups:
 A: in-class integer translations and sign-flip affine rules y = s*x + b, s in {-1,+1}.
 B: out-of-class multipliers y = a*x (a not +/-1) and coordinate distortion y = x^2.

Protocol:
 1. Evaluator privately generates trial truth using a seeded RNG.
 2. Learner sees calibration pairs only and a held-out x.
 3. Learner freezes prediction/action; SHA-256 commitment is written to a separate
    commitments file for ALL trials before any held-out outcomes are written.
 4. Evaluator reveals held-out outcomes into the append-only results ledger.
This is a local synthetic test, not evidence about real-world SDU dynamics.
"""
import csv, hashlib, json, random, sys, platform
from pathlib import Path
from collections import Counter

SEED = 20261020
TRIALS = 10_000
GROUP_A = TRIALS // 2
OUT = Path("exp_sn004_03_run_20261020")
OUT.mkdir(exist_ok=True)

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def evaluator_rule(rng, group):
    if group == "A":
        kind = rng.choice(["unit_increment", "multistep_jump", "sign_flip"])
        if kind == "unit_increment":
            sign, offset = 1, rng.choice([-1, 1])
        elif kind == "multistep_jump":
            sign, offset = 1, rng.choice([-5, -4, -3, -2, 2, 3, 4, 5])
        else:
            sign, offset = -1, 0
        return {"kind": kind, "sign": sign, "offset": offset}
    kind = rng.choice(["multiplicative", "coordinate_distortion"])
    if kind == "multiplicative":
        return {"kind": kind, "multiplier": rng.choice([-3, -2, 2, 3])}
    return {"kind": kind}

def apply_rule(rule, x):
    if rule["kind"] in ("unit_increment", "multistep_jump", "sign_flip"):
        return rule["sign"] * x + rule["offset"]
    if rule["kind"] == "multiplicative":
        return rule["multiplier"] * x
    if rule["kind"] == "coordinate_distortion":
        return x * x
    raise ValueError(rule["kind"])

def learner_decision(calibration, test_x):
    # Fit candidate y=s*x+b from first two calibration points, then validate every point.
    x1, y1 = calibration[0]
    x2, y2 = calibration[1]
    if x2 == x1:
        return {"classification": "MODEL_CLASS_INADEQUATE", "prediction": None,
                "action": "reject_model_class", "reason": "degenerate_calibration"}
    slope_num, slope_den = y2-y1, x2-x1
    # Only candidate slopes +1 or -1 are in the declared model class.
    if slope_num == slope_den:
        sign = 1
    elif slope_num == -slope_den:
        sign = -1
    else:
        return {"classification": "MODEL_CLASS_INADEQUATE", "prediction": None,
                "action": "reject_model_class", "reason": "slope_outside_class"}
    offset = y1 - sign*x1
    if not all(y == sign*x + offset for x, y in calibration):
        return {"classification": "MODEL_CLASS_INADEQUATE", "prediction": None,
                "action": "reject_model_class", "reason": "calibration_inconsistent"}
    return {"classification": "IN_CLASS", "prediction": sign*test_x + offset,
            "action": "predict", "reason": "validated_affine_slope_pm1"}

def main():
    # Separate deterministic streams: evaluator truth and trial input generation.
    eval_rng = random.Random(SEED)
    input_rng = random.Random(SEED ^ 0x5D005D00)
    trial_specs = []
    for i in range(TRIALS):
        group = "A" if i < GROUP_A else "B"
        rule = evaluator_rule(eval_rng, group)
        # Distinct fixed calibration x-values; held-out point is outside calibration set.
        calibration_x = [-3, -1, 2]
        test_x = input_rng.choice([-7, -6, -5, 5, 6, 7])
        calibration = [(x, apply_rule(rule, x)) for x in calibration_x]
        decision = learner_decision(calibration, test_x)
        precommit = {
            "trial_id": f"EXP-SN004-03-{i+1:05d}",
            "group": group,
            "calibration": calibration,
            "held_out_x": test_x,
            "prediction": decision["prediction"],
            "classification": decision["classification"],
            "action": decision["action"],
            "reason": decision["reason"],
        }
        commitment = sha256_bytes(canonical(precommit))
        trial_specs.append((precommit, commitment, rule))

    # Commit all predictions/actions before writing/revealing any held-out outcomes.
    commitments_path = OUT / "commitments.jsonl"
    with commitments_path.open("w", encoding="utf-8") as f:
        for precommit, commitment, _rule in trial_specs:
            f.write(json.dumps({"precommit": precommit, "sha256": commitment},
                               sort_keys=True, separators=(",", ":")) + "\n")

    # Now reveal outcomes and append result records to a new, run-specific ledger.
    ledger_path = OUT / "append_only_results_ledger.jsonl"
    counts = Counter()
    by_group = {"A": Counter(), "B": Counter()}
    with ledger_path.open("x", encoding="utf-8") as f:
        for precommit, commitment, rule in trial_specs:
            x = precommit["held_out_x"]
            outcome = apply_rule(rule, x)
            predicted = precommit["prediction"]
            cls = precommit["classification"]
            if cls == "IN_CLASS":
                correct = (predicted == outcome)
                expected_class = "IN_CLASS" if rule["kind"] in (
                    "unit_increment", "multistep_jump", "sign_flip") else "MODEL_CLASS_INADEQUATE"
                class_correct = cls == expected_class
            else:
                correct = None
                expected_class = "IN_CLASS" if rule["kind"] in (
                    "unit_increment", "multistep_jump", "sign_flip") else "MODEL_CLASS_INADEQUATE"
                class_correct = cls == expected_class
            rec = {
                "trial_id": precommit["trial_id"],
                "commitment_sha256": commitment,
                "revealed_outcome": outcome,
                "evaluator_defect_type": rule["kind"],
                "learner_classification_correct": class_correct,
                "prediction_correct_if_issued": correct,
                "protocol": "commitment_written_before_outcome_reveal"
            }
            f.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
            counts["trials"] += 1
            counts[f"group_{precommit['group']}"] += 1
            counts["classification_correct"] += int(class_correct)
            by_group[precommit["group"]]["trials"] += 1
            by_group[precommit["group"]]["classification_correct"] += int(class_correct)
            by_group[precommit["group"]][f"type_{rule['kind']}"] += 1
            if cls == "IN_CLASS":
                counts["predictions_issued"] += 1
                counts["predictions_correct"] += int(correct)
                by_group[precommit["group"]]["predictions_issued"] += 1
                by_group[precommit["group"]]["predictions_correct"] += int(correct)

    # Verify the commitments and output accounting after reveal.
    commitment_rows = [json.loads(line) for line in commitments_path.read_text().splitlines()]
    result_rows = [json.loads(line) for line in ledger_path.read_text().splitlines()]
    hashes_valid = all(sha256_bytes(canonical(row["precommit"])) == row["sha256"]
                       for row in commitment_rows)
    linked = all(a["precommit"]["trial_id"] == b["trial_id"] and
                 a["sha256"] == b["commitment_sha256"]
                 for a, b in zip(commitment_rows, result_rows))
    ids_unique = len({r["precommit"]["trial_id"] for r in commitment_rows}) == TRIALS
    group_a_correct = by_group["A"]["classification_correct"] == GROUP_A
    group_b_correct = by_group["B"]["classification_correct"] == TRIALS - GROUP_A
    summary = {
        "experiment": "EXP-SN004-03",
        "run_date": "2026-10-20",
        "status": "COMPLETED",
        "seed": SEED,
        "trials_requested": TRIALS,
        "trials_executed": counts["trials"],
        "group_A_trials": counts["group_A"],
        "group_B_trials": counts["group_B"],
        "learner_model_class": "y = s*x + b, where s in {-1,+1} and b is an integer",
        "group_A_defects": ["unit_increment", "multistep_jump", "sign_flip"],
        "group_B_defects": ["multiplicative", "coordinate_distortion"],
        "classification_correct_total": counts["classification_correct"],
        "classification_accuracy": counts["classification_correct"] / TRIALS,
        "predictions_issued": counts["predictions_issued"],
        "predictions_correct": counts["predictions_correct"],
        "prediction_accuracy_when_issued": (counts["predictions_correct"] / counts["predictions_issued"]
                                             if counts["predictions_issued"] else None),
        "by_group": {g: dict(c) for g, c in by_group.items()},
        "integrity_checks": {
            "commitments_written_before_outcome_ledger": True,
            "all_commitment_hashes_recomputed_valid": hashes_valid,
            "all_commitments_link_to_revealed_results": linked,
            "unique_trial_ids": ids_unique,
            "group_A_all_classified_in_class": group_a_correct,
            "group_B_all_rejected_as_model_class_inadequate": group_b_correct,
            "all_checks_passed": all([hashes_valid, linked, ids_unique, group_a_correct, group_b_correct])
        },
        "artifacts": {
            "commitments": commitments_path.name,
            "append_only_results_ledger": ledger_path.name
        },
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "scope_note": "Synthetic controlled test of the specified toy learner and evaluator rules; not empirical validation of the full SDU framework."
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # Flat CSV for convenient inspection.
    with (OUT / "results.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["trial_id","group","calibration","held_out_x","classification","prediction",
                    "action","commitment_sha256","revealed_outcome","defect_type",
                    "classification_correct","prediction_correct_if_issued"])
        for a, b in zip(commitment_rows, result_rows):
            p, r = a["precommit"], b
            w.writerow([p["trial_id"], p["group"], json.dumps(p["calibration"], separators=(",", ":")),
                        p["held_out_x"], p["classification"], p["prediction"], p["action"], a["sha256"],
                        r["revealed_outcome"], r["evaluator_defect_type"], r["learner_classification_correct"],
                        r["prediction_correct_if_issued"]])
    print(json.dumps(summary, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()