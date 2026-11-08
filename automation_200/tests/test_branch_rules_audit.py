"""Offline contract tests for CF-0 branch protection baseline."""
import unittest
from automation_200.branch_rules_audit import classify, REPO, RULESET_ID


def sample():
    return {
        "id": RULESET_ID, "source": REPO, "target": "branch",
        "enforcement": "active",
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH", "refs/heads/main"], "exclude": []}},
        "rules": [{"type": "deletion"}, {"type": "non_fast_forward"}],
    }


class TestRulesAudit(unittest.TestCase):
    def test_expected_baseline_does_not_claim_owner_review(self):
        r = classify(sample())
        self.assertEqual(r["state"], "baseline_verified")
        self.assertEqual(r["owner_review_enforced"], "not_established_by_this_check")

    def test_missing_rules_inactive_or_wrong_repo_fail_closed(self):
        for change in (
            lambda d: d["rules"].pop(),
            lambda d: d.update(enforcement="disabled"),
            lambda d: d["conditions"]["ref_name"].update(include=[]),
            lambda d: d.update(source="other/CF-0"),
        ):
            data = sample()
            change(data)
            self.assertNotEqual(classify(data)["state"], "baseline_verified")

    def test_new_write_restrictions_require_review(self):
        for rule in ("update", "pull_request", "required_status_checks"):
            data = sample()
            data["rules"].append({"type": rule})
            result = classify(data)
            self.assertEqual(result["state"], "review_required")
            self.assertTrue(result["automation_write_restriction_detected"])

    def test_malformed_responses_fail_closed(self):
        for data in (None, [], {}, {"rules": "invalid"}, {"conditions": []}):
            self.assertNotEqual(classify(data)["state"], "baseline_verified")


if __name__ == "__main__":
    unittest.main()
