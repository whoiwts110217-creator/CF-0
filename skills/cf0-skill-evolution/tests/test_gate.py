import json
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from darwin_gate import evaluate, main


def fixture():
    return {
        "experiment_id": "SYNTHETIC-TEST-ONLY",
        "hard_gates": dict.fromkeys(("owner_authority_unchanged", "privacy_preserved", "capabilities_preserved", "continuity_complete"), True),
        "test_runs": [
            {"id": "n", "kind": "normal", "mode": "full_test", "baseline_pass": False, "candidate_pass": True, "baseline_output_ref": "synthetic:base-n", "candidate_output_ref": "synthetic:cand-n"},
            {"id": "a", "kind": "ambiguous", "mode": "full_test", "baseline_pass": True, "candidate_pass": True, "baseline_output_ref": "synthetic:base-a", "candidate_output_ref": "synthetic:cand-a"},
            {"id": "f", "kind": "failure", "mode": "full_test", "baseline_pass": True, "candidate_pass": True, "baseline_output_ref": "synthetic:base-f", "candidate_output_ref": "synthetic:cand-f"},
        ],
        "judges": [
            {"id": "J1", "vote": "better", "order": "baseline_first", "reason": "synthetic evaluation"},
            {"id": "J2", "vote": "better", "order": "candidate_first", "reason": "synthetic evaluation"},
            {"id": "J3", "vote": "tie", "order": "baseline_first", "reason": "synthetic evaluation"},
        ],
    }


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        (self.path / "before").write_text("original", encoding="utf-8")
        (self.path / "after").write_text("improved", encoding="utf-8")
        self.data = fixture()
        self.data["baseline_sha256"] = hashlib.sha256(b"original").hexdigest()
        self.data["candidate_sha256"] = hashlib.sha256(b"improved").hexdigest()

    def check(self):
        (self.path / "evidence.json").write_text(json.dumps(self.data), encoding="utf-8")
        return evaluate(self.path / "before", self.path / "after", self.path / "evidence.json")

    def test_good_shape_only_goes_to_owner_review(self):
        self.assertEqual(self.check()["decision"], "owner_review_required")
        self.assertFalse(self.check()["publishing_authorized"])

    def test_bound_version_hashes_match_original_bytes(self):
        report = self.check()
        self.assertTrue(report["hashes_match"])
        self.assertEqual(report["baseline_sha256"], self.data["baseline_sha256"])
        self.assertEqual(report["candidate_sha256"], self.data["candidate_sha256"])
        self.assertEqual(report["decision"], "owner_review_required")

    def test_missing_version_hash_needs_evidence(self):
        del self.data["baseline_sha256"]
        report = self.check()
        self.assertEqual(report["decision"], "needs_evidence")
        self.assertFalse(report["hashes_match"])

    def test_malformed_version_hash_needs_evidence(self):
        self.data["candidate_sha256"] = "wrong-hash"
        self.assertEqual(self.check()["decision"], "needs_evidence")

    def test_different_skill_bytes_reject_stale_claim(self):
        (self.path / "after").write_text("new unpinned draft", encoding="utf-8")
        report = self.check()
        self.assertEqual(report["decision"], "reject")
        self.assertFalse(report["hashes_match"])

    def test_swapped_version_hashes_reject(self):
        old = self.data["baseline_sha256"]
        self.data["baseline_sha256"] = self.data["candidate_sha256"]
        self.data["candidate_sha256"] = old
        self.assertEqual(self.check()["decision"], "reject")

    def test_identical_versions_reject(self):
        (self.path / "after").write_text("original", encoding="utf-8")
        self.assertEqual(self.check()["decision"], "reject")

    def test_false_owner_gate_reject(self):
        self.data["hard_gates"]["owner_authority_unchanged"] = False
        self.assertEqual(self.check()["decision"], "reject")

    def test_regression_reject(self):
        self.data["test_runs"][1]["candidate_pass"] = False
        self.assertEqual(self.check()["decision"], "reject")

    def test_missing_gate_requires_evidence(self):
        del self.data["hard_gates"]["privacy_preserved"]
        self.assertEqual(self.check()["decision"], "needs_evidence")

    def test_unknown_hard_gate_requires_evidence(self):
        self.data["hard_gates"]["new_remote_access"] = True
        self.assertEqual(self.check()["decision"], "needs_evidence")

    def test_synthetic_evidence_not_promoted(self):
        self.data["synthetic"] = True
        self.assertEqual(self.check()["decision"], "needs_evidence")

    def test_all_ties_not_improvement(self):
        for j in self.data["judges"]:
            j["vote"] = "tie"
        self.assertEqual(self.check()["decision"], "needs_evidence")

    def test_no_measured_gain_needs_evidence(self):
        self.data["test_runs"][0]["baseline_pass"] = True
        self.assertEqual(self.check()["decision"], "needs_evidence")

    def test_dry_run_not_full_test(self):
        self.data["test_runs"][0]["mode"] = "dry_run"
        self.assertEqual(self.check()["decision"], "needs_evidence")

    def test_even_judge_count_not_accepted(self):
        self.data["judges"].append({"id":"J4","vote":"better","order":"candidate_first","reason":"synthetic"})
        self.assertEqual(self.check()["decision"], "needs_evidence")

    def test_duplicate_judge_not_accepted(self):
        self.data["judges"][1]["id"] = "J1"
        self.assertEqual(self.check()["decision"], "needs_evidence")

    def test_missing_failure_case_not_accepted(self):
        self.data["test_runs"][2]["kind"] = "normal"
        self.assertEqual(self.check()["decision"], "needs_evidence")

    def test_missing_output_ref_not_accepted(self):
        self.data["test_runs"][0]["candidate_output_ref"] = ""
        self.assertEqual(self.check()["decision"], "needs_evidence")

    def test_output_file_create_only(self):
        (self.path / "evidence.json").write_text(json.dumps(self.data), encoding="utf-8")
        out = self.path / "gate.json"
        self.assertEqual(main([str(self.path / "before"), str(self.path / "after"), str(self.path / "evidence.json"), "--out", str(out)]), 0)
        original = out.read_bytes()
        self.assertEqual(main([str(self.path / "before"), str(self.path / "after"), str(self.path / "evidence.json"), "--out", str(out)]), 3)
        self.assertEqual(out.read_bytes(), original)

    def test_invalid_json_errors(self):
        (self.path / "evidence.json").write_text("not json", encoding="utf-8")
        self.assertEqual(main([str(self.path / "before"), str(self.path / "after"), str(self.path / "evidence.json")]), 3)


if __name__ == "__main__":
    unittest.main()
