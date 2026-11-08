"""Offline tests: no DNS, share URL, file transfers or site mutations."""
import unittest
from automation_200.vault_access_probe import classify, HOST


class VaultProbeTests(unittest.TestCase):
    def test_unchanged_allowlisted_host(self):
        self.assertEqual(HOST, "folder-drop-vault.whoiwts110217.chatgpt.site")

    def test_root_success_not_equal_download_success(self):
        self.assertEqual(classify(200), "root_reachable")
        self.assertEqual(classify(206), "root_reachable")

    def test_access_denied(self):
        self.assertEqual(classify(401), "access_denied")
        self.assertEqual(classify(403), "access_denied")

    def test_auth_and_other_redirects(self):
        self.assertEqual(classify(302, redirect="/signin"), "login_redirect")
        self.assertEqual(classify(307, redirect="/elsewhere"), "redirect_needs_review")

    def test_unknown_statuses_fail_observation(self):
        self.assertEqual(classify(404), "root_not_found")
        self.assertEqual(classify(405), "method_not_allowed")
        self.assertEqual(classify(500), "http_error")


if __name__ == "__main__":
    unittest.main()
