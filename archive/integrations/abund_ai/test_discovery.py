"""Offline tests for Abund task selection and endpoint validation."""
import importlib.util
import pathlib
import unittest
from unittest.mock import patch

FILE = pathlib.Path(__file__).with_name("discover_tasks.py")
spec = importlib.util.spec_from_file_location("discover_tasks", FILE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class DiscoveryTests(unittest.TestCase):
    def test_python_request_is_prioritized(self):
        self.assertGreater(module.score({"action": "accept_request", "why": "Python Windows automation"}), 0)

    def test_crypto_requests_excluded(self):
        self.assertEqual(module.score({"action": "accept_request", "why": "Python crypto wallet payment"}), -1)

    def test_votes_are_not_tasks(self):
        self.assertEqual(module.score({"action": "vote_poll", "why": "Python"}), -1)

    def test_external_url_rejected(self):
        self.assertEqual(module.read_public_post("https://evil.example/posts/123", "fake")["state"], "not_a_public_post")

    def test_invalid_post_id_rejected(self):
        self.assertEqual(module.read_public_post("/api/v1/posts/not-an-id", "fake")["state"], "not_a_public_post")

    def test_request_board_failure_is_nonfatal(self):
        with patch.object(module.urllib.request, "urlopen", side_effect=module.urllib.error.URLError("offline")):
            result = module.read_request_board("fake")
        self.assertEqual(result["state"], "unavailable")
        self.assertEqual(result["items"], [])

if __name__ == "__main__":
    unittest.main()
