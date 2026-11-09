#!/usr/bin/env python3
"""Read-only, offline comparison of a private CF-0 idea crosswalk with indexed ChatGPT exports.

This is a candidate generator, not a merger or an account/browser controller. Never
publishes private titles, chat IDs, excerpts, or summaries to public CF-0.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys
from urllib.parse import quote

SCHEMA = 'cf0.private_conversation_idea_merge.v2'
REPORT_SCHEMA = 'cf0.private_conversation_reconciliation.v1'
STOPWORDS = frozenset('the that this with from into some were they them what have has had about there their would could should without through actual which where after before only user said asks later earlier source original conversation conversations review reviewed related preserved recovered excerpt particular history exact unclear project distinct records summary'.split())
TOKEN = re.compile(r"[a-z0-9]{5,}")


def normalized_title(value: str) -> str:
    return ' '.join(re.findall(r'[a-z0-9]+', value.casefold()))


def cues(value: str, title: str) -> set[str]:
    excluded=set(TOKEN.findall(normalized_title(title))) | STOPWORDS
    return {x for x in TOKEN.findall(value.casefold()) if x not in excluded}


def validate_map(raw: object) -> dict:
    if not isinstance(raw, dict) or raw.get('schema') != SCHEMA:
        raise ValueError('expected_cf0_private_merge_v2')
    atlas=raw.get('original_atlas_items')
    units=raw.get('conversation_provenance_crosswalk')
    if not isinstance(atlas,list) or not atlas or not isinstance(units,list) or not units or len(units)>10000:
        raise ValueError('invalid_atlas_or_crosswalk')
    ids=[]
    for a in atlas:
        if not isinstance(a,dict) or not isinstance(a.get('id'),str) or not re.fullmatch(r'[A-Z0-9][A-Z0-9_-]{2,63}',a['id']):
            raise ValueError('invalid_project_identity')
        ids.append(a['id'])
    if len(ids)!=len(set(ids)):
        raise ValueError('duplicate_atlas_id')
    unit_ids=[]
    for u in units:
        if not isinstance(u,dict) or any(not isinstance(u.get(key),str) or not u[key] for key in ('source_unit_id','conversation_title','source_sha256')):
            raise ValueError('invalid_source_unit')
        if u.get('original_chat_id') not in (None,'') or u.get('owner_accepted') is not False:
            raise ValueError('this_tool_accepts_unresolved_secondary_links_only')
        if not re.fullmatch(r'[0-9a-f]{64}',u['source_sha256']):
            raise ValueError('invalid_secondary_source_digest')
        if not isinstance(u.get('related_project_ids'),list) or any(pid not in ids for pid in u['related_project_ids']):
            raise ValueError('unknown_project_identity')
        unit_ids.append(u['source_unit_id'])
    if len(unit_ids)!=len(set(unit_ids)):
        raise ValueError('duplicate_source_unit')
    return raw



def verify_secondary_review(data: dict, path: Path) -> dict:
    """Verify the exact source bytes when the owner supplies the original review file."""
    refs={unit['source_sha256'] for unit in data['conversation_provenance_crosswalk']}
    if len(refs)!=1:
        raise ValueError('multiple_secondary_source_digests_require_separate_review_files')
    observed=hashlib.sha256(path.read_bytes()).hexdigest()
    expected=next(iter(refs))
    if observed!=expected:
        raise ValueError('secondary_review_digest_mismatch')
    return {'provided':True,'sha256_verified':True,'sha256':observed}


def open_readonly_db(path: Path) -> sqlite3.Connection:
    path=path.expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError('private_index_missing_import_original_export_first')
    # URI read-only: cannot initialize or mutate even if application code regresses.
    db=sqlite3.connect('file:'+quote(str(path),safe='/')+'?mode=ro',uri=True,timeout=10)
    db.row_factory=sqlite3.Row
    required={'conversations':{'source_id','conversation_id','title'},
              'messages':{'source_id','conversation_id','body','role'},
              'import_status':{'source_id','status'}}
    for table,fields in required.items():
        actual={row['name'] for row in db.execute(f'PRAGMA table_info({table})')}
        if not fields.issubset(actual):
            db.close()
            raise ValueError('unsupported_private_continuity_schema')
    return db


def compare(map_data: dict, db: sqlite3.Connection|None) -> dict:
    data=validate_map(map_data)
    units=data['conversation_provenance_crosswalk']
    rows=[]
    if db is not None:
        rows=db.execute('''SELECT c.source_id,c.conversation_id,c.title,
                         COALESCE(s.status,'unknown') AS import_state
                         FROM conversations c LEFT JOIN import_status s ON s.source_id=c.source_id
                         ORDER BY c.title,c.conversation_id,c.source_id''').fetchall()
    title_index={}
    for row in rows:
        if row['import_state']!='complete':
            continue # Never promote rows from partial or unknown imports.
        key=normalized_title(row['title'])
        if key:
            title_index.setdefault(key,{}).setdefault(row['conversation_id'],[]).append(row['source_id'])
    counts={'original_export_conversations_available':len({r['conversation_id'] for r in rows if r['import_state']=='complete'}),
            'source_units':len(units),'candidate_units':0,'title_only_units':0,
            'ambiguous_units':0,'no_title_match_units':0,'approved_links':0}
    results=[]
    for u in units:
        title=u['conversation_title']
        hits=title_index.get(normalized_title(title),{})
        candidates=[]
        for cid,source_ids in sorted(hits.items()):
            message_parts=[]
            for sid in source_ids[:3]:
                res=db.execute('''SELECT substr(body,1,4000) AS body FROM messages
                                   WHERE source_id=? AND conversation_id=? AND role='user'
                                   ORDER BY sent_at,message_id LIMIT 200''',(sid,cid)).fetchall()
                message_parts.extend(r['body'] or '' for r in res)
            content=' '.join(message_parts).casefold()
            matched=sorted(t for t in cues(u.get('review_summary',''),title) if re.search(r'(?<![a-z0-9])'+re.escape(t)+r'(?![a-z0-9])',content))
            candidates.append({'conversation_id':cid, 'export_source_ids':sorted(source_ids),
                               'evidence':'title_plus_text_cues' if len(matched)>=2 else 'title_only',
                               'matched_cues':matched[:12], 'owner_accepted':False})
        if not candidates:status='no_primary_title_match'
        elif len(candidates)>1:status='ambiguous_multiple_originals'
        elif candidates[0]['evidence']=='title_plus_text_cues':status='candidate_requires_original_review'
        else:status='title_only_unverified'
        if candidates:counts['candidate_units']+=1
        if status=='title_only_unverified':counts['title_only_units']+=1
        if status=='ambiguous_multiple_originals':counts['ambiguous_units']+=1
        if status=='no_primary_title_match':counts['no_title_match_units']+=1
        results.append({'source_unit_id':u['source_unit_id'],'secondary_title':title,
                        'related_project_ids':u['related_project_ids'],
                        'match_status':status,'candidate_originals':candidates,
                        'merge_approved':False,'original_quote_checked':False})
    return {'schema':REPORT_SCHEMA,'private':True,'generated_at_utc':datetime.now(timezone.utc).isoformat(),
            'mode':'read_only_proposals_only','source_merge_id':data['continuity_id'],
            'counts':counts,'matches':results,
            'identity_collision': 'Historic AUTO-08 two-account bridge versus modern Chrome continuation; do not auto-collapse.',
            'next_action':'Review full original content and explicit user corrections before any project-to-chat approval.',
            'limits':['No original ChatGPT account access.','Title similarity is not identity verification.',
                      'No modifications to the 62-entry atlas, original exports, or CF-200.']}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--merge-map',type=Path,required=True,help='Private CF0 conversation idea map v2 JSON')
    parser.add_argument('--index',type=Path,help='Existing private continuity.sqlite3; omit for missing-export readiness audit')
    parser.add_argument('--secondary-review',type=Path,help='Optional original secondary review file; its SHA-256 must match every crosswalk unit')
    parser.add_argument('--output',type=Path,help='Optional PRIVATE JSON output path outside public CF-0 repository')
    args=parser.parse_args(argv)
    try:
        source=validate_map(json.loads(args.merge_map.read_text(encoding='utf-8')))
        review_verified=(verify_secondary_review(source,args.secondary_review) if args.secondary_review else
                         {'provided':False,'sha256_verified':False})
        db=open_readonly_db(args.index) if args.index else None
        try:out=compare(source,db)
        finally:
            if db is not None:db.close()
        out['secondary_review_verification']=review_verified
        payload=json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+'\n'
        if args.output:
            p=args.output.expanduser().resolve()
            # Prevent accidental publication from a repository checkout.
            module_repo=Path(__file__).resolve().parents[1]
            if p==module_repo or module_repo in p.parents:raise ValueError('private_report_must_stay_outside_source_tree')
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(payload,encoding='utf-8')
            print(json.dumps({'saved_private_report':str(p),'counts':out['counts']}))
        else:print(payload,end='')
        return 0
    except (ValueError,FileNotFoundError,sqlite3.Error,json.JSONDecodeError) as e:
        print('crosswalk_error: '+str(e),file=sys.stderr)
        return 2

if __name__=='__main__':raise SystemExit(main())