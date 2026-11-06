"""Offline checks for public receipt classification and live status text."""
import importlib.util
import pathlib
import sys
import types
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE = ROOT / "relay" / "cf200_live_status.py"

class StatusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # GUI import is optional in minimal CI images; test pure functions without opening windows.
        try:
            spec = importlib.util.spec_from_file_location("cf200_live_status", MODULE)
            cls.mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.mod)
        except ImportError as exc:
            raise unittest.SkipTest(str(exc))

    def test_matching_receipt_never_claims_scheduler(self):
        receipt = {"id": self.mod.PROBE_ID, "request_sha256": self.mod.PROBE_DIGEST,
                   "status": "completed", "result": {"pong": True, "protocol": 1}}
        text = self.mod.probe_summary(lambda url: receipt)
        self.assertIn("matching completed ping", text)
        self.assertIn("UNVERIFIED", text)

    def test_mismatched_digest_rejected(self):
        receipt = {"id": self.mod.PROBE_ID, "request_sha256": "bad",
                   "status": "completed", "result": {"pong": True, "protocol": 1}}
        self.assertIn("mismatched", self.mod.probe_summary(lambda url: receipt))

    def test_unavailable_receipt_is_not_success(self):
        def unavailable(url):
            raise TimeoutError()
        self.assertIn("unavailable", self.mod.probe_summary(unavailable))

    def test_snapshot_separates_public_commit_and_hp(self):
        registry = {"completed": 52, "target": 200, "status": "WORK_IN_PROGRESS"}
        commits = [{"sha": "a" * 40, "commit": {"message": "test commit"}}]
        with patch.object(self.mod, "fetch_json", side_effect=[registry, commits]), patch.object(
            self.mod, "probe_summary", return_value="HP ping receipt: unavailable"):
            output = self.mod.snapshot()
        self.assertIn("52 / 200", output)
        self.assertIn("NOT VERIFIED", output)
        self.assertIn("does not prove CI passed", output)

if __name__ == "__main__":
    unittest.main()
