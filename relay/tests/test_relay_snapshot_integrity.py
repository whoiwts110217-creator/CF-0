"""Pure in-memory regression fixtures; no private messages, network or disk I/O."""
import pathlib
import sys
import unittest
from unittest.mock import patch
import io

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import relay_snapshot_integrity as check


def make(ident="CF0-RELAY-0001", uid="uid-1", tag="worker-a",
         ack=None, inline=False, closed=True):
    out = (f"BEGIN {ident}\nMESSAGE_ID: {ident}\nMESSAGE_UID: {uid}\n"
           f"DOCK_TAG: {tag}\n")
    if ack:
        out += f"ACK_BOOTSTRAP: {ack}\n"
    if closed:
        out += (f"BODY: completed. END {ident}\n" if inline
                else f"END {ident}\n")
    return out


class SnapshotAuditTests(unittest.TestCase):
    def test_one_entry(self):
        self.assertEqual(check.audit(make())["entries"], 1)

    def test_separate_end(self):
        self.assertEqual(check.audit(make())["unclosed"], [])

    def test_inline_legacy_end(self):
        self.assertEqual(check.audit(make(inline=True))["unclosed"], [])

    def test_missing_end(self):
        self.assertEqual(check.audit(make(closed=False))["unclosed"],
                         ["CF0-RELAY-0001"])

    def test_wrong_end(self):
        x = make().replace("END CF0-RELAY-0001", "END CF0-RELAY-0099")
        self.assertEqual(check.audit(x)["wrong_end"], ["CF0-RELAY-0001"])

    def test_unique_uid(self):
        x = make() + make("CF0-RELAY-0002", "uid-2")
        self.assertEqual(check.audit(x)["duplicate_uid"], [])

    def test_duplicate_uid(self):
        x = make() + make("CF0-RELAY-0002", "uid-1")
        self.assertEqual(check.audit(x)["duplicate_uid"], ["uid-1"])

    def test_duplicate_numeric_message_id(self):
        x = make() + make(uid="uid-2")
        self.assertEqual(check.audit(x)["duplicate_message_id"],
                         ["CF0-RELAY-0001"])

    def test_duplicate_begin(self):
        x = make() + make(uid="uid-2")
        self.assertEqual(check.audit(x)["duplicate_begin"],
                         ["CF0-RELAY-0001"])

    def test_missing_uid(self):
        x = make().replace("MESSAGE_UID: uid-1\n", "")
        self.assertEqual(check.audit(x)["missing_uid"], ["CF0-RELAY-0001"])

    def test_per_worker_id(self):
        x = make("CF0-RELAY-WORKER-A-001")
        self.assertEqual(check.audit(x)["unclosed"], [])

    def test_crlf(self):
        self.assertEqual(check.audit(make().replace("\n", "\r\n"))["entries"], 1)

    def test_orphan_end(self):
        self.assertEqual(check.audit("END CF0-RELAY-0001\n")["entries"], 0)

    def test_no_embedded_begin(self):
        x = "BODY: BEGIN CF0-RELAY-OLD\n" + make()
        self.assertEqual(check.audit(x)["entries"], 1)

    def test_reply_to_end_is_not_close(self):
        x = make(closed=False) + "REPLY_TO: END CF0-RELAY-0001\n"
        self.assertEqual(check.audit(x)["unclosed"], ["CF0-RELAY-0001"])

    def test_subject_end_is_not_close(self):
        x = make(closed=False) + "SUBJECT: END CF0-RELAY-0001\n"
        self.assertEqual(check.audit(x)["unclosed"], ["CF0-RELAY-0001"])

    def test_reply_to_metadata_followed_by_real_end(self):
        x = make(closed=False) + ("REPLY_TO: END CF0-RELAY-0001\n"
                                  "END CF0-RELAY-0001\n")
        self.assertEqual(check.audit(x)["unclosed"], [])

    def test_new_begin_leaves_previous_unclosed(self):
        x = make(closed=False) + make("CF0-RELAY-WORKER-B-002", "uid-2")
        self.assertEqual(check.audit(x)["unclosed"], ["CF0-RELAY-0001"])

    def test_bootstrap_missing_when_not_provided(self):
        self.assertFalse(check.audit(make())["bootstrap_seen"])

    def test_bootstrap_ack_post_rollout(self):
        marker = "example-bootstrap-announcement"
        x = (make("CF0-RELAY-BOOT-001", marker, "steward")
             + make("CF0-RELAY-A-001", "uid-a", "worker-a")
             + make("CF0-RELAY-B-001", "uid-b", "worker-b", "v1"))
        r = check.audit(x, bootstrap_uid=marker)
        self.assertTrue(r["bootstrap_seen"])
        self.assertEqual(r["post_rollout_tags"], 2)
        self.assertEqual(r["post_rollout_ack_tags"], 1)
        self.assertEqual(r["post_rollout_missing_ack_tags"], ["worker-a"])

    def test_strict_legacy_duplicate_id_exit(self):
        sample = make() + make(uid="uid-2")
        with patch.object(sys, "stdin", io.StringIO(sample)), patch.object(sys, "stdout", io.StringIO()):
            self.assertEqual(check.main(["-", "--strict"]), 2)
        with patch.object(sys, "stdin", io.StringIO(sample)), patch.object(sys, "stdout", io.StringIO()):
            self.assertEqual(check.main(["-"]), 0)

    def test_strict_missing_uid_exit(self):
        sample = make().replace("MESSAGE_UID: uid-1\n", "")
        with patch.object(sys, "stdin", io.StringIO(sample)), patch.object(sys, "stdout", io.StringIO()):
            self.assertEqual(check.main(["-", "--strict"]), 2)
        with patch.object(sys, "stdin", io.StringIO(sample)), patch.object(sys, "stdout", io.StringIO()):
            self.assertEqual(check.main(["-"]), 0)

    def test_strict_valid_exit(self):
        with patch.object(sys, "stdin", io.StringIO(make())), patch.object(sys, "stdout", io.StringIO()):
            self.assertEqual(check.main(["-", "--strict"]), 0)

    def test_no_private_data_in_fixture(self):
        self.assertNotIn("https://docs.google.com", make())
        self.assertNotIn("password", make())

if __name__ == "__main__":
    unittest.main()
