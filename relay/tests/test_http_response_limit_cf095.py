"""CF-095: exactly bounded HTTP response reads before JSON parsing.

Network-free; fake byte streams prove exact 1,000,001-byte read cap and a
1,000,000-byte acceptance boundary, with no private payload echoed.
"""
import json
import pathlib
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import cf_public_relay as relay


PATH = f"/repos/{relay.REPO}/contents/command_queue/inbox?ref=main"
SECRET = "CF0SyntheticPrivateBody741"


class FakeResponse:
    def __init__(self, data):
        self.data = data
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, n=-1):
        self.calls.append(n)
        return self.data[:n]


class HTTPResponseLimitTests(unittest.TestCase):
    def test_exact_limit_accepts_valid_one_megabyte_json(self):
        prefix = b'{"safe": true}'
        response = FakeResponse(prefix + b" " * (1_000_000 - len(prefix)))
        with patch.object(relay.urllib.request, "urlopen", return_value=response) as open_url:
            result = relay.HttpRepo().request("GET", PATH)
        self.assertEqual(result, {"safe": True})
        self.assertEqual(response.calls, [1_000_001])
        self.assertEqual(open_url.call_args.kwargs.get("timeout"), 20)

    def test_one_byte_over_limit_refused_before_json_or_display(self):
        prefix = b'{"private":"' + SECRET.encode() + b'"}'
        # The body is syntactically valid JSON, but its size is unacceptable.
        response = FakeResponse(prefix + b" " * (1_000_001 - len(prefix)))
        with patch.object(relay.urllib.request, "urlopen", return_value=response):
            with self.assertRaisesRegex(relay.RelayError, "^response_too_large$") as caught:
                relay.HttpRepo(token="synthetic").request("GET", PATH)
        self.assertEqual(response.calls, [1_000_001])
        self.assertNotIn(SECRET, str(caught.exception))

    def test_extremely_large_stream_never_read_fully(self):
        response = FakeResponse(b'{"secret":"' + SECRET.encode() + b'"}' + b" " * 1_500_000)
        with patch.object(relay.urllib.request, "urlopen", return_value=response):
            with self.assertRaisesRegex(relay.RelayError, "^response_too_large$"):
                relay.HttpRepo().request("GET", PATH)
        self.assertEqual(response.calls, [1_000_001])

    def test_small_response_and_unauthorized_target_handling_unchanged(self):
        response = FakeResponse(json.dumps([{"name": "safe"}]).encode())
        with patch.object(relay.urllib.request, "urlopen", return_value=response):
            result = relay.HttpRepo().request("GET", PATH)
        self.assertEqual(result, [{"name": "safe"}])
        with patch.object(relay.urllib.request, "urlopen") as open_url:
            with self.assertRaises(relay.RelayError):
                relay.HttpRepo().request("GET", "/repos/other/repo/contents/README.md")
            open_url.assert_not_called()


if __name__ == "__main__":
    unittest.main()
