"""CF-094: no arbitrary GitHub repository or network endpoint override.

The public worker always uses one owner-approved repository and the fixed
inbox/receipt/health endpoints. Only explicit offline tests may use a local
127.0.0.1 server. No real network or HP machine is accessed by these tests.
"""
import pathlib
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import cf_public_relay as relay

ROOT = f"/repos/{relay.REPO}/contents/"
PING_ID = "00000000-0000-4000-8000-000000000001"


class FixedRepositoryTests(unittest.TestCase):
    def test_default_repository_api_and_existing_actions_preserved(self):
        repo = relay.HttpRepo()
        self.assertEqual(repo.repo, relay.REPO)
        self.assertEqual(repo.api, "https://api.github.com")
        self.assertEqual(relay.ALLOWED, frozenset(("ping", "hp_status", "sidecar_verify")))
        expected = [
            ("GET", ROOT + "command_queue/inbox?ref=main"),
            ("GET", ROOT + "command_queue/inbox/" + PING_ID + ".json?ref=main"),
            ("GET", ROOT + "command_queue/receipts/" + PING_ID + ".json?ref=main"),
            ("PUT", ROOT + "command_queue/receipts/" + PING_ID + ".json"),
            ("GET", ROOT + "relay/health/latest.json?ref=main"),
            ("PUT", ROOT + "relay/health/latest.json"),
        ]
        for method, path in expected:
            with self.subTest(method=method, path=path):
                repo._assert_fixed_target(method, path)

    def test_constructor_rejects_wrong_repository_before_network(self):
        with patch.object(relay.urllib.request, "urlopen") as transport:
            for wrong in ("attacker/repo", "whoiwts110217-creator/other",
                          "../CF-0", relay.REPO + "/../../elsewhere", "",
                          relay.REPO + "?ref=other"):
                with self.subTest(wrong=wrong):
                    with self.assertRaisesRegex(relay.RelayError, "^repo_override_not_allowed$"):
                        relay.HttpRepo(repo=wrong, token="synthetic-token")
            transport.assert_not_called()

    def test_constructor_rejects_arbitrary_api_before_network(self):
        invalid = (
            "https://example.net", "https://api.github.com.evil.invalid",
            "http://api.github.com", "http://127.0.0.1:8080",
            "http://127.0.0.1:not-a-port", "https://user:pass@evil.invalid",
            "file:///private/path", "https://api.github.com/other/path",
        )
        with patch.object(relay.urllib.request, "urlopen") as transport:
            for url in invalid:
                with self.subTest(url=url):
                    with self.assertRaisesRegex(relay.RelayError, "^api_override_not_allowed$"):
                        relay.HttpRepo(api=url, token="synthetic-token")
            transport.assert_not_called()

    def test_mutated_client_rejects_repo_and_api_changes_before_network(self):
        with patch.object(relay.urllib.request, "urlopen") as transport:
            repo = relay.HttpRepo(token="synthetic-token")
            repo.repo = "attacker/repo"
            with self.assertRaisesRegex(relay.RelayError, "^repo_override_not_allowed$"):
                repo.files()
            repo.repo = relay.REPO
            repo.api = "https://bad.invalid"
            with self.assertRaisesRegex(relay.RelayError, "^api_override_not_allowed$"):
                repo.files()
            transport.assert_not_called()

    def test_only_whitelisted_repo_paths_methods_and_branch_allowed(self):
        bad_requests = (
            ("GET", "/repos/attacker/repo/contents/command_queue/inbox?ref=main"),
            ("GET", ROOT + "command_queue/inbox?ref=dev"),
            ("GET", ROOT + "command_queue/inbox/../receipts/" + PING_ID + ".json?ref=main"),
            ("GET", ROOT + "command_queue/receipts/" + PING_ID + ".json?ref=dev"),
            ("GET", ROOT + "command_queue/receipts/" + PING_ID + ".json"),
            ("PUT", ROOT + "command_queue/inbox/" + PING_ID + ".json"),
            ("PUT", ROOT + "README.md"),
            ("DELETE", ROOT + "command_queue/receipts/" + PING_ID + ".json"),
            ("POST", ROOT + "relay/health/latest.json"),
            ("GET", ROOT + "relay/health/latest.json%3Fref=main"),
            ("GET", "https://evil.invalid/"),
        )
        with patch.object(relay.urllib.request, "urlopen") as transport:
            client = relay.HttpRepo(token="synthetic-token")
            for method, path in bad_requests:
                with self.subTest(method=method, path=path):
                    with self.assertRaises(relay.RelayError):
                        client.request(method, path)
            transport.assert_not_called()

    def test_loopback_test_override_cannot_target_other_networks_or_repos(self):
        client = relay.HttpRepo(
            api="http://127.0.0.1:8765", test_loopback=True,
            token="synthetic-only")
        client._assert_fixed_target("GET", ROOT + "command_queue/inbox?ref=main")
        with self.assertRaisesRegex(relay.RelayError, "^repo_override_not_allowed$"):
            relay.HttpRepo(repo="attacker/repo", api="http://127.0.0.1:8765", test_loopback=True)
        with self.assertRaisesRegex(relay.RelayError, "^api_override_not_allowed$"):
            relay.HttpRepo(api="http://192.0.2.1:8765", test_loopback=True)
        with self.assertRaisesRegex(relay.RelayError, "^api_override_not_allowed$"):
            relay.HttpRepo(api="http://127.0.0.1.evil.invalid:8765", test_loopback=True)


if __name__ == "__main__":
    unittest.main()
