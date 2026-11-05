#!/usr/bin/env python3
"""CF-200 registry consistency: deterministic offline validation, no network or HP claims."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
class RegistryValidationError(ValueError): pass

def check_registry(data):
    if not isinstance(data,dict) or not isinstance(data.get('tasks'),list):
        raise RegistryValidationError('registry_shape')
    tasks=data['tasks']
    if len(tasks)!=200 or data.get('target')!=200:
        raise RegistryValidationError('target_count')
    mapping={}
    for t in tasks:
        if not isinstance(t,dict) or not isinstance(t.get('id'),str) or t['id'] in mapping:
            raise RegistryValidationError('duplicate_or_invalid_id')
        mapping[t['id']]=t
    verified=0
    for t in tasks:
        ident=t['id']
        deps=t.get('depends_on')
        if not isinstance(deps,list) or len(deps)!=len(set(deps)) or any(d not in mapping or d==ident for d in deps):
            raise RegistryValidationError('invalid_dependencies:'+ident)
        if not isinstance(t.get('authority'),str) or not t['authority'].strip():
            raise RegistryValidationError('missing_authority:'+ident)
        if type(t.get('physical_hp_required')) is not bool:
            raise RegistryValidationError('missing_hp_gate:'+ident)
        if t.get('status') not in ('planned','verified'):
            raise RegistryValidationError('invalid_status:'+ident)
        if t['status']=='verified':
            verified+=1
            if not isinstance(t.get('evidence'),str) or len(t['evidence'].strip())<12:
                raise RegistryValidationError('missing_evidence:'+ident)
    color={}
    def visit(ident):
        if color.get(ident)==1:raise RegistryValidationError('dependency_cycle:'+ident)
        if color.get(ident)==2:return
        color[ident]=1
        for dep in mapping[ident]['depends_on']:visit(dep)
        color[ident]=2
    for ident in mapping:visit(ident)
    if type(data.get('completed')) is not int or data['completed']!=verified:
        raise RegistryValidationError('completed_mismatch')
    return {'verified':verified,'planned':len(tasks)-verified,'target':len(tasks)}

def main():
    result=check_registry(json.loads((ROOT/'registry.json').read_text(encoding='utf-8')))
    print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
