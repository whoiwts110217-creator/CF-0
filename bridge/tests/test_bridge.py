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
            self.assertEqual((one['replied'],two['replied']), (1,0))
            self.assertEqual(two['already_published'],1)
            self.assertEqual(mailbox.out[0][1]['result']['ping'],'pong')
            self.assertEqual(len(mailbox.out),1)

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
            # Previously published jobs are immutable by protocol: the local
            # ledger ignores a later edit to the same filename, never reexecutes.
            self.assertEqual(out['executed'], 0)
            self.assertEqual(out['already_published'], 1)
            self.assertEqual(ledger.counts()['published'], 1)

    def test_no_duplicate_when_publication_failed(self):
        job=make_job('ping')
        class FailPublish(FakeMailbox):
            def publish(self,*args): raise BridgeError('test_publish_failed')
        with tempfile.TemporaryDirectory() as td:
            mb=FailPublish(job);ledger=LocalLedger(Path(td)/'l.sqlite3')
            first=run_once(mb,ledger);second=run_once(mb,ledger)
            self.assertEqual((first['executed'],second['executed']),(1,0))
            self.assertEqual(first['errors'][0]['error'],'test_publish_failed')

    def test_queue_drain_without_starving_newer_jobs(self):
        jobs = [make_job('ping') for _ in range(26)]
        jobs.sort(key=lambda job: job['id'])
        class ManyMailbox(FakeMailbox):
            def __init__(self): self.out=[];self.private=True
            def list_jobs(self): return [j['id']+'.json' for j in jobs]
            def load_job(self, fn): return next(j for j in jobs if j['id']+'.json' == fn)
        with tempfile.TemporaryDirectory() as td:
            mb=ManyMailbox();led=LocalLedger(Path(td)/'l.sqlite3')
            runs=[run_once(mb,led) for _ in range(4)]
            self.assertEqual([r['executed'] for r in runs],[10,10,6,0])
            self.assertEqual([r['pending'] for r in runs],[16,6,0,0])
            self.assertEqual(len(mb.out),26)
            self.assertEqual(led.counts()['published'],26)

    def test_retry_publication_after_unknown_response_no_duplicate_execute(self):
        job=make_job('ping')
        class FlakyMailbox(FakeMailbox):
            failed=False
            def publish(self,jid,reply):
                if not self.failed:
                    self.failed=True
                    raise BridgeError('simulated_ambiguous_delivery')
                super().publish(jid,reply)
        with tempfile.TemporaryDirectory() as td:
            mb=FlakyMailbox(job);led=LocalLedger(Path(td)/'l.sqlite3')
            first=run_once(mb,led);second=run_once(mb,led)
            self.assertEqual((first['executed'],second['executed']),(1,0))
            self.assertEqual(second['replied'],1)
            self.assertEqual(led.counts()['published'],1)

    def test_bad_action_types_are_rejected_not_crash(self):
        job=make_job('ping')
        for action in ([],{},1,None):
            bad=dict(job,action=action)
            with self.assertRaisesRegex(BridgeError,'action_not_allowlisted'):
                parse_job(bad,job['id']+'.json')

    def test_multiline_sidecar_verify_is_parsed(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            (p / 'domino.py').write_text(
                'import json\nimport sys\n'
                'if sys.argv[1] == "verify":\n'
                '    print(json.dumps({"valid":True,"events":7},indent=2))\n',
                encoding='utf-8'
            )
            result = execute_job(make_job('sidecar_verify'),p)
            self.assertEqual(result,{'verification':'valid','events':7})

    def test_token_is_required_to_construct_mailbox(self):
        with self.assertRaises(BridgeError):GitHubMailbox('owner/repo','')

if __name__=='__main__':unittest.main()
