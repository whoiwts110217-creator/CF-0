"""Network-free tests for one-time CF-0 agent-native outreach receipts."""
import unittest

from ai_tracker.agent_native_round_2_2026_11_07 import (
    normalize_public_link, parse_swarmmemo_receipt, parse_msgboard_receipt,
)


class OutboundReceiptTests(unittest.TestCase):
    def test_only_expected_public_hosts(self):
        self.assertEqual(
            normalize_public_link("https://swarmmemo.com/api/thread/abc", "swarmmemo.com"),
            "https://swarmmemo.com/api/thread/abc",
        )
        self.assertIsNone(normalize_public_link("https://other.example/secret", "swarmmemo.com"))
        self.assertIsNone(normalize_public_link("https://swarmmemo.com@evil.example/", "swarmmemo.com"))

    def test_swarmmemo_requires_server_commit_receipt(self):
        r = parse_swarmmemo_receipt({"ok": True, "receipt": {"id": "m-1"}}, 200)
        self.assertEqual(r["state"], "committed_readback_pending")
        self.assertEqual(r["message_id"], "m-1")
        self.assertEqual(parse_swarmmemo_receipt({"ok": True}, 200)["state"], "unverified_response")

    def test_swarmmemo_accepts_only_safe_readback_url(self):
        r = parse_swarmmemo_receipt({
            "ok": True, "receipt": {"id": "m-1"},
            "shared_receipt": {"publication": {"read_back": "https://swarmmemo.com/api/thread/m-1"}},
        }, 200)
        self.assertEqual(r["state"], "confirmed_public_readback_link")
        bad = parse_swarmmemo_receipt({
            "ok": True, "receipt": {"id": "m-1"},
            "shared_receipt": {"publication": {"read_back": "https://evil.example/token"}},
        }, 200)
        self.assertIsNone(bad.get("public_url"))

    def test_msgboard_requires_successful_http_response(self):
        self.assertEqual(parse_msgboard_receipt({}, 400)["state"], "http_error")
        self.assertEqual(parse_msgboard_receipt({}, 200)["state"], "accepted_link_unverified")


if __name__ == "__main__":
    unittest.main()
