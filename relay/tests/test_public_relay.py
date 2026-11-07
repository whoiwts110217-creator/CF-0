# cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
import sys,pathlib,unittest,tempfile,base64,json,time
from unittest.mock import patch
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


    def test_oversized_job_file_rejected(self):
        x=r.make_job('ping')
        x['junk']='A'*(r.MAX_JOB_BYTES+1)
        with self.assertRaises(r.RelayError):r.validate(x,x['id']+'.json')

    def test_json_expired_not_executed(self):
        x=r.make_job('ping',now=1000)
        class BadRepo(FakeRepo):
            pass
        # Expired request is examined but does not create a ledger receipt.
        with tempfile.TemporaryDirectory() as td:
            state=r.State(pathlib.Path(td)/'db')
            status=r.tick(BadRepo([x]),state)
            self.assertEqual(status['executed'],0)
            self.assertEqual(state.count(),0)
            self.assertEqual(status['errors'][0]['error'],'expired_or_future')

    def test_state_connection_closed_after_tick(self):
        x=r.make_job('ping')
        with tempfile.TemporaryDirectory() as td:
            home=pathlib.Path(td)
            db=home/'state.sqlite3'
            state=r.State(db)
            self.assertEqual(r.tick(FakeRepo([x]),state)['executed'],1)
            # Windows would fail this rename if the SQLite database were still open.
            db.rename(home/'renamed.sqlite3')
            self.assertTrue((home/'renamed.sqlite3').exists())

    def test_http_transport_integration(self):
        self.assert_http_transport_receipt('ping', {'pong': True, 'protocol': 1})

    def test_http_status_receipt_excludes_private_host_metadata(self):
        import os

        with patch.dict(os.environ, {
            'USERNAME': 'synthetic-private-user',
            'COMPUTERNAME': 'synthetic-private-host',
            'USERPROFILE': r'C:\Users\synthetic-private-user',
        }):
            self.assert_http_transport_receipt('hp_status', {
                'worker': 'online',
                'policy': 'public-safe',
                'commands': ['hp_status', 'ping', 'sidecar_verify'],
            })

    def assert_http_transport_receipt(self, action, expected_result):
        import hashlib
        import threading
        from urllib.parse import urlparse
        from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
        job=r.make_job(action)
        root = f"/repos/{r.REPO}/contents/command_queue"
        filename = job["id"] + ".json"
        receipt_path = f"{root}/receipts/{filename}"
        writes = []

        def contents(value):
            return {"encoding": "base64", "content": base64.b64encode(json.dumps(value).encode()).decode()}

        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def respond(self,status,payload):
                data=json.dumps(payload).encode()
                self.send_response(status)
                self.send_header('Content-Length',str(len(data)))
                self.end_headers();self.wfile.write(data)
            def do_GET(self):
                url = urlparse(self.path)
                if url.query != "ref=main":
                    self.respond(404, {"message": "wrong ref"})
                elif url.path == f"{root}/inbox":
                    self.respond(200, [{"name": filename, "type": "file"}])
                elif url.path == f"{root}/inbox/{filename}":
                    self.respond(200, contents(job))
                elif url.path == receipt_path and writes:
                    self.respond(200, contents(writes[-1]))
                else:
                    self.respond(404, {"message": "missing"})
            def do_PUT(self):
                data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                if self.path != receipt_path or data.get("branch") != "main":
                    self.respond(404, {"message": "wrong write target"})
                    return
                writes.append(json.loads(base64.b64decode(data["content"])))
                self.respond(201, {"content": {"sha": "demo"}})
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            with tempfile.TemporaryDirectory() as td:
                mb=r.HttpRepo(api=f'http://127.0.0.1:{server.server_port}',token='local-test')
                database = pathlib.Path(td) / "state.sqlite3"
                first = r.tick(mb, r.State(database))
                replay = r.tick(mb, r.State(database))
                self.assertEqual((first["executed"], replay["executed"]), (1, 0))
                self.assertEqual((first["public_receipts"], replay["public_receipts"]), (1, 1))
                self.assertEqual(replay["replayed"], 1)
                self.assertEqual(first["errors"] + replay["errors"], [])
                canonical = json.dumps(job, sort_keys=True, separators=(",", ":")).encode()
                response = json.dumps(expected_result, sort_keys=True, separators=(",", ":")).encode()
                expected = {
                    "v": 2,
                    "id": job["id"],
                    "request_sha256": hashlib.sha256(canonical).hexdigest(),
                    "status": "completed",
                    "result": expected_result,
                    "response_sha256": hashlib.sha256(response).hexdigest(),
                }
                self.assertEqual(writes, [expected])
                self.assertEqual(r.State(database).receipt(job["id"]),
                                 (expected["request_sha256"], expected))
        finally:
            server.shutdown();thread.join(timeout=3);server.server_close()


    def test_exact_four_actions_per_tick_restarts(self):
        jobs=[r.make_job('ping') for _ in range(15)]
        inbox=FakeRepo(jobs)
        with tempfile.TemporaryDirectory() as td:
            database=pathlib.Path(td)/'relay.sqlite3'
            first=r.tick(inbox,r.State(database))
            self.assertEqual(first['executed'],4)
            counts=[r.tick(inbox,r.State(database))['executed'] for _ in range(4)]
            self.assertEqual(counts,[4,4,3,0])
            self.assertEqual(r.State(database).count(),15)
            self.assertEqual(len(inbox.sent),15)

    def test_spoofed_uuid_filename_is_inert(self):
        supplied=r.make_job('ping');fake=r.make_job('ping')
        class Swapped(FakeRepo):
            def files(self):return [fake['id']+'.json']
            def load(self,name):return supplied
        with tempfile.TemporaryDirectory() as td:
            state=r.State(pathlib.Path(td)/'ledger.sqlite3')
            result=r.tick(Swapped([supplied]),state)
            self.assertEqual(result['executed'],0)
            self.assertEqual(result['errors'][0]['error'],'bad_id')
            self.assertEqual(state.count(),0)

    def test_remote_existing_receipt_forgery_and_malformed_data_rejected(self):
        job=r.make_job('ping');jid=job['id'];result={'pong':True,'protocol':1}
        expected={'v':2,'id':jid,'request_sha256':r.sha(job),'status':'completed',
                  'result':result,'response_sha256':r.sha(result)}
        mailbox=r.HttpRepo(repo=r.REPO,token='local-demo')
        calls=[]
        def pretend(method,path,payload=None):
            calls.append(method)
            return {'encoding':'base64','content':base64.b64encode(r.dump({'id':jid,'status':'forged'})).decode()}
        mailbox.request=pretend
        with self.assertRaisesRegex(r.RelayError,'receipt_conflict'):
            mailbox.publish(jid,expected)
        self.assertEqual(calls,['GET'])
        for invalid in ([], {'encoding':'base64'}, {'encoding':'base64','content':'NOT-BASE64!'},
                        {'encoding':'base64','content':123}):
            calls.clear()
            mailbox.request=lambda method,path,payload=None,bad=invalid: calls.append(method) or bad
            with self.assertRaises(r.RelayError):mailbox.publish(jid,expected)
            self.assertEqual(calls,['GET'])

    def test_existing_receipt_versions_match_without_rewriting(self):
        job = r.make_job("ping")
        job_id = job["id"]
        result = {"pong": True, "protocol": 1}
        legacy = {"v": 1, "id": job_id, "request_sha256": r.sha(job),
                  "status": "completed", "result": result}
        current = {**legacy, "v": 2, "response_sha256": r.sha(result)}
        mailbox = r.HttpRepo(token="local-test")
        path = f"/repos/{r.REPO}/contents/command_queue/receipts/{job_id}.json?ref=main"
        for saved, existing in ((current, legacy), (legacy, current)):
            with self.subTest(saved=saved["v"], existing=existing["v"]):
                response = {"encoding": "base64", "content": base64.b64encode(r.dump(existing)).decode()}
                with patch.object(mailbox, "request", return_value=response) as request:
                    self.assertTrue(mailbox.publish(job_id, saved))
                    request.assert_called_once_with("GET", path)
        invalid = {**current, "response_sha256": "0" * 64}
        response = {"encoding": "base64", "content": base64.b64encode(r.dump(invalid)).decode()}
        with patch.object(mailbox, "request", return_value=response) as request:
            with self.assertRaisesRegex(r.RelayError, "receipt_conflict"):
                mailbox.publish(job_id, current)
            request.assert_called_once_with("GET", path)

    def test_corrupt_saved_response_is_neither_reexecuted_nor_republished(self):
        job = r.make_job("ping")
        job_id = job["id"]
        with tempfile.TemporaryDirectory() as folder:
            db = pathlib.Path(folder) / "relay.sqlite3"
            state = r.State(db)
            repo = FakeRepo([job])
            self.assertEqual(r.tick(repo, state)["executed"], 1)
            receipt = repo.sent.pop(job_id)
            tampered = {**receipt, "result": {"pong": False, "protocol": 1}}
            missing_digest = {key: value for key, value in receipt.items() if key != "response_sha256"}
            for raw, error in ((r.dump(tampered).decode(), "response_digest_mismatch"),
                               (r.dump(missing_digest).decode(), "invalid_receipt"),
                               ("{", "receipt_unreadable")):
                with self.subTest(error=error):
                    with state.conn() as connection:
                        connection.execute("UPDATE receipts SET receipt=? WHERE id=?", (raw, job_id))
                    with patch.object(r, "execute") as execute:
                        outcome = r.tick(repo, r.State(db))
                        execute.assert_not_called()
                    self.assertEqual(outcome["errors"], [{"file": job_id + ".json", "error": error}])
                    self.assertEqual((outcome["executed"], outcome["replayed"]), (0, 0))
                    self.assertEqual(repo.sent, {})
                    self.assertEqual(state.count(), 1)

    def test_result_isolation_rejects_remote_shell_and_personal_fields(self):
        job=r.make_job('ping')
        for illegal in ({'cmd':'powershell'}, {'read_private_files':True}):
            modified=dict(job,args=illegal)
            with self.assertRaisesRegex(r.RelayError,'invalid_arguments'):
                r.validate(modified,job['id']+'.json')
        status=r.execute(r.make_job('hp_status'))
        receipt=r.dump(status).decode()
        for forbidden in ('C:\\Users', 'hostname', 'user_name', 'bank', 'token', 'private_file'):
            self.assertNotIn(forbidden,receipt)


    def test_reject_dynamic_python_evaluation_action(self):
        for action in ('eval', 'exec', 'python_eval'):
            x=r.make_job('ping');x['action']=action
            with self.assertRaisesRegex(r.RelayError,'action_not_allowed'):
                r.validate(x,x['id']+'.json')

    def test_reject_remote_file_write_action(self):
        x=r.make_job('ping');x['action']='file_write'
        with self.assertRaisesRegex(r.RelayError,'action_not_allowed'):
            r.validate(x,x['id']+'.json')
        x=r.make_job('ping');x['args']={'path':'anything','content':'test'}
        with self.assertRaisesRegex(r.RelayError,'invalid_arguments'):
            r.validate(x,x['id']+'.json')

    def test_reject_browser_execution_action(self):
        for action in ('browser','browser_open','chrome'):
            x=r.make_job('ping');x['action']=action
            with self.assertRaisesRegex(r.RelayError,'action_not_allowed'):
                r.validate(x,x['id']+'.json')

    def test_reject_unknown_json_keys_even_if_allowlisted(self):
        for field in ('command','path','url','python','browser'):
            x=r.make_job('ping');x[field]='inert'
            with self.assertRaisesRegex(r.RelayError,'invalid_schema'):
                r.validate(x,x['id']+'.json')

if __name__=='__main__':unittest.main()
