#!/usr/bin/env python3
# cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
"""Evidence-only 200-task checkpoint keeper: complete four → create reviewable artifact."""
import argparse, hashlib, json, pathlib, sys, datetime, subprocess

if __package__:
    from .validate_registry import check_registry
else:
    from validate_registry import check_registry

ROOT=pathlib.Path(__file__).parent
SRC=ROOT/'registry.json'
EVENTS=ROOT/'events.jsonl'
CHECKPOINTS=ROOT/'checkpoints'

def load():return json.loads(SRC.read_text(encoding='utf-8'))
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def verify():
 r=load();check_registry(r)
 return r

def complete(ids,proof):
    if not isinstance(proof, str) or len(proof.strip()) < 12:
        raise ValueError('specific evidence reference required')
    ids = tuple(ids)
    if not 1 <= len(ids) <= 4 or len(set(ids)) != len(ids):
        raise ValueError('complete 1-4 distinct items')

    registry = verify()
    tasks = {task['id']: task for task in registry['tasks']}
    for task_id in ids:
        if task_id not in tasks:
            raise ValueError('unknown id')
        task = tasks[task_id]
        if task['status'] != 'planned':
            raise ValueError('already completed')
        task['status'] = 'verified'
        task['evidence'] = proof
    registry['completed'] += len(ids)
    check_registry(registry)

    SRC.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    recorded_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with EVENTS.open('a', encoding='utf-8') as log:
        for task_id in ids:
            event = {'task': task_id, 'status': 'verified', 'evidence': proof, 'recorded_at': recorded_at}
            log.write(json.dumps(event, sort_keys=True) + '\n')
    return registry

def checkpoint():
 r=verify();n=r['completed'];CHECKPOINTS.mkdir(exist_ok=True)
 snap={'completed':n,'target':200,'pending':200-n,'evidence_ids':[t['id'] for t in r['tasks'] if t['status']=='verified'],
       'registry_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),
       'warning':'Checkpoint is source-level task progress, not proof of HP installation.'}
 path=CHECKPOINTS/f'checkpoint_{n:03d}.json'
 path.write_text(json.dumps(snap,indent=2)+'\n')
 print(path)

def git_checkpoint(push=False):
    """Commit one four-item verified checkpoint in a real Git checkout.

    No network or write credentials are required for the local commit;
    --push is explicit, and depends on preconfigured owner Git authorization.
    """
    r=verify();n=r['completed']
    if n==0 or n%4!=0:raise ValueError('git checkpoint requires 4 verified tasks since prior checkpoint')
    root=ROOT.parent
    names=['automation_200/registry.json','automation_200/events.jsonl',
           f'automation_200/checkpoints/checkpoint_{n:03d}.json']
    def call(*args):
        result=subprocess.run(['git',*args],cwd=root,check=True,capture_output=True,text=True,timeout=40)
        return result.stdout.strip()
    if call('rev-parse','--is-inside-work-tree')!='true':raise ValueError('not a Git checkout')
    checkpoint()
    call('add','--',*names)
    if call('diff','--cached','--name-only','--',*names):
        call('commit','--only','-m',f'CF200 verified checkpoint {n:03d}/200','--',*names)
    if push:call('push','origin','HEAD')
    print(json.dumps({'saved_git':True,'verified':n,'pushed':push}))

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=('status','complete','checkpoint','validate','git-checkpoint'))
 p.add_argument('ids',nargs='*');p.add_argument('--evidence',default='');p.add_argument('--push',action='store_true')
 a=p.parse_args()
 if a.action=='complete':r=complete(a.ids,a.evidence)
 else:r=verify()
 if a.action=='git-checkpoint':git_checkpoint(a.push)
 elif a.action=='checkpoint':checkpoint()
 else:print(json.dumps({'verified':r['completed'],'target':len(r['tasks']),'planned':200-r['completed']}))
if __name__=='__main__':main()
