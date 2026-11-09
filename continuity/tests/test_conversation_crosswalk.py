import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from continuity.conversation_crosswalk import validate_map,compare,open_readonly_db,verify_secondary_review

SHA='a'*64
ID='CF-CORE'
MAP={'schema':'cf0.private_conversation_idea_merge.v2','continuity_id':'test','original_atlas_items':[{'id':ID}],
'conversation_provenance_crosswalk':[{'source_unit_id':'U-1','conversation_title':'Stone and Rock','source_sha256':SHA,
'original_chat_id':None,'owner_accepted':False,'related_project_ids':[ID],
'review_summary':'Nature stared at the carpenter with a stone hammer during the discovery.'}]}

def synthetic(root, include=True,duplicate=False,partial=False):
    p=root/'continuity.sqlite3'
    db=sqlite3.connect(p)
    db.executescript('''CREATE TABLE conversations(source_id text,conversation_id text,title text);
      CREATE TABLE messages(source_id text,conversation_id text,body text,role text,message_id text,sent_at text);
      CREATE TABLE import_status(source_id text,status text);''')
    if include:
        db.execute('insert into import_status values (?,?)',('source-1','partial' if partial else 'complete'))
        db.execute('insert into conversations values (?,?,?)',('source-1','original-123','Stone and Rock'))
        db.execute('insert into messages values (?,?,?,?,?,?)',('source-1','original-123','The carpenter met the stone hammer and nature after the discovery.','user','m1','0'))
        if duplicate:
            db.execute('insert into conversations values (?,?,?)',('source-1','original-456','Stone and Rock'))
    db.commit();db.close();return p

class CrosswalkTests(unittest.TestCase):
    def test_no_export_never_promotes_secondary_summary(self):
        r=compare(MAP,None)
        self.assertEqual(r['counts']['original_export_conversations_available'],0)
        self.assertEqual(r['matches'][0]['match_status'],'no_primary_title_match')
        self.assertFalse(r['matches'][0]['merge_approved'])
    def test_read_only_original_candidate_still_requires_review(self):
        with tempfile.TemporaryDirectory() as d:
            path=synthetic(Path(d))
            with open_readonly_db(path) as db:
                r=compare(MAP,db)
                self.assertEqual(r['matches'][0]['match_status'],'candidate_requires_original_review')
                self.assertEqual(r['matches'][0]['candidate_originals'][0]['conversation_id'],'original-123')
                self.assertFalse(r['matches'][0]['merge_approved'])
                self.assertEqual(db.execute('select count(*) from conversations').fetchone()[0],1)
    def test_duplicate_title_is_ambiguous(self):
        with tempfile.TemporaryDirectory() as d:
            with open_readonly_db(synthetic(Path(d),duplicate=True)) as db:
                r=compare(MAP,db)
            self.assertEqual(r['matches'][0]['match_status'],'ambiguous_multiple_originals')
            self.assertEqual(len(r['matches'][0]['candidate_originals']),2)
    def test_partial_import_never_promoted(self):
        with tempfile.TemporaryDirectory() as d:
            with open_readonly_db(synthetic(Path(d),partial=True)) as db:r=compare(MAP,db)
            self.assertEqual(r['matches'][0]['match_status'],'no_primary_title_match')
    def test_title_without_content_is_not_confirmed(self):
        with tempfile.TemporaryDirectory() as d:
            p=synthetic(Path(d));db=sqlite3.connect(p)
            db.execute('update messages set body=?',('Generic hello',));db.commit();db.close()
            with open_readonly_db(p) as db:r=compare(MAP,db)
            self.assertEqual(r['matches'][0]['match_status'],'title_only_unverified')
    def test_bad_project_id_not_silently_accepted(self):
        data=json.loads(json.dumps(MAP));data['conversation_provenance_crosswalk'][0]['related_project_ids']=['NOT-IN-ATLAS']
        with self.assertRaisesRegex(ValueError,'unknown_project_identity'):validate_map(data)
    def test_imported_preapproved_links_forbidden(self):
        data=json.loads(json.dumps(MAP));data['conversation_provenance_crosswalk'][0]['owner_accepted']=True
        with self.assertRaisesRegex(ValueError,'unresolved_secondary_links_only'):validate_map(data)
    def test_secondary_source_digest_checked_if_supplied(self):
        with tempfile.TemporaryDirectory() as d:
            file=Path(d)/'review.md';file.write_text('private review')
            import hashlib
            source=json.loads(json.dumps(MAP))
            source['conversation_provenance_crosswalk'][0]['source_sha256']=hashlib.sha256(file.read_bytes()).hexdigest()
            self.assertTrue(verify_secondary_review(source,file)['sha256_verified'])
            file.write_text('tampered')
            with self.assertRaisesRegex(ValueError,'digest_mismatch'):verify_secondary_review(source,file)
    def test_missing_db_refuses_to_create_it(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'nonexistent.sqlite3'
            with self.assertRaises(FileNotFoundError):open_readonly_db(p)
            self.assertFalse(p.exists())

if __name__=='__main__':unittest.main()