"""No-network regression tests for the public Issue #16 monitor."""
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from ai_tracker import monitor_public_issue as monitor


def page(comments, next_page=False):
    response = io.BytesIO(json.dumps(comments).encode())
    response.headers = {"Link": '<https://example.org/>; rel="next"'} if next_page else {}
    return response


class PublicIssueMonitorTests(unittest.TestCase):
    def test_empty_issue(self):
        summary = monitor.summarize([])
        self.assertEqual(summary["public_comments_observed"], 0)
        self.assertEqual(summary["external_response_urls"], [])

    def test_invalid_payload_rejected(self):
        with self.assertRaisesRegex(ValueError, "comments list"):
            monitor.summarize({"error": "synthetic rate limit"})

    def test_pagination_stays_on_the_fixed_github_issue(self):
        with (
            patch.dict(os.environ, {"GITHUB_TOKEN": "synthetic-test-token"}, clear=True),
            patch.object(monitor.urllib.request, "urlopen", side_effect=[
                page([{"id": 1}], next_page=True),
                page([{"id": 2}]),
            ]) as request,
        ):
            self.assertEqual(monitor.fetch_comments(), ([{"id": 1}, {"id": 2}], True))
        for number, call in enumerate(request.call_args_list, 1):
            self.assertEqual(call.args[0].full_url, f"{monitor.API}&page={number}")
            self.assertEqual(call.args[0].get_header("Authorization"), "Bearer synthetic-test-token")

    def test_page_cap_reports_partial_coverage(self):
        with (
            patch.object(monitor, "MAX_PAGES", 1),
            patch.object(monitor.urllib.request, "urlopen", return_value=page([], next_page=True)),
        ):
            self.assertEqual(monitor.fetch_comments(), ([], False))

    def test_summary_deduplicates_and_omits_comment_content(self):
        visitor = {"id": 2, "user": {"login": "synthetic-visitor"}, "body": "never copy this body"}
        summary = monitor.summarize([
            {"id": 1, "user": {"login": monitor.OWNER.upper()}},
            visitor, visitor,
            {"id": 3, "user": None},
        ])
        self.assertEqual(summary, {
            "public_comments_observed": 3,
            "non_owner_comments_observed": 1,
            "external_responses_verified": 1,
            "external_response_urls": [monitor.ISSUE_URL + "#issuecomment-2"],
        })
        with self.assertRaisesRegex(ValueError, "comment ID"):
            monitor.summarize([{"id": True}])

    def test_rogue_03_plain_non_owner_comments_only_change_observations(self):
        visitor = {"id": 1, "user": {"login": "visitor"}, "body": "Hello"}
        owner = {"id": 2, "user": {"login": monitor.OWNER}}
        second_visitor = {"id": 3, "user": {"login": "second-visitor"}}
        cases = (([visitor], 1), ([owner], 0), ([visitor, owner, second_visitor], 2))
        for comments, expected in cases:
            with self.subTest(expected=expected):
                result = monitor.summarize(comments)
                self.assertEqual(result["non_owner_comments_observed"], expected)
                self.assertEqual(result["external_responses_verified"], expected)
                self.assertNotIn("independent_contributions_verified", result)

    def test_observation_keeps_scheduled_evidence_and_prior_contribution_count(self):
        visitor = {"id": 1, "user": {"login": "visitor"}, "body": "Hello"}
        review_link = monitor.GITHUB + "/blob/main/docs/AI_TRACKER_HANDOFF.md#accepted-public-contributions"
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "status.json"
            output.write_text(json.dumps({
                "schema": "cf0.ai_tracker.status.v1",
                "issue_url": monitor.ISSUE_URL,
                "independent_contributions_verified": 2,
                "independent_contributions_evidence": review_link,
            }), encoding="utf-8")
            environment = {"AI_TRACKER_OUTPUT": str(output), "GITHUB_REPOSITORY": monitor.REPOSITORY}
            with patch.dict(os.environ, environment, clear=True), redirect_stdout(io.StringIO()):
                with patch.object(monitor, "fetch_comments", side_effect=OSError("synthetic failure")):
                    previous = output.read_bytes()
                    with self.assertRaises(OSError):
                        monitor.main()
                    self.assertEqual(output.read_bytes(), previous)
                with patch.object(monitor, "fetch_comments", return_value=([visitor], True)):
                    for event, run in (("schedule", "123"), ("push", "124")):
                        with patch.dict(os.environ, {"GITHUB_EVENT_NAME": event, "GITHUB_RUN_ID": run}):
                            monitor.main()
            saved = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(saved["last_check_run_url"], monitor.GITHUB + "/actions/runs/124")
            self.assertEqual(saved["last_scheduled_run_url"], monitor.GITHUB + "/actions/runs/123")
            self.assertEqual(saved["public_comments_observed"], 1)
            self.assertEqual(saved["non_owner_comments_observed"], 1)
            self.assertEqual(saved["independent_contributions_verified"], 2)
            self.assertEqual(saved["independent_contributions_evidence"], review_link)
            self.assertTrue(saved["comment_scan_complete"])

    def test_partial_scan_keeps_last_complete_snapshot(self):
        visitor = {"id": 12, "user": {"login": "synthetic-visitor"}, "body": "not persisted"}
        saved_url = monitor.ISSUE_URL + "#issuecomment-11"
        prior_time = "2026-11-01T00:00:00+00:00"
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "status.json"
            output.write_text(json.dumps({
                "schema": "cf0.ai_tracker.status.v1",
                "issue_url": monitor.ISSUE_URL,
                "updated_utc": prior_time,
                "comment_scan_complete": True,
                "public_comments_observed": 9,
                "non_owner_comments_observed": 4,
                "external_responses_verified": 4,
                "external_response_urls": [saved_url],
                "independent_contributions_verified": 2,
            }), encoding="utf-8")
            with patch.dict(os.environ, {"AI_TRACKER_OUTPUT": str(output)}, clear=True):
                with patch.object(monitor, "fetch_comments", return_value=([visitor], False)):
                    with redirect_stdout(io.StringIO()):
                        monitor.main()
            partial = json.loads(output.read_text(encoding="utf-8"))
            self.assertFalse(partial["comment_scan_complete"])
            self.assertEqual(partial["last_complete_scan_utc"], prior_time)
            self.assertEqual(partial["public_comments_observed"], 9)
            self.assertEqual(partial["non_owner_comments_observed"], 4)
            self.assertEqual(partial["external_responses_verified"], 4)
            self.assertEqual(partial["external_response_urls"], [saved_url])
            self.assertEqual(partial["independent_contributions_verified"], 2)
            self.assertEqual(partial["partial_comment_scan"]["public_comments_observed"], 1)
            self.assertEqual(partial["partial_comment_scan"]["non_owner_comments_observed"], 1)
            self.assertTrue(partial["partial_comment_scan"]["page_cap_reached"])
            self.assertNotIn("not persisted", output.read_text(encoding="utf-8"))

            with patch.dict(os.environ, {"AI_TRACKER_OUTPUT": str(output)}, clear=True):
                with patch.object(monitor, "fetch_comments", return_value=([visitor], True)):
                    with redirect_stdout(io.StringIO()):
                        monitor.main()
            complete = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(complete["comment_scan_complete"])
            self.assertEqual(complete["public_comments_observed"], 1)
            self.assertEqual(complete["non_owner_comments_observed"], 1)
            self.assertEqual(complete["external_response_urls"], [monitor.ISSUE_URL + "#issuecomment-12"])
            self.assertEqual(complete["independent_contributions_verified"], 2)
            self.assertNotEqual(complete["last_complete_scan_utc"], prior_time)
            self.assertNotIn("partial_comment_scan", complete)

    def test_partial_scan_without_complete_baseline_stays_unverified(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "status.json"
            output.write_text(json.dumps({
                "schema": "cf0.ai_tracker.status.v1",
                "issue_url": monitor.ISSUE_URL,
                "comment_scan_complete": False,
            }), encoding="utf-8")
            with patch.dict(os.environ, {"AI_TRACKER_OUTPUT": str(output)}, clear=True):
                with patch.object(monitor, "fetch_comments", return_value=([], False)):
                    with redirect_stdout(io.StringIO()):
                        monitor.main()
            partial = json.loads(output.read_text(encoding="utf-8"))
            self.assertFalse(partial["comment_scan_complete"])
            self.assertNotIn("public_comments_observed", partial)
            self.assertNotIn("last_complete_scan_utc", partial)
            self.assertEqual(partial["partial_comment_scan"]["public_comments_observed"], 0)
