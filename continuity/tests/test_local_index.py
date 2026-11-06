"""Offline private continuity regression tests; all content synthetic and disposable."""
import contextlib
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import zipfile

from continuity import local_index as c


class LocalContinuityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.state = self.root / "private" / "continuity"
        self.conn = c.open_db(self.state)
        self.addCleanup(self.conn.close)

    def file(self, name, text):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def test_sha_dedup_retains_two_original_source_origins(self):
        first = self.file("a/one.md", "Synthetic historical text")
        second = self.file("b/two.md", "Synthetic historical text")
        a = c.ingest(self.conn, self.state, first, "memo", "archive 1")
        b = c.ingest(self.conn, self.state, second, "memo", "archive 2")
        self.assertEqual(a["source_id"], b["source_id"])
        self.assertTrue(b["duplicate"])
        self.assertEqual(c.audit(self.conn)["sources"], 1)
        self.assertEqual(c.audit(self.conn)["origins"], 2)
        self.assertEqual(Path(a["private_original"]).read_text(), "Synthetic historical text")

    def test_repeated_exact_import_does_not_duplicate_events(self):
        src = self.file("memo.md", "A test for stable source IDs")
        for i in range(3):
            c.ingest(self.conn, self.state, src, "memo")
        self.assertEqual(c.audit(self.conn)["events"], 1)
        self.assertEqual(c.audit(self.conn)["origins"], 1)

    def test_chatgpt_export_index_private_search_reimport_idempotent(self):
        export = [{"id": "conversation-1", "title": "Book Machine",
                   "create_time": 123, "mapping": {
                       "m1": {"message": {"id": "m1", "author": {"role": "user"},
                                          "content": {"parts": ["Book Machine creates explorable worlds."]}}},
                       "m2": {"message": {"id": "m2", "author": {"role": "assistant"},
                                          "content": {"parts": ["Proof is still required."]}}},
                       "m3": {"message": {"id": "m3", "content": {"parts": [{"image": "omitted"}]}}}
                   }}]
        path = self.file("conversations.json", json.dumps(export))
        first = c.import_conversations(self.conn, self.state, path)
        again = c.import_conversations(self.conn, self.state, path)
        self.assertEqual((first["conversations"], first["messages"]), (1, 2))
        self.assertFalse(again["reindexed"])
        hits = c.search(self.conn, "explorable worlds")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["conversation_id"], "conversation-1")
        self.assertEqual(hits[0]["role"], "user")
        self.assertTrue(c.audit(self.conn, full_hash=True)["chain_valid"])

    def test_chatgpt_export_from_zip_not_extracted_and_searchable(self):
        path = self.root / "export.zip"
        with zipfile.ZipFile(path, "w") as z:
            z.writestr("nested/conversations.json", json.dumps([
                {"title": "Sidecar Test", "mapping": {
                    "key": {"message": {"content": {"parts": ["Domino Sidecar saved"]}}}}
                }
            ]))
            z.writestr("../../escape.txt", "safe: not extracted")
        out = c.import_conversations(self.conn, self.state, path)
        self.assertEqual(out["messages"], 1)
        self.assertEqual(len(c.search(self.conn, "Domino Sidecar")), 1)
        self.assertFalse((self.root.parent / "escape.txt").exists())
        self.assertEqual(c.audit(self.conn)["sources"], 1)

    def test_missing_conversation_export_keeps_original_and_reports_error(self):
        src = self.root / "invalid.zip"
        with zipfile.ZipFile(src, "w") as z:
            z.writestr("fake.json", "[]")
        with self.assertRaisesRegex(ValueError, "zip_requires_one_conversations_json"):
            c.import_conversations(self.conn, self.state, src)
        self.assertEqual(c.audit(self.conn)["sources"], 1)

    def test_invalid_json_marks_partial_but_does_not_invent_completion(self):
        src = self.file("bad.json", '[{"id":"ok","mapping":{}}, MALFORMED]')
        with self.assertRaises(ValueError):
            c.import_conversations(self.conn, self.state, src)
        self.assertEqual(self.conn.execute("SELECT status FROM import_status").fetchone()[0], "partial")
        self.assertEqual(c.audit(self.conn)["conversations"], 1)
        self.assertEqual(len([r for r in self.conn.execute("SELECT kind FROM events")
                              if r[0] == "conversation_export_indexed"]), 0)

    def test_manual_project_preserves_distinct_relationships(self):
        src = c.ingest(self.conn, self.state, self.file("book.txt", "A tactile world"), "source")
        c.add_project(self.conn, "CF-BOOK", "Book Machine", "Explorable book worlds")
        c.add_project(self.conn, "CF-BOOK-TACTILE", "Tactile Prototype", "Physical interface", "CF-BOOK")
        link = c.link_source(self.conn, "CF-BOOK-TACTILE", src["source_id"], "primary")
        self.assertTrue(link["linked"])
        self.assertFalse(c.link_source(self.conn, "CF-BOOK-TACTILE", src["source_id"], "primary")["linked"])
        self.assertEqual(c.audit(self.conn)["projects"], 2)
        self.assertEqual(c.audit(self.conn)["project_source_links"], 1)
        self.assertEqual(self.conn.execute("SELECT parent_id FROM projects WHERE id='CF-BOOK-TACTILE'").fetchone()[0], "CF-BOOK")

    def test_unknown_parent_or_source_rejected_without_event(self):
        with self.assertRaisesRegex(ValueError, "unknown_parent_project"):
            c.add_project(self.conn, "CF-BOOK", "Book Machine", "Explorable worlds", "UNKNOWN")
        c.add_project(self.conn, "CF-BOOK", "Book Machine", "Explorable worlds")
        before = c.audit(self.conn)["events"]
        with self.assertRaisesRegex(ValueError, "unknown_source"):
            c.link_source(self.conn, "CF-BOOK", "sha256:" + "0" * 64, "primary")
        self.assertEqual(c.audit(self.conn)["events"], before)

    def test_conflicting_claims_open_review_without_choosing_truth(self):
        a = c.ingest(self.conn, self.state, self.file("a.txt", "Option A"), "original")
        b = c.ingest(self.conn, self.state, self.file("b.txt", "Option B"), "original")
        c.add_project(self.conn, "CF-BOOK", "Book Machine", "Explorable books")
        one = c.add_claim(self.conn, "CF-BOOK", "current_state", "prototype", a["source_id"])
        two = c.add_claim(self.conn, "CF-BOOK", "current_state", "idea", b["source_id"])
        self.assertTrue(one["created"])
        self.assertEqual(len(two["open_conflicts"]), 1)
        self.assertEqual(c.audit(self.conn)["open_conflicts"], 1)
        self.assertEqual(set(row[0] for row in self.conn.execute("SELECT status FROM claims")), {"proposed"})
        self.assertFalse(c.add_claim(self.conn, "CF-BOOK", "current_state", "idea", b["source_id"])["created"])
        self.assertEqual(c.audit(self.conn)["open_conflicts"], 1)

    def test_events_are_append_only_and_chain_verifies(self):
        c.add_project(self.conn, "CF-BOOK", "Book Machine", "Explorable books")
        self.assertTrue(c.audit(self.conn)["chain_valid"])
        with self.assertRaisesRegex(sqlite3.IntegrityError, "append_only_events"):
            self.conn.execute("UPDATE events SET kind='overwrite'")
        with self.assertRaisesRegex(sqlite3.IntegrityError, "append_only_events"):
            self.conn.execute("DELETE FROM events")
        self.assertTrue(c.audit(self.conn)["chain_valid"])

    def test_hash_integrity_detects_tampered_preserved_original(self):
        s = c.ingest(self.conn,self.state,self.file("original.txt", "Unmodified record"),"original")
        Path(s["private_original"]).write_text("CHANGED",encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "original_hash_changed"):
            c.audit(self.conn,full_hash=True)

    def test_export_array_parser_rejects_nonarray_and_trailing_bad_data(self):
        with self.assertRaisesRegex(ValueError,"expected_chatgpt_conversation_array"):
            list(c.iter_json_array(io.StringIO('{}')))
        with self.assertRaisesRegex(ValueError,"trailing_json_data"):
            list(c.iter_json_array(io.StringIO('[] XXX')))
        with self.assertRaisesRegex(ValueError,"trailing_comma"):
            list(c.iter_json_array(io.StringIO('[{},]')))

    def test_source_state_path_rejects_public_source_tree(self):
        with self.assertRaisesRegex(ValueError,"private_state_must_be_outside_public_repo"):
            c.safe_state(c.ROOT / "example_private_state")

    def test_search_wildcards_are_literal_and_query_only_matches_actual_content(self):
        path = self.file("conversations.json", json.dumps([{"title":"test","mapping":{"x":{"message":{"content":{"parts":["100% true, 0_false"]}}}}}]))
        c.import_conversations(self.conn,self.state,path)
        self.assertEqual(len(c.search(self.conn, "100%")),1)
        self.assertEqual(len(c.search(self.conn, "100_")),0)
        self.assertEqual(len(c.search(self.conn, "0_false")),1)


if __name__ == "__main__":
    unittest.main()