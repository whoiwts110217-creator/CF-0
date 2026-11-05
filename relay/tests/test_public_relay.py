# cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
import sys,pathlib,unittest,tempfile,base64,json,time
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
import cf_public_relay as r

class FakeRepo:
    def __init__(self,jobs):self.jobs=jobs;self.sent={};self.token=None
    def files(self):return sorted(j['id']+'.json' for j in self.jobs)
    def load(self,name):return next(x for x in self.jobs if x['id']+'.json'==name)
    def publish(self,jid,receipt):self.sent[jid]=receipt;return False

class Tests(unittest.TestCase):
    def test_ping(self):self.assertEqual(r.execute(r.make_job('ping'))['pong'],True)
    def test_health(self):self.assertEqual(r.execute(r.make_job('hp_status'))['worker'],'online')
    def test_sidecar_default(self):self.assertFalse(r.execute(r.make_job('sidecar_verify'))['verified'])
    def test_job_schema(self):
        x=r.make_job('ping');self.assertEqual(r.validate(x,x['id']+'.json')['id'],x['id'])
    def test_reject_arbitrary_shell(self):
        x=r.make_job('ping');x['action']='shell'
        with self.assertRaisesRegex(r.RelayError,'action_not_allowed'):r.validate(x,x['id']+'.json')
    def test_reject_extra_fields(self):
        x=r.make_job('ping');x['command']='powershell'
        with self.assertRaises(r.RelayError):r.validate(x,x['id']+'.json')
    def test_no_stale(self):
        x=r.make_job('ping',now=1000)
        with self.assertRaises(r.RelayError):r.validate(x,x['id']+'.json',now=20000)
    def test_no_future(self):
        x=r.make_job('ping',now=5000)
        with self.assertRaises(r.RelayError):r.validate(x,x['id']+'.json',now=1000)
    def test_no_identity_mismatch(self):
        x=r.make_job('ping')
        with self.assertRaises(r.RelayError):r.validate(x,r.make_job('ping')['id']+'.json')
    def test_no_arguments(self):
        x=r.make_job('ping');x['args']={'cmd':'whoami'}
        with self.assertRaises(r.RelayError):r.validate(x,x['id']+'.json')
    def test_idempotence(self):
        x=r.make_job('ping');m=FakeRepo([x])
        with tempfile.TemporaryDirectory() as td:
            s=r.State(pathlib.Path(td)/'db');a=r.tick(m,s);b=r.tick(m,s)
            self.assertEqual((a['executed'],b['executed']),(1,0));self.assertEqual(s.count(),1)
    def test_batch_limit(self):
        jobs=[r.make_job('ping') for _ in range(12)];m=FakeRepo(jobs)
        with tempfile.TemporaryDirectory() as td:
            s=r.State(pathlib.Path(td)/'db')
            counts=[r.tick(m,s)['executed'] for _ in range(4)]
            self.assertEqual(counts,[4,4,4,0])
    def test_spoofed_output_not_in_public_receipt(self):
        x=r.make_job('hp_status');self.assertNotIn('username',r.execute(x))
    def test_missing_github_queue(self):
        self.assertEqual(r.tick(type('Empty',(),{'files':lambda _:[]})(),r.State(pathlib.Path(tempfile.mkdtemp())/'db'))['executed'],0)
    def test_multi_line_real_verify(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            (root/'domino.py').write_text('import json\nprint(json.dumps({"valid":True,"events":3},indent=2))\n')
            self.assertEqual(r.execute(r.make_job('sidecar_verify'),root),{'verified':True,'events':3})

if __name__=='__main__':unittest.main()
