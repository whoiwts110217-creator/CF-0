#!/usr/bin/env python3
"""Verify Spider Puzzle's isolated source pieces; never execute extracted code.

Stdlib-only: python verify_piece_hashes.py [path/to/index.html]
Checks that every AST card's displayed source slice is byte-for-byte the
recorded SHA-256 and byte length, with unique stable IDs and skill paths.
This proves extraction integrity, NOT behavior, safe integration or HP runtime.
"""
import hashlib
import json
from pathlib import Path
import re
import sys
from collections import Counter

EXPECTED_SOURCE_ARCHIVE = '438c442a781b028b1ef8fc336585e540e14dfb5e3828a8d2e8ab35857e2dec24'
DATA_RE = re.compile(r'<script id="embedded-data" type="application/json">(.*?)</script>', re.S)


def verify(html_path):
    raw = Path(html_path).read_text(encoding='utf-8')
    match = DATA_RE.search(raw)
    if not match:
        raise ValueError('Missing embedded source-backed puzzle data')
    data = json.loads(match.group(1))
    if data.get('source_sha256') != EXPECTED_SOURCE_ARCHIVE:
        raise ValueError('Spider source archive fingerprint mismatch')
    sources = data['sources']
    pieces = data['pieces']
    seen_ids, seen_skill_paths = set(), set()
    failures = []
    categories = Counter()
    for piece in pieces:
        card_id = piece['id']
        categories[piece['kind']] += 1
        file_path = piece['path']
        line, end = piece['line'], piece['end']
        skill_file = piece['skill_file']
        if card_id in seen_ids or skill_file in seen_skill_paths:
            failures.append((card_id, 'duplicate card ID or skill path'))
        seen_ids.add(card_id)
        seen_skill_paths.add(skill_file)
        if card_id != f"{file_path}:{line}:{piece['kind']}:{piece['symbol']}":
            failures.append((card_id, 'unstable source-locator ID'))
        if file_path not in sources or not isinstance(line, int) or not isinstance(end, int):
            failures.append((card_id, 'missing source or invalid line numbers'))
            continue
        lines = sources[file_path].splitlines(keepends=True)
        if not (1 <= line <= end <= len(lines)):
            failures.append((card_id, 'source line range out of bounds'))
            continue
        excerpt = ''.join(lines[line - 1:end]).encode('utf-8')
        if len(excerpt) != piece['bytes']:
            failures.append((card_id, 'source byte-length mismatch'))
        if hashlib.sha256(excerpt).hexdigest() != piece['sha256']:
            failures.append((card_id, 'source SHA-256 mismatch'))
    if len(sources) != 94 or len(pieces) != 1289:
        failures.append(('inventory', 'expected 94 source files and 1289 code pieces'))
    if failures:
        preview = '\n'.join(f'  {item}: {reason}' for item, reason in failures[:15])
        raise ValueError(f'{len(failures)} integrity failures:\n{preview}')
    return len(sources), len(pieces), categories


def main(argv):
    candidate = Path(argv[1]) if len(argv) > 1 else Path(__file__).with_name('index.html')
    try:
        source_count, piece_count, counts = verify(candidate)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1
    print(f'PASS: {piece_count}/{piece_count} source-backed pieces match SHA-256 and bytes; '
          f'{source_count} source files; kinds={dict(counts)}')
    print('LIMIT: static extraction integrity only; no runtime/behavior confirmation')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
