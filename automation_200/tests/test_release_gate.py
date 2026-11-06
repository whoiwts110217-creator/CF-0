import unittest

from automation_200.release_gate import GATES, evaluate


class ReleaseGateTests(unittest.TestCase):
    def test_unknown_defaults_to_unverified(self):
        result = evaluate({})
        self.assertFalse(result["release_ready"])
        self.assertEqual(result["verified_count"], 0)
        self.assertEqual(len(result["gates"]), 8)

    def test_partial_evidence_does_not_release(self):
        result = evaluate({GATES[0]: {"status": "verified", "evidence": ["https://example.org/receipt"]}})
        self.assertFalse(result["release_ready"])
        self.assertEqual(result["verified_count"], 1)

    def test_all_verified_with_references(self):
        result = evaluate({k: {"status": "verified", "evidence": ["reviewed:artifact"]} for k in GATES})
        self.assertTrue(result["release_ready"])

    def test_verified_without_evidence_rejected(self):
        with self.assertRaises(ValueError):
            evaluate({GATES[0]: {"status": "verified"}})

    def test_invalid_status_rejected(self):
        with self.assertRaises(ValueError):
            evaluate({GATES[0]: {"status": "complete"}})

    def test_unknown_gate_rejected(self):
        with self.assertRaises(ValueError):
            evaluate({"invented": {"status": "verified", "evidence": ["x"]}})


if __name__ == "__main__":
    unittest.main()
