#!/usr/bin/env python3
"""Offline, stdlib-only integrity checks for the published Spider Puzzle HTML.

Usage: python docs/spider-puzzle/verify_board.py
Requires no packages, internet, login, or execution of extracted Spider skills.
"""
from collections import Counter
from pathlib import Path
import json
import re
import unittest

HTML = Path(__file__).with_name('index.html')
EXPECTED_SOURCE_SHA = '438c442a781b028b1ef8fc336585e540e14dfb5e3828a8d2e8ab35857e2dec24'

class PuzzleIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML.read_text(encoding='utf-8')
        match = re.search(r'<script id="embedded-data" type="application/json">(.*?)</script>', cls.html, re.S)
        if not match:
            raise ValueError('Missing embedded puzzle data')
        cls.data = json.loads(match.group(1))
        cls.ids = {p['id'] for p in cls.data['pieces']}

    def test_source_binding(self):
        self.assertEqual(self.data['source_sha256'], EXPECTED_SOURCE_SHA)
        self.assertEqual(self.data['dep_layout']['source_zip_sha256'], EXPECTED_SOURCE_SHA)

    def test_piece_id_uniqueness(self):
        self.assertEqual(len(self.ids), len(self.data['pieces']))
        self.assertEqual(len(self.ids), 1289)

    def test_piece_kinds(self):
        kinds = Counter(p['kind'] for p in self.data['pieces'])
        self.assertEqual(kinds['FILE'], 94)
        self.assertEqual(kinds['FUNCTION'], 1007)
        self.assertEqual(kinds['CLASS'], 181)
        self.assertEqual(sum(kinds.values())-94-1007-181, 7)

    def test_structural_summaries_not_overstated(self):
        summaries = [p for p in self.data['pieces'] if str(p['purpose_evidence']).startswith('STATIC-')]
        self.assertEqual(len(summaries), 1036)
        self.assertFalse(any(p['purpose'].startswith('Purpose inferred from name:') for p in self.data['pieces']))
        self.assertIn('NO HP RUNTIME CLAIM', self.data['v2_audit']['evidence_scope'])

    def test_edge_types_and_endpoints(self):
        edges = self.data['dep_edges']
        self.assertEqual(len(edges), 632)
        self.assertTrue(all(e['from'] in self.ids and e['to'] in self.ids for e in edges))
        self.assertEqual(Counter(e['evidence_level'] for e in edges), Counter({'STATIC-SOURCE':626,'HYPOTHESIS':6}))
        self.assertEqual(sum(bool(e['windows_hwnd_sendinput_boundary']) for e in edges), 164)

    def test_dependency_layout(self):
        layout = self.data['dep_layout']
        self.assertEqual(len(layout['nodes']), 94)
        self.assertEqual(len(layout['links']), 210)
        ids = {n['id'] for n in layout['nodes']}
        self.assertEqual(len(ids), 94)
        self.assertTrue(ids <= self.ids)
        self.assertTrue(all(x['from'] in ids and x['to'] in ids for x in layout['links']))
        self.assertTrue(all(0<=n['x'] and n['x']+226<=2300 and 0<=n['y'] and n['y']+120<=2000 for n in layout['nodes']))

    def test_evidence_filter_controls(self):
        for option in ['selected','all','source','hypothesis','boundary','none']:
            self.assertIn('value="'+option+'"', self.html)
        self.assertIn("visible+' of '+paths.length+' connections visible'", self.html)

    def test_matching_arrowheads(self):
        for color in ['#64d7cb','#f0be68','#ee90b7','#8d99b0']:
            self.assertIn(color, self.html)
        self.assertIn("'url(#cf0-arrow-'+provenance+')'",self.html)
        self.assertIn("marker.setAttribute('id','cf0-arrow-'+category)",self.html)

    def test_legacy_layout_storage_isolated(self):
        self.assertIn('cf0_spider_puzzle_ast_v2_',self.html)
        self.assertNotIn("'cf0_spider_puzzle_'+DATA.source_sha256",self.html)

    def test_source_inspector_and_nonexecution_notice(self):
        self.assertIn('id="sourceCode"',self.html)
        self.assertIn('not a standalone executable plugin',self.html)
        self.assertIn('Connecting pieces creates a design hypothesis',self.html)

if __name__ == '__main__':
    unittest.main(verbosity=2)
