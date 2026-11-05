# cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
"""Caveman Focus HP Bridge local tests — no external network."""
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cf_hp_bridge import BridgeError, GitHubMailbox, LocalLedger, make_job, parse_job, run_once, demo, execute_job

class FakeMailbox:
    def __init__(self, job, private=True):
        self.job = job
        self.private = private
        self.out = []
    def require_private(self):
        if not self.private: raise BridgeError('repository_must_be_private')
    def list_jobs(self): return [self.job['id']+'.json']
    def load_job(self, fn): return self.job
    def publish(self, jid, reply): self.out.append((jid,reply))

class BridgeTests(unittest.TestCase):
    def test_synthetic_local_demo(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertTrue(demo(Path(td))['pass'])

    def test_ping_and_repeated_receipt(self):
        job=make_job('ping')
        with tempfile.TemporaryDirectory() as td:
            mailbox=FakeMailbox(job)
            ledger=LocalLedger(Path(td)/'l.sqlite3')
            one=run_once(mailbox,ledger)
            two=run_once(mailbox,ledger)
            self.assertEqual((one['executed'],two['executed']), (1,0))
            self.assertEqual((one['replied'],two['replied']), (1,1))
            self.assertEqual(mailbox.out[0][1]['result']['ping'],'pong')
            self.assertEqual(mailbox.out[0],mailbox.out[1])

    def test_private_repository_required(self):
        job=make_job('ping'); mb=FakeMailbox(job,False)
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(BridgeError,'private'):
                run_once(mb,LocalLedger(Path(td)/'l.sqlite3'))

    def test_unknown_actions_and_params_rejected(self):
        job=make_job('ping')
        for field,value in [('action','shell'),('params',{'cmd':'whoami'}),('version',True)]:
            bad=dict(job);bad[field]=value
            with self.assertRaises(BridgeError):parse_job(bad,job['id']+'.json')

    def test_renamed_id_rejected(self):
        job=make_job('ping')
        with self.assertRaises(BridgeError):parse_job(job,str(uuid.uuid4())+'.json')

    def test_expired_rejected(self):
        job=make_job('ping',now=1000)
        with self.assertRaises(BridgeError):parse_job(job,job['id']+'.json',now=10000)

    def test_future_job_rejected(self):
        job=make_job('ping',now=5000)
        with self.assertRaises(BridgeError):parse_job(job,job['id']+'.json',now=1000)

    def test_sidecar_is_read_only_by_default(self):
        job=make_job('sidecar_verify')
        self.assertEqual(execute_job(job,None), {'verification':'not_configured'})

    def test_id_reuse_with_different_payload_rejected(self):
        job=make_job('ping')
        with tempfile.TemporaryDirectory() as td:
            mb=FakeMailbox(job);ledger=LocalLedger(Path(td)/'l.sqlite3')
            run_once(mb,ledger)
            modified=dict(job);modified['issued_at']-=1;mb.job=modified
            out=run_once(mb,ledger)
            self.assertIn('identity_reused_with_different_payload',str(out['errors']))

    def test_no_duplicate_when_publication_failed(self):
        job=make_job('ping')
        class FailPublish(FakeMailbox):
            def publish(self,*args): raise BridgeError('test_publish_failed')
        with tempfile.TemporaryDirectory() as td:
            mb=FailPublish(job);ledger=LocalLedger(Path(td)/'l.sqlite3')
            first=run_once(mb,ledger);second=run_once(mb,ledger)
            self.assertEqual((first['executed'],second['executed']),(1,0))
            self.assertEqual(first['errors'][0]['error'],'test_publish_failed')

    def test_token_is_required_to_construct_mailbox(self):
        with self.assertRaises(BridgeError):GitHubMailbox('owner/repo','')

if __name__=='__main__':unittest.main()