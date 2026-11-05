# cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
"""Stress and genuine loopback HTTP tests for HP Bridge v0.3.

No GitHub connection or external network; use local ephemeral HTTP receiver.
"""
import base64
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cf_hp_bridge as bridge

class SyntheticMailbox:
    def __init__(self, jobs):
        self.jobs = {j['id']+'.json':j for j in jobs}
        self.replies = {}
        self.reads = []
    def require_private(self): pass
    def list_jobs(self): return sorted(self.jobs)
    def load_job(self, filename):
        self.reads.append(filename)
        return self.jobs[filename]
    def publish(self, jid, reply):
        if jid in self.replies and self.replies[jid] != reply:
            raise bridge.BridgeError('result_conflict')
        self.replies[jid] = reply

class FairnessTests(unittest.TestCase):
    def test_old_invalid_requests_dont_starve_valid_new_jobs(self):
        invalid=[bridge.make_job('ping') for _ in range(55)]
        for j in invalid: j['action']='arbitrary_command'
        valid=[bridge.make_job('ping') for _ in range(3)]
        # Sort deterministic names and make the valid IDs lexically higher
        # so that they fall at the tail of the queue.
        valid_jobs=[]
        for i,j in enumerate(valid):
            j['id']=f'ffffffff-ffff-4fff-8fff-{i:012x}'
            valid_jobs.append(j)
        mb=SyntheticMailbox(invalid+valid_jobs)
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'ledger.sqlite3'
            a=bridge.run_once(mb,bridge.LocalLedger(path))
            b=bridge.run_once(mb,bridge.LocalLedger(path))
            c=bridge.run_once(mb,bridge.LocalLedger(path))
        self.assertEqual([a['executed'],b['executed'],c['executed']],[0,3,0])
        self.assertEqual([a['scanned'],b['scanned']],[40,40]) # rotates and wraps
        self.assertEqual(len(mb.replies),3)
        self.assertEqual(len(set(mb.replies)),3)

    def test_corrupt_jobs_cannot_force_unbounded_single_tick_reads(self):
        jobs=[bridge.make_job('ping') for _ in range(130)]
        for j in jobs:j['params']={'bad':'unsafe'}
        mb=SyntheticMailbox(jobs)
        with tempfile.TemporaryDirectory() as td:
            led=bridge.LocalLedger(Path(td)/'ledger.sqlite3')
            r=bridge.run_once(mb,led)
            self.assertEqual(r['scanned'],bridge.MAX_SCAN_PER_RUN)
            self.assertEqual(len(mb.reads),bridge.MAX_SCAN_PER_RUN)
            self.assertEqual(len(r['errors']),bridge.MAX_SCAN_PER_RUN)
            self.assertEqual(r['executed'],0)
            self.assertEqual(r['pending'],130)

    def test_cursor_wraps_when_new_smaller_id_arrives(self):
        hi=bridge.make_job('ping');hi['id']='ffffffff-ffff-4fff-8fff-ffffffffffff'
        mb=SyntheticMailbox([hi])
        with tempfile.TemporaryDirectory() as td:
            led=bridge.LocalLedger(Path(td)/'ledger.sqlite3')
            self.assertEqual(bridge.run_once(mb,led)['executed'],1)
            lo=bridge.make_job('ping');lo['id']='00000000-0000-4000-8000-000000000001'
            mb.jobs[lo['id']+'.json']=lo
            self.assertEqual(bridge.run_once(mb,led)['executed'],1)

    def test_persisted_cursor_avoids_prefix_replay_on_restart(self):
        bad=[bridge.make_job('ping') for _ in range(45)]
        for job in bad:job['action']='disabled'
        mb=SyntheticMailbox(bad)
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'db.sqlite3'
            a=bridge.run_once(mb,bridge.LocalLedger(path))
            observed_before=set(mb.reads)
            b=bridge.run_once(mb,bridge.LocalLedger(path))
            second=set(mb.reads)-observed_before
        self.assertEqual(a['scanned'],40)
        self.assertEqual(b['scanned'],40) # wraps after the five unseen jobs
        self.assertEqual(len(second),5)

    def test_old_ledger_schema_upgrades_without_losing_jobs(self):
        import sqlite3
        from contextlib import closing
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'db.sqlite3'
            with closing(sqlite3.connect(str(path))) as conn:
                conn.execute('CREATE TABLE jobs(id TEXT PRIMARY KEY, digest TEXT NOT NULL, status TEXT NOT NULL, reply TEXT, created_at INTEGER NOT NULL)')
                conn.execute("INSERT INTO jobs VALUES('old', 'abc', 'published', '{}', 1)")
                conn.commit()
            led=bridge.LocalLedger(path)
            self.assertEqual(led.counts(), {'published':1})
            self.assertEqual(led.scan_cursor(),'')
            led.set_scan_cursor('00000000-0000-4000-8000-000000000001.json')
            self.assertNotEqual(led.scan_cursor(),'')

