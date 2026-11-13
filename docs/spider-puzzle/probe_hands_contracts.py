#!/usr/bin/env python3
"""Isolated RED probes for original v3.3.14 spider/hands.py (no OS I/O).

These tests PASS when the original unsafe behavior is reproduced. Passing
is evidence of a defect, NOT acceptance that the actuator is safe to ship.

Run from the same directory as the public Spider puzzle HTML:
    python probe_hands_contracts.py
"""
import ast
import json
import re
import types
import typing
import unittest
from pathlib import Path

BOARD = Path(__file__).with_name('index.html')
EXPECTED = '438c442a781b028b1ef8fc336585e540e14dfb5e3828a8d2e8ab35857e2dec24'


def load_methods(names, sender=None, windows=True):
    doc = BOARD.read_text(encoding='utf-8')
    m = re.search(r'<script id="embedded-data" type="application/json">(.*?)</script>',doc,re.S)
    if not m:
        raise RuntimeError('Missing embedded source map')
    data = json.loads(m.group(1))
    if data['source_sha256'] != EXPECTED:
        raise RuntimeError('Unknown source SHA; refuse mismatched source')
    original = data['sources']['spider/hands.py']
    if not isinstance(original,str):
        raise RuntimeError('Expected full source text')
    # Compile only the requested method AST nodes: no imports, top-level code,
    # hardware binding or application code is loaded.
    tree = ast.parse(original)
    hands = next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='SpiderHands')
    units = [n for n in hands.body if isinstance(n,ast.FunctionDef) and n.name in names]
    if len(units)!=len(names):
        raise RuntimeError('Missing requested methods')
    shell=ast.fix_missing_locations(ast.Module(body=units,type_ignores=[]))
    ns={'Any':typing.Any,'platform':types.SimpleNamespace(system=lambda:'Windows' if windows else 'Linux'),
        'time':types.SimpleNamespace(sleep=lambda _:None),
        '_send_win32_mouse':sender or (lambda *a,**k:True)}
    exec(compile(shell,'spider/hands.py#method-extract','exec'),ns,ns)
    return {name:ns[name] for name in names}

class Authority:
    def __init__(self,fail_on_check=None):
        self.fail_on_check=fail_on_check
        self.calls=0
    def check_interrupt(self):
        self.calls+=1
        if self.calls==self.fail_on_check:
            raise RuntimeError('simulated STOP')

class Hands:
    def __init__(self,authority=None):
        self.authority=authority or Authority()
        self.dry_run_ui=False
        self.action_log=[]
    def _to_abs_coords(self,x,y):
        return x,y

class RedSourceProbes(unittest.TestCase):
    def test_stop_during_drag_leaves_left_button_down(self):
        events=[]
        f=load_methods(['drag'],sender=lambda flags,*args,**kw:events.append(flags) or True)['drag']
        h=Hands(Authority(fail_on_check=2))
        record=f(h,10,10,20,20,steps=3)
        self.assertIn(0x0002,events,events)
        self.assertNotIn(0x0004,events,events)
        self.assertEqual(record['status'],'simulated_dry_run')
        print('REPRODUCED: STOP after leftdown emits no leftup; flags='+repr(events))

    def test_failed_drag_move_skips_left_button_release(self):
        events=[]
        def sender(flags,*args,**kwargs):
            events.append(flags)
            # First movement after button-down fails. With short-circuiting,
            # left-button-up is never attempted.
            return not (len(events)==3)
        f=load_methods(['drag'],sender=sender)['drag']
        record=f(Hands(),10,10,20,20,steps=3)
        self.assertEqual(events[:2],[0x8001,0x0002])
        self.assertNotIn(0x0004,events)
        self.assertEqual(record['status'],'simulated_dry_run')
        print('REPRODUCED: failed intermediate move skips leftup')

    def test_failed_focus_still_pastes_into_current_active_window(self):
        events=[]
        f=load_methods(['paste_via_clipboard'])['paste_via_clipboard']
        h=Hands()
        h.set_clipboard=lambda text:{'provenance':'memory_clipboard'}
        h.focus_window=lambda window:{'executed_os_input':False,'status':'simulated_dry_run'}
        h.press_shortcut=lambda s:(events.append(s) or {'executed_os_input':True})
        record=f(h,'EXAMPLE',target_window='EXPECTED TARGET')
        self.assertEqual(events,['ctrl+v'])
        self.assertEqual(record['status'],'completed')
        self.assertFalse(record['focus_result']['executed_os_input'])
        print('REPRODUCED: paste reports completed despite failed requested focus')

    def test_invalid_mouse_button_silently_defaults_to_left(self):
        events=[]
        f=load_methods(['move_and_click'],sender=lambda flags,*args,**kw:events.append(flags) or True)['move_and_click']
        record=f(Hands(),5,5,button='bogus')
        self.assertEqual(events,[0x8001,0x0002,0x0004])
        self.assertEqual(record['status'],'completed')
        self.assertEqual(record['button'],'bogus')
        print('REPRODUCED: invalid button triggers left-click but claims requested button')

if __name__=='__main__':
    unittest.main(verbosity=2)