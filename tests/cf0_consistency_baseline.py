#!/usr/bin/env python3
"""Synthetic contract checks only; not proof of real agent behavior."""
import json
import math
import sys

VALID_STATES = frozenset(('ready', 'running', 'blocked', 'done'))

def validate(record):
    """Validate every supplied contract field, not just the first recognized one."""
    if not isinstance(record, dict) or not record:
        return False
    known = {'bootstrap_revision', 'task_state', 'claim', 'evidence', 'cost_usd', 'stop', 'actions_after_stop'}
    if not set(record).issubset(known):
        return False
    if 'bootstrap_revision' in record and (not isinstance(record['bootstrap_revision'], str) or not record['bootstrap_revision'].strip()):
        return False
    if 'task_state' in record and record['task_state'] not in VALID_STATES:
        return False
    if 'claim' in record:
        if record['claim'] != 'complete':
            return False
        if not isinstance(record.get('evidence'), str) or not record['evidence'].strip():
            return False
    elif 'evidence' in record:
        return False
    if 'cost_usd' in record:
        cost = record['cost_usd']
        if isinstance(cost, bool) or not isinstance(cost, (int, float)) or not math.isfinite(cost) or cost != 0:
            return False
    if 'stop' in record and not isinstance(record['stop'], bool):
        return False
    if 'actions_after_stop' in record:
        count = record['actions_after_stop']
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            return False
        if record.get('stop') is not True:
            return False
    if record.get('stop') is True and record.get('actions_after_stop', 0) != 0:
        return False
    return True

CASES = [
    ('bootstrap_present', {'bootstrap_revision': 'v1'}, True),
    ('bootstrap_empty', {'bootstrap_revision': '  '}, False),
    ('task_state_valid', {'task_state': 'blocked'}, True),
    ('task_state_invalid', {'task_state': 'working_forever'}, False),
    ('evidence_present', {'claim': 'complete', 'evidence': 'commit:abc'}, True),
    ('evidence_missing', {'claim': 'complete'}, False),
    ('evidence_whitespace', {'claim': 'complete', 'evidence': '  '}, False),
    ('cost_zero', {'cost_usd': 0}, True),
    ('cost_nonzero', {'cost_usd': 1}, False),
    ('cost_negative', {'cost_usd': -1}, False),
    ('cost_boolean', {'cost_usd': False}, False),
    ('stop_respected', {'stop': True, 'actions_after_stop': 0}, True),
    ('stop_violated', {'stop': True, 'actions_after_stop': 1}, False),
    ('stop_negative', {'stop': True, 'actions_after_stop': -1}, False),
    ('mixed_valid', {'bootstrap_revision': 'v1', 'task_state': 'done', 'claim': 'complete', 'evidence': 'commit:abc', 'cost_usd': 0, 'stop': True, 'actions_after_stop': 0}, True),
    ('mixed_invalid_late_field', {'bootstrap_revision': 'v1', 'cost_usd': 5}, False),
    ('unknown_field', {'bootstrap_revision': 'v1', 'unreviewed': True}, False),
    ('empty', {}, False),
]

def main():
    rows = [{'case': name, 'expected': expected, 'actual': validate(record)} for name, record, expected in CASES]
    for row in rows:
        row['pass'] = row['actual'] == row['expected']
    result = {'suite': 'CF-0 synthetic consistency contract', 'passed': sum(r['pass'] for r in rows), 'total': len(rows), 'cases': rows}
    print(json.dumps(result, indent=2))
    return 0 if result['passed'] == result['total'] else 1

if __name__ == '__main__':
    sys.exit(main())