class LoopbackHTTPTest(unittest.TestCase):
    def test_true_http_request_receipt_and_duplicate_prevention(self):
        job=bridge.make_job('ping')
        state={'jobs':{job['id']+'.json':job},'results':{},'calls':[]}
        repo='demo-owner/private-box'
        prefix='/repos/'+repo
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def respond(self,status,obj):
                b=json.dumps(obj).encode()
                self.send_response(status)
                self.send_header('Content-Type','application/json')
                self.send_header('Content-Length',str(len(b)))
                self.end_headers();self.wfile.write(b)
            def do_GET(self):
                self.assert_authorized()
                path=self.path.split('?')[0]
                state['calls'].append(('GET',path))
                if path==prefix:
                    self.respond(200,{'private':True,'full_name':repo})
                elif path==prefix+'/contents/bridge/queue':
                    self.respond(200,[{'name':n,'type':'file'} for n in state['jobs']])
                elif path.startswith(prefix+'/contents/bridge/queue/'):
                    name=path.rsplit('/',1)[-1]
                    if name not in state['jobs']:
                        self.respond(404,{'message':'not found'})
                    else:
                        raw=bridge.canonical(state['jobs'][name])
                        self.respond(200,{'encoding':'base64','content':base64.b64encode(raw).decode()})
                elif path.startswith(prefix+'/contents/bridge/results/'):
                    name=path.rsplit('/',1)[-1]
                    if name not in state['results']:
                        self.respond(404,{'message':'not found'})
                    else:
                        self.respond(200,{'encoding':'base64','content':base64.b64encode(bridge.canonical(state['results'][name])).decode()})
                else:
                    self.respond(404,{'message':'not found'})
            def assert_authorized(self):
                if self.headers.get('Authorization')!='Bearer local-demo-secret':
                    raise AssertionError('Authorization header missing')
            def do_PUT(self):
                self.assert_authorized()
                path=self.path.split('?')[0]
                state['calls'].append(('PUT',path))
                if not path.startswith(prefix+'/contents/bridge/results/'):
                    self.respond(400,{'error':'bad path'});return
                payload=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                name=path.rsplit('/',1)[-1]
                state['results'][name]=json.loads(base64.b64decode(payload['content']))
                self.respond(201,{'content':{'name':name},'commit':{'sha':'abc'}})
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            with patch.object(bridge,'API',f'http://127.0.0.1:{server.server_port}'):
                mb=bridge.GitHubMailbox(repo,'local-demo-secret')
                with tempfile.TemporaryDirectory() as td:
                    led=bridge.LocalLedger(Path(td)/'state.sqlite3')
                    a=bridge.run_once(mb,led)
                    b=bridge.run_once(mb,led)
                    self.assertEqual((a['executed'],b['executed']),(1,0))
                    self.assertEqual(led.counts()['published'],1)
            result=state['results'][job['id']+'.json']
            self.assertEqual(result['request_sha256'],bridge.hash_obj(job))
            self.assertEqual(result['result']['ping'],'pong')
            self.assertEqual(sum(m=='PUT' for m,p in state['calls']),1)
        finally:
            server.shutdown();thread.join(timeout=3);server.server_close()

if __name__=='__main__':unittest.main()
