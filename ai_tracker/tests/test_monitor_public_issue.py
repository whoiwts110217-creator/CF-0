"""No-network regression tests for CF-0 public issue monitor."""
import unittest
from ai_tracker.monitor_public_issue import summarize

class PublicIssueMonitorTests(unittest.TestCase):
    def test_counts_only_non_owner_comments(self):
        records = [
            {"user": {"login": "whoiwts110217-creator"}, "html_url": "https://github.com/whoiwts110217-creator/CF-0/issues/16#issuecomment-1"},
            {"user": {"login": "independent-builder"}, "html_url": "https://github.com/whoiwts110217-creator/CF-0/issues/16#issuecomment-2"},
        ]
        summary = summarize(records)
        self.assertEqual(summary["public_comments_observed"], 2)
        self.assertEqual(summary["external_responses_verified"], 1)
        self.assertEqual(len(summary["external_response_urls"]), 1)

    def test_empty_issue(self):
        summary = summarize([])
        self.assertEqual(summary["public_comments_observed"], 0)
        self.assertEqual(summary["external_response_urls"], [])

    def test_invalid_payload_rejected(self):
        with self.assertRaises(ValueError):
            summarize({"error": "rate limited"})

if __name__ == "__main__":
    unittest.main()
