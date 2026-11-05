#!/usr/bin/env python3
# cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
"""Evidence-only 200-task checkpoint keeper: complete four → create reviewable artifact."""
import argparse, hashlib, json, pathlib, sys, datetime, subprocess
ROOT=pathlib.Path(__file__).parent
SRC=ROOT/'registry.json'
EVENTS=ROOT/'events.jsonl'
CHECKPOINTS=ROOT/'checkpoints'

def load():return json.loads(SRC.read_text(encoding='utf-8'))
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def verify():
 from validate_registry import check_registry
 r=load();check_registry(r)
 return r

def complete(ids,proof):
 if not proof or len(proof)<12:raise ValueError('specific evidence reference required')
 r=verify(); found=set(ids)
 if not 1<=len(found)<=4:raise ValueError('complete 1-4 distinct items')
 for t in r['tasks']:
  if t['id'] in found:
   if t['status']!='planned':raise ValueError('already completed')
   t['status']='verified';t['evidence']=proof
 if sum(t['status']=='verified' for t in r['tasks'])!=r['completed']+len(found):raise ValueError('unknown id')
 r['completed']+=len(found)
 SRC.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 events=[{'task':id,'status':'verified','evidence':proof,'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat()} for id in ids]
 with EVENTS.open('a',encoding='utf-8') as f:
  for e in events:f.write(json.dumps(e,sort_keys=True)+'\n')
 return r

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
    checkpoint()
    root=ROOT.parent
    names=['automation_200/registry.json','automation_200/events.jsonl',
           f'automation_200/checkpoints/checkpoint_{n:03d}.json']
    def call(*args):
        result=subprocess.run(['git',*args],cwd=root,check=True,capture_output=True,text=True,timeout=40)
        return result.stdout.strip()
    if call('rev-parse','--is-inside-work-tree')!='true':raise ValueError('not a Git checkout')
    call('add','--',*names)
    if call('diff','--cached','--name-only'):
        call('commit','-m',f'CF200 verified checkpoint {n:03d}/200')
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
