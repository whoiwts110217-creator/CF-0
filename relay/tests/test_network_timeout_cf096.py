"""CF-096: cloud-to-HP relay GitHub HTTP calls have bounded socket timeout.

All calls use mocked transports; no actual GitHub or physical HP access.
A socket timeout does not prove a guaranteed total end-to-end duration.
"""
import json
import pathlib
import sys
import unittest
import urllib.error
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import cf_public_relay as relay

READ = f"/repos/{relay.REPO}/contents/command_queue/inbox?ref=main"
WRITE = f"/repos/{relay.REPO}/contents/command_queue/receipts/00000000-0000-4000-8000-000000000001.json"
SECRET = "CF0SYNTHETIC-NETWORK-FAILURE-DETAIL"


class FakeResponse:
    def __init__(self, value):
        self.payload = json.dumps(value).encode()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, count):
        return self.payload[:count]


class TimeoutBoundaryTests(unittest.TestCase):
    def test_all_fixed_client_http_methods_supply_same_finite_timeout(self):
        self.assertEqual(relay.NETWORK_TIMEOUT_SECONDS, 20)
        self.assertGreater(relay.NETWORK_TIMEOUT_SECONDS, 0)
        self.assertLessEqual(relay.NETWORK_TIMEOUT_SECONDS, 30)
        with patch.object(relay.urllib.request, "urlopen",
                          return_value=FakeResponse({"ok": True})) as transport:
            client = relay.HttpRepo(token="synthetic")
            self.assertEqual(client.request("GET", READ), {"ok": True})
            self.assertEqual(client.request("PUT", WRITE, {"v": 1}), {"ok": True})
            self.assertEqual(transport.call_count, 2)
            for call in transport.call_args_list:
                self.assertEqual(call.kwargs["timeout"], relay.NETWORK_TIMEOUT_SECONDS)

    def test_timeouts_become_fixed_reason_not_repeated_attempts(self):
        for failure in (TimeoutError(SECRET), urllib.error.URLError(SECRET)):
            with self.subTest(error=type(failure).__name__):
                with patch.object(relay.urllib.request, "urlopen",
                                  side_effect=failure) as transport:
                    with self.assertRaisesRegex(relay.RelayError, "^github_unreachable$") as caught:
                        relay.HttpRepo(token="synthetic").request("GET", READ)
                    self.assertTrue(caught.exception.__suppress_context__)
                    self.assertNotIn(SECRET, str(caught.exception))
                    self.assertEqual(transport.call_count, 1)
                    self.assertEqual(transport.call_args.kwargs["timeout"], 20)

    def test_write_timeout_has_no_implicit_duplicate_retry(self):
        with patch.object(relay.urllib.request, "urlopen",
                          side_effect=TimeoutError(SECRET)) as transport:
            with self.assertRaisesRegex(relay.RelayError, "^github_unreachable$"):
                relay.HttpRepo(token="synthetic").request("PUT", WRITE, {"v": 1})
            self.assertEqual(transport.call_count, 1)

    def test_unsupported_host_or_method_fails_before_network(self):
        with patch.object(relay.urllib.request, "urlopen") as transport:
            with self.assertRaises(relay.RelayError):
                relay.HttpRepo(api="https://unexpected.example").request("GET", READ)
            with self.assertRaises(relay.RelayError):
                relay.HttpRepo().request("DELETE", WRITE)
            transport.assert_not_called()


if __name__ == "__main__":
    unittest.main()
