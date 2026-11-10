"""CF-MESH-001 source-only handoff tests; no live chats or user data."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from continuity.public_mesh_handoff import (
    ROOT, GRAPH_PATH, LEDGER_PATH, HandoffError, git_blob_sha,
    digest_event, new_event, rehearsal, validate_events,
)

GRAPH = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
HEAD = "a" * 40


def append(raw="", *, worker="A", topic="CF-MESH-001", kind="handoff", consumes=None):
    return new_event(raw, GRAPH, kind=kind, worker=worker, topic=topic,
                     read_main_commit=HEAD, consumes=consumes)


def mutate_line(raw, index, function):
    lines = raw.splitlines()
    ev = json.loads(lines[index])
    function(ev)
    ev["event_sha256"] = digest_event(ev)
    lines[index] = json.dumps(ev, sort_keys=True, separators=(",", ":"))
    return "\n".join(lines) + "\n"


class HandoffTests(unittest.TestCase):
    def test_git_object_sha_matches_actual_file_graph(self):
        actual = git_blob_sha(GRAPH_PATH.read_bytes())
        self.assertRegex(actual, r"^[0-9a-f]{40}$")
        self.assertEqual(git_blob_sha(b"hello"), "b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0")

    def test_existing_ledger_and_rehearsal_validate_without_live_claim(self):
        raw = LEDGER_PATH.read_text(encoding="utf-8") if LEDGER_PATH.exists() else ""
        out = validate_events(raw, GRAPH)
        self.assertFalse(out["live_three_chat_acceptance"])
        sim = rehearsal(GRAPH)
        self.assertTrue(sim["synthetic_only"])
        self.assertEqual(sim["events"], 4)
        self.assertEqual(sim["handoffs"], 2)
        self.assertEqual(sim["readbacks"], 2)
        self.assertFalse(sim["provider_origin_verified"])

    def test_handoff_preserves_topic_source_and_master_order(self):
        a = append()
        self.assertEqual(a["event"]["active_topic_id"], "CF-MESH-001")
        self.assertEqual(a["event"]["topic_source_path"],
                         "docs/PUBLIC_THREE_CHAT_CONTINUITY_MESH.md")
        self.assertEqual(len(a["event"]["read_master_blob_shas"]), 3)
        self.assertEqual(a["event"]["read_graph_blob_sha1"],
                         git_blob_sha(GRAPH_PATH.read_bytes()))
        self.assertFalse(a["event"]["provider_origin_verified"])
        self.assertEqual(validate_events(a["proposed_ledger"], GRAPH)["events"], 1)

    def test_independent_label_readback_is_structurally_valid_not_proof(self):
        a = append()
        ack = append(a["proposed_ledger"], worker="B", kind="readback",
                     consumes=a["event"]["event_sha256"])
        checked = validate_events(ack["proposed_ledger"], GRAPH)
        self.assertEqual(checked["readbacks"], 1)
        self.assertFalse(checked["live_three_chat_acceptance"])

    def test_same_worker_cannot_claim_cross_worker_readback(self):
        a = append()
        with self.assertRaisesRegex(HandoffError, "self_readback"):
            append(a["proposed_ledger"], worker="A", kind="readback",
                   consumes=a["event"]["event_sha256"])

    def test_cannot_acknowledge_missing_or_changed_digest(self):
        a = append()
        for ref in ("b" * 64, None, "not-a-sha"):
            with self.subTest(ref=ref), self.assertRaises(HandoffError):
                append(a["proposed_ledger"], worker="B", kind="readback",
                       consumes=ref)

    def test_wrong_topic_cannot_acknowledge(self):
        a = append()
        with self.assertRaisesRegex(HandoffError, "readback_topic_mismatch"):
            append(a["proposed_ledger"], worker="B", topic="AUTO-08",
                   kind="readback", consumes=a["event"]["event_sha256"])

    def test_duplicate_readback_label_rejected(self):
        a = append()
        b = append(a["proposed_ledger"], worker="B", kind="readback",
                   consumes=a["event"]["event_sha256"])
        with self.assertRaisesRegex(HandoffError, "duplicate_readback_label"):
            append(b["proposed_ledger"], worker="B", kind="readback",
                   consumes=a["event"]["event_sha256"])

    def test_chain_tampering_refused(self):
        a = append()
        raw = a["proposed_ledger"]
        tampered = raw.replace("CF-MESH-001", "CF-200", 1)
        with self.assertRaisesRegex(HandoffError, "topic_source_mismatch|event_hash_mismatch"):
            validate_events(tampered, GRAPH)

    def test_changing_earlier_event_invalidates_following_parent(self):
        a = append()
        b = append(a["proposed_ledger"], worker="B")
        modified = mutate_line(b["proposed_ledger"], 0, lambda ev: ev.update(
            read_main_commit="c" * 40
        ))
        with self.assertRaisesRegex(HandoffError, "chain_parent_mismatch"):
            validate_events(modified, GRAPH)

    def test_extra_payload_and_private_text_field_rejected(self):
        a = append()
        modified = mutate_line(a["proposed_ledger"], 0, lambda ev: ev.update(
            private_chat_excerpt="SECRET"
        ))
        with self.assertRaisesRegex(HandoffError, "invalid_event_fields"):
            validate_events(modified, GRAPH)

    def test_cannot_claim_identity_or_extra_authority(self):
        a = append()
        for changes in ({"provider_origin_verified": True},
                        {"evidence_scope": "live_cross_chat"},
                        {"evidence_scope": "machine_authorized"}):
            modified = mutate_line(a["proposed_ledger"], 0,
                                   lambda ev: ev.update(changes))
            with self.subTest(change=changes), self.assertRaisesRegex(
                HandoffError, "unverified_provider_claim"
            ):
                validate_events(modified, GRAPH)

    def test_broken_parent_link_rejected(self):
        a = append()
        b = append(a["proposed_ledger"], worker="B")
        altered = mutate_line(b["proposed_ledger"], 1, lambda ev: ev.update(
            previous_event_sha256="a" * 64
        ))
        with self.assertRaisesRegex(HandoffError, "chain_parent_mismatch"):
            validate_events(altered, GRAPH)

    def test_unrelated_project_cannot_replace_context(self):
        a = append()
        modified = mutate_line(a["proposed_ledger"], 0, lambda ev: ev.update(
            related_ids=["CF-UNKNOWN"]
        ))
        with self.assertRaisesRegex(HandoffError, "unrelated_context"):
            validate_events(modified, GRAPH)

    def test_duplicate_event_id_refused(self):
        a = append()
        b = append(a["proposed_ledger"], worker="B")
        altered = mutate_line(b["proposed_ledger"], 1, lambda ev: ev.update(
            event_id="MESH-000001"
        ))
        with self.assertRaisesRegex(HandoffError, "duplicate_event_id"):
            validate_events(altered, GRAPH)

    def test_invalid_jsonl_or_extra_blank_line_fail_closed(self):
        for value in ("not json\n", "\n", '{"schema": 0}\n"):
            with self.subTest(value=value), self.assertRaises(HandoffError):
                validate_events(value, GRAPH)

    def test_missing_source_snapshot_fails_before_proposal(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(Exception):
                new_event("", GRAPH, kind="handoff", worker="A",
                          topic="CF-MESH-001", read_main_commit=HEAD,
                          root=Path(folder))

    def test_proposal_is_pure_and_does_not_write_public_ledger(self):
        graph_before = copy.deepcopy(GRAPH)
        old = LEDGER_PATH.read_bytes() if LEDGER_PATH.exists() else None
        first = append()
        self.assertTrue(first["proposed_ledger"])
        self.assertEqual(GRAPH, graph_before)
        self.assertEqual(LEDGER_PATH.read_bytes() if LEDGER_PATH.exists() else None, old)


if __name__ == "__main__":
    unittest.main()
