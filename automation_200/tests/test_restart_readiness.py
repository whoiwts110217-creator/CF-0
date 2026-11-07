"""Synthetic boundary checks for the non-destructive CF-0 restart readiness gate."""
import unittest

from automation_200.restart_readiness import ROOT, RESTART_GATES, declared_gates, evaluate


class RestartReadinessTests(unittest.TestCase):
    def test_current_repo_cannot_be_called_restart_ready(self):
        result = evaluate(ROOT)
        self.assertEqual(result["schema"], "cf0.restart_readiness.v1")
        self.assertFalse(result["cutover_ready"])
        self.assertFalse(result["full_cf200_closure_ready"])
        self.assertEqual(result["action"], "READ_ONLY_NO_RESET")
        self.assertEqual(result["target_work_orders"], 200)
        self.assertLess(result["verified_work_orders"], 200)
        self.assertTrue(result["release_gate"]["total_gates"] >= 8)

    def test_unverified_gates_fail_closed(self):
        self.assertEqual(set(declared_gates({})), set(RESTART_GATES))
        self.assertTrue(all(v["status"] == "unverified" for v in declared_gates({}).values()))

    def test_evidence_cannot_be_claimed_without_refs(self):
        with self.assertRaisesRegex(ValueError, "requires evidence"):
            declared_gates({"owner_cutover_approval": {"status": "verified", "evidence": []}})

    def test_unknown_evidence_or_invalid_reference_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown restart gate"):
            declared_gates({"run_an_unrestricted_command": {"status": "verified"}})
        with self.assertRaisesRegex(ValueError, "invalid gate references"):
            declared_gates({"seven_day_unattended_cycle": {"status": "verified", "evidence": ["file:///private"]}})

    def test_evaluation_is_read_only(self):
        paths = [
            ROOT / "automation_200/registry.json",
            ROOT / "docs/PUBLIC_CONTINUITY_STATE.json",
            ROOT / "automation_200/OWNER_CAPABILITY_CONTRACT.json",
        ]
        before = {str(path): path.read_bytes() for path in paths}
        evaluate(ROOT)
        self.assertEqual(before, {str(path): path.read_bytes() for path in paths})


if __name__ == "__main__":
    unittest.main()
