#!/usr/bin/env python3
# cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
"""Caveman Focus public queue relay: read-only GitHub fetch; local allowlisted work.

Owner's iPhone ChatGPT -> a GitHub commit in CF-0 -> this poller on HP.
No token needed to *receive*. This does NOT implement arbitrary remote shell.
Results stay local unless user configures explicitly scoped GitHub write token.
"""
from __future__ import annotations
import argparse, base64, contextlib, hashlib, json, os, pathlib, re, sqlite3, sys, time, urllib.error, urllib.parse, urllib.request, uuid
from dataclasses import dataclass
from typing import Any

REPO = 'whoiwts110217-creator/CF-0'
API = 'https://api.github.com'
AGENT = 'CavemanFocus-CF0-Relay/0.1'
ALLOWED = frozenset(('ping', 'hp_status', 'sidecar_verify'))
MAX_JOB_BYTES = 8192
MAX_SCAN = 80
MAX_ACTIONS = 4
UUID = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')
MARKER = 'CAVEMAN FOCUS | KIARA LYNN-ROSE. SMITH'

class RelayError(Exception): pass

def dump(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')

def sha(obj: Any) -> str:
    return hashlib.sha256(dump(obj)).hexdigest()

def validate(job: Any, name: str, now: int | None=None) -> dict:
    now = int(time.time()) if now is None else now
    if not isinstance(job,dict) or set(job) != {'v','id','action','issued','expires','args'}:
        raise RelayError('invalid_schema')
    jid=job['id']
    if not isinstance(jid,str) or not UUID.fullmatch(jid) or name != jid+'.json':
        raise RelayError('bad_id')
    if type(job['v']) is not int or job['v']!=1: raise RelayError('bad_version')
    if not isinstance(job['action'],str) or job['action'] not in ALLOWED: raise RelayError('action_not_allowed')
    if job['args'] != {} or type(job['args']) is not dict: raise RelayError('invalid_arguments')
    ts,ex=job['issued'],job['expires']
    if type(ts) is not int or type(ex) is not int or not (ts - 180 <= now <= ex) or ex-ts > 86400 or ex<=ts:
        raise RelayError('expired_or_future')
    if len(dump(job)) > MAX_JOB_BYTES: raise RelayError('oversize')
    return job

def make_job(action: str, now: int | None = None) -> dict:
    if action not in ALLOWED: raise RelayError('action_not_allowed')
    now=int(time.time()) if now is None else now
    return dict(v=1,id=str(uuid.uuid4()),action=action,issued=now,expires=now+7200,args={})

@dataclass
class HttpRepo:
    repo: str=REPO
    api: str=API
    token: str | None=None
    def request(self,method: str,path:str,payload:dict | None=None) -> Any:
        url=self.api.rstrip('/')+path
        data=dump(payload) if payload is not None else None
        headers={'Accept':'application/vnd.github+json','User-Agent':AGENT,'X-GitHub-Api-Version':'2022-11-28'}
        if data is not None: headers['Content-Type']='application/json'
        if self.token: headers['Authorization']='Bearer '+self.token
        req=urllib.request.Request(url,data=data,headers=headers,method=method)
        try:
            with urllib.request.urlopen(req,timeout=20) as res:
                data=res.read(1_000_001)
                if len(data)>1_000_000:raise RelayError('response_too_large')
                return json.loads(data)
        except urllib.error.HTTPError as e:
            if e.code==404 and method=='GET': return None
            raise RelayError('github_http_'+str(e.code)) from e
        except (urllib.error.URLError,TimeoutError,OSError) as e:
            raise RelayError('github_unreachable') from e
        except (ValueError, UnicodeDecodeError) as e:
            raise RelayError('github_invalid_json') from e
    def files(self):
        path=f'/repos/{self.repo}/contents/command_queue/inbox?ref=main'
        data=self.request('GET',path)
        if data is None: return []
        if not isinstance(data,list): raise RelayError('not_directory')
        if len(data)>=1000:raise RelayError('queue_full')
        return sorted({x['name'] for x in data if isinstance(x,dict) and x.get('type')=='file' and
                       isinstance(x.get('name'),str) and x['name'].endswith('.json') and UUID.fullmatch(x['name'][:-5])})
    def load(self,name):
        path=f'/repos/{self.repo}/contents/command_queue/inbox/{name}?ref=main'
        data=self.request('GET',path)
        if not isinstance(data,dict) or data.get('encoding')!='base64':raise RelayError('invalid_file')
        try:
            b=base64.b64decode(''.join(data['content'].split()),validate=True)
            if len(b)>MAX_JOB_BYTES:raise RelayError('oversize')
            return json.loads(b)
        except (KeyError,ValueError,TypeError) as e:
            raise RelayError('invalid_file_data') from e
    def publish(self,job_id,receipt):
        # Optional GitHub write. Never put device name, file lists, paths or secrets in public receipt.
        if not self.token: return False
        path=f'/repos/{self.repo}/contents/command_queue/receipts/{job_id}.json'
        previous=self.request('GET',path+'?ref=main')
        if previous is not None:
            # Remote receipts are untrusted; reject malformed or conflicting data.
            if not isinstance(previous, dict) or previous.get('encoding') != 'base64':
                raise RelayError('receipt_conflict')
            try:
                encoded = previous['content']
                if not isinstance(encoded, str): raise ValueError('invalid content type')
                old = json.loads(base64.b64decode(''.join(encoded.split()), validate=True))
            except (KeyError, ValueError, TypeError, UnicodeDecodeError) as exc:
                raise RelayError('receipt_unreadable') from exc
            if old != receipt: raise RelayError('receipt_conflict')
            return True
        self.request('PUT',path,{'message':f'HP public relay receipt {job_id}', 'branch':'main',
                                 'content':base64.b64encode(dump(receipt)).decode('ascii')})
        return True

class State:
    def __init__(self, db:pathlib.Path):
        db.parent.mkdir(parents=True,exist_ok=True)
        self.db=db
        with self.conn() as con:
            con.execute('CREATE TABLE IF NOT EXISTS receipts(id TEXT PRIMARY KEY, digest TEXT NOT NULL, receipt TEXT NOT NULL)')
            con.execute('CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, value TEXT NOT NULL)')
            # Durable at-most-once start marker: if the process disappears
            # after starting an action but before saving a receipt, an unknown
            # outcome must never be silently treated as safe to re-execute.
            con.execute('CREATE TABLE IF NOT EXISTS attempts(id TEXT PRIMARY KEY, digest TEXT NOT NULL, state TEXT NOT NULL)')
    @contextlib.contextmanager
    def conn(self):
        # SQLite connection context manager commits but does not close; this
        # explicit close is necessary for Windows temporary-directory cleanup.
        with contextlib.closing(sqlite3.connect(self.db,timeout=12)) as con:
            with con:
                yield con
    def receipt(self,jid):
        with self.conn() as con:
            x=con.execute('SELECT digest,receipt FROM receipts WHERE id=?',(jid,)).fetchone()
        return (x[0],json.loads(x[1])) if x else None
    def attempt(self,jid):
        with self.conn() as con:
            x=con.execute('SELECT digest,state FROM attempts WHERE id=?',(jid,)).fetchone()
        return (x[0],x[1]) if x else None
    def begin(self,jid,digest):
        # SQLite commits the marker BEFORE executing the allowlisted action.
        # Never re-run if a prior attempt for this UUID is already recorded.
        with self.conn() as con:
            existing=con.execute('SELECT digest FROM attempts WHERE id=?',(jid,)).fetchone()
            if existing is not None:
                if existing[0]!=digest:raise RelayError('attempt_conflict')
                return False
            con.execute('INSERT INTO attempts VALUES(?,?,?)',(jid,digest,'in_progress'))
        return True
    def save(self,jid,digest,receipt):
        with self.conn() as con:
            con.execute('INSERT INTO receipts VALUES(?,?,?)',(jid,digest,dump(receipt).decode()))
            # Atomic with the completed receipt. A failed save leaves the
            # original in_progress marker, not a fabricated success.
            con.execute("UPDATE attempts SET state='completed' WHERE id=? AND digest=?",(jid,digest))
    def cursor(self):
        with self.conn() as con:r=con.execute("SELECT value FROM meta WHERE k='cursor'").fetchone()
        return r[0] if r else ''
    def set_cursor(self,name):
        with self.conn() as con:con.execute("INSERT INTO meta VALUES('cursor',?) ON CONFLICT(k) DO UPDATE SET value=excluded.value",(name,))
    def count(self):
        with self.conn() as con:return con.execute('SELECT COUNT(*) FROM receipts').fetchone()[0]

def execute(job,sidecar:pathlib.Path|None=None):
    if job['action']=='ping':return {'pong':True,'protocol':1}
    if job['action']=='hp_status':return {'worker':'online','policy':'public-safe','commands':sorted(ALLOWED)}
    if job['action']=='sidecar_verify':
        if not sidecar:return {'verified':False,'reason':'not_configured'}
        script=sidecar/'domino.py'
        if not script.is_file():return {'verified':False,'reason':'missing_script'}
        import subprocess
        try:
            p=subprocess.run([sys.executable,str(script),'verify'],cwd=str(sidecar),capture_output=True,text=True,timeout=20)
            out=json.loads(p.stdout)
            return {'verified':p.returncode==0 and out.get('valid') is True,
                    'events':out.get('events') if type(out.get('events')) is int else None}
        except (OSError,subprocess.TimeoutExpired,ValueError):return {'verified':False,'reason':'verify_failed'}
    raise RelayError('action_not_allowed')

def tick(repo:HttpRepo, state:State,sidecar=None):
    names=repo.files();cur=state.cursor()
    ordered=[n for n in names if n>cur]+[n for n in names if n<=cur]
    result={'scanned':0,'executed':0,'replayed':0,'uncertain':0,'public_receipts':0,'errors':[]}
    for n in ordered[:MAX_SCAN]:
        state.set_cursor(n);result['scanned']+=1
        jid=n[:-5];stored=state.receipt(jid)
        try:
            if stored is not None:
                result['replayed']+=1
                if repo.publish(jid,stored[1]):result['public_receipts']+=1
                continue
            job=validate(repo.load(n),n)
            digest=sha(job)
            previous=state.attempt(jid)
            if previous is not None:
                if previous[0]!=digest:raise RelayError('attempt_conflict')
                # No durable completed receipt. Could have executed before
                # crash; do not retry and do not publish a completed receipt.
                result['uncertain']+=1
                continue
            if not state.begin(jid,digest):
                result['uncertain']+=1
                continue
            value=execute(job,sidecar)
            receipt={'v':1,'id':jid,'request_sha256':digest,'status':'completed','result':value}
            state.save(jid,digest,receipt)
            result['executed']+=1
            if repo.publish(jid,receipt):result['public_receipts']+=1
            if result['executed']>=MAX_ACTIONS:break
        except (RelayError,sqlite3.DatabaseError) as e:
            result['errors'].append({'file':n,'error':str(e)})
    return result

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('command',choices=['ping-demo','once','watch','make-job','status'])
    p.add_argument('--action',choices=sorted(ALLOWED),default='ping')
    p.add_argument('--state-dir',default=os.environ.get('CF_RELAY_HOME',str(pathlib.Path.home()/'.caveman_focus_relay')))
    p.add_argument('--sidecar',default=os.environ.get('CF_SIDECAR_DIR'))
    p.add_argument('--interval',type=int,default=90)
    args=p.parse_args(argv)
    if args.command=='make-job':print(json.dumps(make_job(args.action),indent=2));return 0
    if args.command=='ping-demo':
        job=make_job('ping');print(json.dumps({'validated':validate(job,job['id']+'.json')['action'],'result':execute(job)}));return 0
    state=State(pathlib.Path(args.state_dir)/'relay.sqlite3')
    if args.command=='status':print(json.dumps({'processed':state.count(),'queue':REPO,'tokenless_read':True}));return 0
    repo=HttpRepo(token=os.environ.get('CF_RELAY_GITHUB_TOKEN'))
    if args.command=='once':print(json.dumps(tick(repo,state,pathlib.Path(args.sidecar) if args.sidecar else None)));return 0
    if args.interval<30:p.error('minimum interval 30s')
    while True:
        try:print(json.dumps(tick(repo,state,pathlib.Path(args.sidecar) if args.sidecar else None)),flush=True)
        except RelayError as e:print(json.dumps({'error':str(e)}),file=sys.stderr,flush=True)
        time.sleep(args.interval)

if __name__=='__main__':raise SystemExit(main())
