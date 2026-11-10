"""Synthetic-only tests for the existing local ChatGPT index → Spider bridge."""
from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest

from continuity import local_index
from continuity import spider_action_export as spider

CID = "12345678-abcd-4def-9876-123456789abc"


class SpiderPrivateBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="cf-spider-private-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.state = self.root / "private-state"
        self.conn = local_index.open_db(self.state)

    def tearDown(self):
        self.conn.close()

    def _import(self, name="chat-export-1.json", *, extra=False, cid=CID):
        messages = [
            ("m1", "user", "I need to install the proper browser extension before testing."),
            ("m2", "assistant", "ACTION REQUIRED [AUTO-08]: Run one signed-in browser test and verify STOP."),
            ("m3", "user", "My password is hidden. I need to reset my password."),
            ("m4", "user", "continue"),
            ("m5", "assistant", "Here are some example projects for hypothetical users."),
            ("m6", "user", "Remind me to review the grant status."),
        ]
        if extra:
            messages.append(("m7", "assistant", "Nothing else required."))
        raw = [{"id": cid, "title": "Private testing conversation",
                "mapping": {
                    k: {"message": {"id": k, "author": {"role": role},
                                    "content": {"parts": [body]}, "create_time": 1780000000 + i}}
                    for i, (k, role, body) in enumerate(messages)
                }}]
        path = self.root / name
        path.write_text(json.dumps(raw), encoding="utf-8")
        result = local_index.import_conversations(self.conn, self.state, path)
        return result["source_id"]

    def test_action_candidates_from_original_index_have_private_message_provenance(self):
        self._import()
        manifest, summary = spider.read_private_index(self.state)
        self.assertEqual(manifest["schema"], "cf0.spider.action_manifest.v1")
        self.assertEqual(summary["candidates_returned"], 3)
        self.assertEqual(summary["messages_scanned"], 6)
        self.assertTrue(summary["heuristic_only"])
        self.assertTrue(summary["private_index_read_only"])
        self.assertTrue(all(x["zone"] == "conditional" and x["review_required"] for x in manifest["actions"]))
        self.assertTrue(all(x["source_ref"].startswith("indexed-chat:sha256:") for x in manifest["actions"]))
        self.assertTrue(all(x["project_id"] == "UNRESOLVED" for x in manifest["actions"]))
        self.assertTrue(all(x["task_ids"] == [] for x in manifest["actions"]))
        self.assertTrue(all(x["link"] == f"https://chatgpt.com/c/{CID}" for x in manifest["actions"]))
        self.assertFalse(any("password" in x["action"].lower() for x in manifest["actions"]))

    def test_repeated_chat_in_two_distinct_archives_merges_same_message_id_but_keeps_origins(self):
        sid1 = self._import()
        sid2 = self._import("chat-export-2.json", extra=True)
        self.assertNotEqual(sid1, sid2)
        manifest, summary = spider.read_private_index(self.state)
        self.assertEqual(summary["candidates_returned"], 3)
        self.assertTrue(all(len(x["source_refs"]) == 2 for x in manifest["actions"]))
        self.assertTrue(all(x["source_ref"] in x["source_refs"] for x in manifest["actions"]))
        self.assertTrue(all(x["id"].startswith("LOCAL-") for x in manifest["actions"]))

    def test_non_uuid_conversation_gets_private_pointer_without_invented_web_url(self):
        self._import(cid="source-ordinal:0")
        manifest, _ = spider.read_private_index(self.state)
        self.assertTrue(manifest["actions"])
        self.assertTrue(all(not x["link"] and not x["source"] for x in manifest["actions"]))
        self.assertTrue(all("source-ordinal:0" in x["source_ref"] for x in manifest["actions"]))

    def test_partial_index_not_treated_as_complete_evidence(self):
        sid = self._import()
        self.conn.execute("UPDATE import_status SET status='partial' WHERE source_id=?", (sid,))
        self.conn.commit()
        manifest, summary = spider.read_private_index(self.state)
        self.assertEqual(manifest["actions"], [])
        self.assertEqual(summary["candidates_returned"], 0)

    def test_read_only_cli_writes_private_manifest_without_printing_private_text(self):
        self._import()
        dest = self.root / "PRIVATE-Spider-Candidates.json"
        before = self.conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(spider.main(["--state-dir", str(self.state), "--output", str(dest)]), 0)
        self.assertTrue(dest.is_file())
        self.assertNotIn("browser extension", output.getvalue())
        self.assertNotIn("Private testing conversation", output.getvalue())
        self.assertTrue(json.loads(output.getvalue())["private_manifest_written"])
        self.assertEqual(before, self.conn.execute("SELECT COUNT(*) FROM events").fetchone()[0])
        with self.assertRaisesRegex(ValueError, "refuse_to_overwrite"):
            spider.write_private_manifest(dest, {})
        if os.name != "nt":
            self.assertEqual(stat.S_IMODE(dest.stat().st_mode), 0o600)

    def test_output_inside_public_repo_or_repo_descendant_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "manifest_output_must_be_private"):
            spider.write_private_manifest(spider.ROOT / "INVALID-SPIDER-EXPORT.json", {})
        with self.assertRaisesRegex(ValueError, "manifest_output_must_be_private"):
            spider.write_private_manifest(spider.ROOT / "link-vault" / "INVALID-SPIDER-EXPORT.json", {})

    def test_invalid_sources_and_unsafe_candidates_fail_closed(self):
        self.assertEqual(spider.candidate_text("Continue", "user"), [])
        self.assertEqual(spider.candidate_text("ACTION REQUIRED: My API key is secret.", "assistant"), [])
        self.assertEqual(spider.candidate_text("Example: I need to gamble tomorrow", "user"), [])
        with self.assertRaisesRegex(ValueError, "bad_index_source"):
            spider.private_pointer("not_sha", "conversation", "msg")
        with self.assertRaisesRegex(ValueError, "bad_private_message_pointer"):
            spider.private_pointer("sha256:"+"a"*64, "../escape", "m")
        with self.assertRaisesRegex(ValueError, "existing_private_index_required"):
            spider.read_private_index(self.root / "missing")

    def test_limit_is_explicit_and_omitted_count_not_silent(self):
        self._import()
        manifest, summary = spider.read_private_index(self.state, limit=1)
        self.assertEqual(len(manifest["actions"]), 1)
        self.assertEqual(summary["candidates_omitted"], 2)
        with self.assertRaisesRegex(ValueError, "limit_must_be"):
            spider.read_private_index(self.state, limit=101)


if __name__ == "__main__":
    unittest.main()
