#!/usr/bin/env python3
# cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
"""Evidence-only 200-task checkpoint keeper: complete four → create reviewable artifact."""
import argparse, hashlib, json, pathlib, sys, datetime
ROOT=pathlib.Path(__file__).parent
SRC=ROOT/'registry.json'
EVENTS=ROOT/'events.jsonl'
CHECKPOINTS=ROOT/'checkpoints'

def load():return json.loads(SRC.read_text(encoding='utf-8'))
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def verify():
 r=load();assert len(r['tasks'])==200
 ids=[t['id'] for t in r['tasks']];assert len(set(ids))==len(ids)
 actual=sum(t['status']=='verified' for t in r['tasks']);assert r['completed']==actual
 assert all(t['evidence'] for t in r['tasks'] if t['status']=='verified')
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

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=('status','complete','checkpoint','validate'))
 p.add_argument('ids',nargs='*');p.add_argument('--evidence',default='')
 a=p.parse_args()
 if a.action=='complete':r=complete(a.ids,a.evidence)
 else:r=verify()
 if a.action=='checkpoint':checkpoint()
 else:print(json.dumps({'verified':r['completed'],'target':len(r['tasks']),'planned':200-r['completed']}))
if __name__=='__main__':main()
