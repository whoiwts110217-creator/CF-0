"""CF-119: negative-proof tests for public/cloud HP claims. No physical HP calls."""
import copy
import unittest

from automation_200.decision_engine import propose
from automation_200.hp_authority_gate import assess_public_proof, cloud_hold_reason


def task(tid, stream="priority_logic", hp=False):
    return {"id": tid, "stream": stream, "title": tid,
            "status": "planned", "depends_on": [], "priority": 1,
            "authority": "owner-reviewed", "physical_hp_required": hp}


class HpAuthorityProofGateTests(unittest.TestCase):
    def test_public_health_receipts_scheduler_and_claims_never_grant_hp(self):
        for health in ("fresh_public_report", "stale", "not_published", "unavailable"):
            with self.subTest(health=health):
                report = assess_public_proof(
                    health_state=health, receipt_digest_matched=True,
                    scheduler_window_reported=True, owner_approval_claimed=True)
                self.assertFalse(report["hp_execution_authorized"])
                self.assertFalse(report["physical_hp_identity_attested"])
                self.assertFalse(report["owner_local_approval_verified"])
                self.assertFalse(report["receipt_matching_proves_device_identity"])
                self.assertFalse(report["scheduler_overlap_proves_execution_origin"])
                self.assertEqual(report["scope"], "read_only_cloud_advisory")

    def test_forged_public_proof_cannot_override_task_gate(self):
        sample = {"tasks": [
            task("HP-LOCAL", "hp_install", hp=False),
            task("CF-042", "sidecar", hp=False),
            task("HARDWARE", "real_operations", hp=True),
            task("SOURCE", "security", hp=False),
        ]}
        original = copy.deepcopy(sample)
        result = propose(sample, health_state="fresh_public_report", now=100,
                         owner_preference_ids=["HP-LOCAL", "CF-042", "HARDWARE", "SOURCE"])
        self.assertEqual([x["id"] for x in result["selected"]], ["SOURCE"])
        self.assertEqual(result["held_counts"]["hp_install_needs_local_review"], 1)
        self.assertEqual(result["held_counts"]["owner_local_evidence_required"], 1)
        self.assertEqual(result["held_counts"]["physical_hp_required"], 1)
        self.assertFalse(result["execution_authorized"])
        self.assertFalse(result["hp_proof_gate"]["hp_execution_authorized"])
        self.assertEqual(sample, original)

    def test_invalid_hp_flag_is_held_not_coerced(self):
        for value in (None, 0, 1, "false", [], {}):
            with self.subTest(value=value):
                entry = task("BOGUS")
                entry["physical_hp_required"] = value
                self.assertEqual(cloud_hold_reason(entry), "invalid_hp_requirement")
                result = propose({"tasks": [entry, task("SAFE")]}, now=100)
                self.assertEqual([x["id"] for x in result["selected"]], ["SAFE"])
                self.assertEqual(result["held_counts"]["invalid_hp_requirement"], 1)

    def test_source_task_not_executable_even_when_eligible(self):
        entry = task("CF-119")
        self.assertIsNone(cloud_hold_reason(entry))
        result = propose({"tasks": [entry]}, now=100)
        self.assertEqual(result["selected"][0]["id"], "CF-119")
        self.assertEqual(result["selected"][0]["action"], "propose_source_work_only")
        self.assertFalse(result["execution_authorized"])
        self.assertFalse(result["hp_proof_gate"]["hp_execution_authorized"])

    def test_invalid_claims_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "invalid_public_health_state"):
            assess_public_proof(health_state="owner_authorized")
        for evidence in (1, "true", None, [], {}):
            with self.subTest(evidence=evidence):
                with self.assertRaisesRegex(ValueError, "invalid_public_proof_claim"):
                    assess_public_proof(health_state="fresh_public_report",
                                        owner_approval_claimed=evidence)
        with self.assertRaisesRegex(ValueError, "invalid_hp_gate_identity"):
            cloud_hold_reason({"id": "", "stream": "hp_install"})
        with self.assertRaisesRegex(ValueError, "invalid_hp_gate_task"):
            cloud_hold_reason("CF-119")


if __name__ == "__main__":
    unittest.main()
