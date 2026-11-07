"""CF-091: no local relay tokens or transport details in error logs."""
import pathlib
import sys
import traceback
import unittest
import urllib.error
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import cf_public_relay as relay

SECRET = "ghp_CF0NeverLogSyntheticSecret_XYZ123"


class BadJsonResponse:
    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, *_):
        return ("{" + SECRET + "}").encode()


class SecretSafeHTTPTests(unittest.TestCase):
    def assert_safe(self, error):
        self.assertIsInstance(error, relay.RelayError)
        self.assertNotIn(SECRET, str(error))
        self.assertTrue(error.__suppress_context__)
        displayed = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        self.assertNotIn(SECRET, displayed, "Exception chain printed the local secret")

    def test_http_error_message_never_reaches_logs(self):
        upstream = urllib.error.HTTPError(
            "https://api.github.com/repos/example", 503,
            SECRET, {}, None
        )
        with patch.object(relay.urllib.request, "urlopen", side_effect=upstream):
            with self.assertRaises(relay.RelayError) as caught:
                relay.HttpRepo(token=SECRET).request("POST", "/repos/example", {})
        self.assertEqual(str(caught.exception), "github_http_503")
        self.assert_safe(caught.exception)

    def test_network_error_reason_never_reaches_logs(self):
        with patch.object(relay.urllib.request, "urlopen",
                          side_effect=urllib.error.URLError(SECRET)):
            with self.assertRaises(relay.RelayError) as caught:
                relay.HttpRepo(token=SECRET).request("GET", "/repos/example")
        self.assertEqual(str(caught.exception), "github_unreachable")
        self.assert_safe(caught.exception)

    def test_malformed_response_does_not_print_transport_payload(self):
        with patch.object(relay.urllib.request, "urlopen",
                          return_value=BadJsonResponse()):
            with self.assertRaises(relay.RelayError) as caught:
                relay.HttpRepo(token=SECRET).request("GET", "/repos/example")
        self.assertEqual(str(caught.exception), "github_invalid_json")
        self.assert_safe(caught.exception)

    def test_write_token_remains_header_only(self):
        with patch.object(relay.urllib.request, "urlopen",
                          return_value=BadJsonResponse()) as send:
            with self.assertRaises(relay.RelayError):
                relay.HttpRepo(token=SECRET).request("GET", "/repos/example")
        request = send.call_args.args[0]
        self.assertIn(SECRET, request.get_header("Authorization"))
        self.assertNotIn(SECRET, request.full_url)


if __name__ == "__main__":
    unittest.main()
