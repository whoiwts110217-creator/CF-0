"""Conservative, secret-safe classification of GitHub 403 rate headers.

The presence of a zero rate budget header is observed evidence only: it
does not prove why a given request was rejected, and never authorizes retry.
"""
import pathlib
import sys
import traceback
import unittest
import urllib.error
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import cf_public_relay as relay


class HTTP403RateHeaderTests(unittest.TestCase):
    def test_403_reports_only_literal_zero_budget(self):
        cases = (
            ({"X-RateLimit-Remaining": "0"}, "github_http_403_rate_budget_zero"),
            ({"X-RateLimit-Remaining": "1"}, "github_http_403"),
            ({"X-RateLimit-Remaining": "0 "}, "github_http_403"),
            ({}, "github_http_403"),
        )
        for headers, expected in cases:
            with self.subTest(headers=headers):
                # The upstream message/body/url are untrusted and must not leak.
                secret = "synthetic_private_token_403_not_for_logs"
                err = urllib.error.HTTPError(
                    "https://api.github.com/secret-" + secret, 403,
                    secret, {**headers, "X-Unrelated": secret}, None)
                with patch.object(relay.urllib.request, "urlopen", side_effect=err) as request:
                    with self.assertRaises(relay.RelayError) as caught:
                        relay.HttpRepo(token=secret).request(
                            "GET", f"/repos/{relay.REPO}/contents/command_queue/inbox?ref=main")
                self.assertEqual(str(caught.exception), expected)
                self.assertEqual(request.call_count, 1, "no rate-limit retry added")
                self.assertTrue(caught.exception.__suppress_context__)
                trace = "".join(traceback.format_exception(caught.exception))
                self.assertNotIn(secret, trace)

    def test_other_http_codes_keep_existing_behavior(self):
        for code, expected in ((404, None), (429, "github_http_429"), (503, "github_http_503")):
            with self.subTest(code=code):
                err = urllib.error.HTTPError("https://api.github.com/", code, "failure",
                                             {"X-RateLimit-Remaining": "0"}, None)
                with patch.object(relay.urllib.request, "urlopen", side_effect=err) as request:
                    if expected is None:
                        output = relay.HttpRepo().request(
                            "GET", f"/repos/{relay.REPO}/contents/command_queue/inbox?ref=main")
                        self.assertIsNone(output)
                    else:
                        with self.assertRaises(relay.RelayError) as caught:
                            relay.HttpRepo().request(
                                "GET", f"/repos/{relay.REPO}/contents/command_queue/inbox?ref=main")
                        self.assertEqual(str(caught.exception), expected)
                self.assertEqual(request.call_count, 1)


    def test_rate_budget_exhaustion_never_starts_or_completes_a_job(self):
        """An inbox listing failure is not an empty successful poll."""
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            state = relay.State(pathlib.Path(folder) / "relay.sqlite3")
            failure = urllib.error.HTTPError(
                "https://api.github.com/redacted", 403, "synthetic",
                {"X-RateLimit-Remaining": "0"}, None)
            with patch.object(relay.urllib.request, "urlopen", side_effect=failure):
                with patch.object(relay, "execute") as execute:
                    with self.assertRaisesRegex(
                            relay.RelayError, "^github_http_403_rate_budget_zero$"):
                        relay.tick(relay.HttpRepo(), state)
                    execute.assert_not_called()
            self.assertEqual(state.count(), 0)
            self.assertEqual(state.unknown_count(), 0)
            self.assertEqual(state.cursor(), "")

if __name__ == "__main__":
    unittest.main()
