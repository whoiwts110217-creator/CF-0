#!/usr/bin/env python3
"""Generate & isolated-test a narrow Spider Hands repair proposal; NEVER apply to Spider.

python docs/spider-puzzle/hands_repair_candidate.py
No physical OS I/O; runs synthetic mocks against only extracted AST methods.
"""
from __future__ import annotations
import ast
import difflib
import json
import re
import types
import typing
import unittest
from pathlib import Path

HTML=Path(__file__).with_name('index.html')
SHA='438c442a781b028b1ef8fc336585e540e14dfb5e3828a8d2e8ab35857e2dec24'


def original_source():
    html=HTML.read_text(encoding='utf-8')
    m=re.search(r'<script id="embedded-data" type="application/json">(.*?)</script>',html,re.S)
    if not m: raise RuntimeError('Missing puzzle source')
    data=json.loads(m.group(1))
    if data['source_sha256']!=SHA: raise RuntimeError('Wrong source ZIP fingerprint; refusing patch')
    return data['sources']['spider/hands.py']


def update_method(source, name, replacements):
    lines=source.splitlines(keepends=True)
    tree=ast.parse(source)
    cl=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='SpiderHands')
    func=next(n for n in cl.body if isinstance(n,ast.FunctionDef) and n.name==name)
    start,end=func.lineno-1,func.end_lineno
    chunk=''.join(lines[start:end])
    for old,new in replacements:
        if chunk.count(old)!=1: raise RuntimeError('Patch anchor mismatch in '+name)
        chunk=chunk.replace(old,new,1)
    lines[start:end]=[chunk]
    modified=''.join(lines)
    ast.parse(modified)
    return modified


def patch(source):
    source=update_method(source,'drag',[(
'''                ok = _send_win32_mouse(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, ax1, ay1)
                ok = ok and _send_win32_mouse(MOUSEEVENTF_LEFTDOWN, ax1, ay1)
                for i in range(1, max(1, steps) + 1):
                    self.authority.check_interrupt()
                    ix = int(ax1 + (ax2 - ax1) * (i / max(1, steps)))
                    iy = int(ay1 + (ay2 - ay1) * (i / max(1, steps)))
                    ok = ok and _send_win32_mouse(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, ix, iy)
                    time.sleep(0.01)
                ok = ok and _send_win32_mouse(MOUSEEVENTF_LEFTUP, ax2, ay2)
                executed_native = ok''',
'''                ok = _send_win32_mouse(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, ax1, ay1)
                leftdown_attempted = False
                try:
                    if ok:
                        leftdown_attempted = True
                        ok = _send_win32_mouse(MOUSEEVENTF_LEFTDOWN, ax1, ay1)
                    for i in range(1, max(1, steps) + 1):
                        self.authority.check_interrupt()
                        if not ok:
                            break
                        ix = int(ax1 + (ax2 - ax1) * (i / max(1, steps)))
                        iy = int(ay1 + (ay2 - ay1) * (i / max(1, steps)))
                        ok = _send_win32_mouse(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, ix, iy)
                        time.sleep(0.01)
                finally:
                    # Release is cleanup, not a new authorized task; it must be
                    # attempted even when STOP interrupts the movement loop.
                    if leftdown_attempted:
                        release_ok = _send_win32_mouse(MOUSEEVENTF_LEFTUP, ax2, ay2)
                        ok = bool(ok and release_ok)
                executed_native = ok'''
    )])
    source=update_method(source,'move_and_click',[(
'''        self.authority.check_interrupt()
        executed_native = False''',
'''        self.authority.check_interrupt()
        if not isinstance(button, str) or button.lower() not in ('left', 'right', 'middle'):
            raise ValueError('Unsupported mouse button')
        button = button.lower()
        executed_native = False'''),(
'''                }.get(button.lower(), (0x0002, 0x0004))''',
'''                }[button]''')])
    source=update_method(source,'paste_via_clipboard',[(
'''        clip_res = self.set_clipboard(text)
        focus_res = None
        if target_window:
            focus_res = self.focus_window(target_window)
            if focus_res["executed_os_input"]:
                time.sleep(0.05)
        paste_res = self.press_shortcut("ctrl+v")''',
'''        focus_res = None
        if target_window:
            focus_res = self.focus_window(target_window)
            if not focus_res.get("executed_os_input", False):
                record = {
                    "type": "paste_via_clipboard",
                    "chars": len(text),
                    "target_window": target_window,
                    "press_enter": press_enter,
                    "clipboard_provenance": "not_modified",
                    "focus_result": focus_res,
                    "executed_os_input": False,
                    "status": "blocked_target_focus",
                }
                self.action_log.append(record)
                return record
            time.sleep(0.05)
        clip_res = self.set_clipboard(text)
        paste_res = self.press_shortcut("ctrl+v")''')])
    return source


def methods(source,names,sender=None,windows=True):
    tree=ast.parse(source)
    cl=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='SpiderHands')
    units=[n for n in cl.body if isinstance(n,ast.FunctionDef) and n.name in names]
    if len(units)!=len(names):raise RuntimeError('Expected methods not found')
    ns={'Any':typing.Any,'platform':types.SimpleNamespace(system=lambda:'Windows' if windows else 'Linux'),
        'time':types.SimpleNamespace(sleep=lambda _x:None),
        '_send_win32_mouse':sender or (lambda *a,**kw:True)}
    exec(compile(ast.fix_missing_locations(ast.Module(body=units,type_ignores=[])),
                 'spider/hands.py#isolated-candidate','exec'),ns,ns)
    return {name:ns[name] for name in names}

class FakeAuthority:
    def __init__(self,stop_on=None):self.n=0;self.stop_on=stop_on
    def check_interrupt(self):
        self.n+=1
        if self.n==self.stop_on:raise RuntimeError('mock STOP')
class FakeHands:
    def __init__(self,authority=None):
        self.authority=authority or FakeAuthority();self.action_log=[];self.dry_run_ui=False
    def _to_abs_coords(self,x,y):return x,y

ORIGINAL=original_source()
CANDIDATE=patch(ORIGINAL)

class CandidateTests(unittest.TestCase):
    def test_stop_releases_after_down(self):
        events=[]
        f=methods(CANDIDATE,['drag'],lambda flags,*a,**kw:events.append(flags) or True)['drag']
        result=f(FakeHands(FakeAuthority(stop_on=2)),10,10,20,20,steps=3)
        self.assertEqual(events,[0x8001,0x0002,0x0004]);self.assertEqual(result['status'],'simulated_dry_run')

    def test_failed_intermediate_move_still_releases(self):
        events=[]
        def sender(flags,*a,**kw):events.append(flags);return len(events)!=3
        f=methods(CANDIDATE,['drag'],sender)['drag']
        result=f(FakeHands(),10,10,20,20,steps=3)
        self.assertEqual(events,[0x8001,0x0002,0x8001,0x0004]);self.assertEqual(result['status'],'simulated_dry_run')

    def test_successful_drag_releases_once(self):
        events=[]
        f=methods(CANDIDATE,['drag'],lambda flags,*a,**kw:events.append(flags) or True)['drag']
        result=f(FakeHands(),10,10,20,20,steps=2)
        self.assertEqual(events,[0x8001,0x0002,0x8001,0x8001,0x0004]);self.assertEqual(result['status'],'completed')

    def test_failed_target_focus_blocks_paste_and_clipboard(self):
        called=[]
        f=methods(CANDIDATE,['paste_via_clipboard'])['paste_via_clipboard']
        h=FakeHands();h.focus_window=lambda s:{'executed_os_input':False}
        h.set_clipboard=lambda s:(called.append('clipboard') or {'provenance':'memory'})
        h.press_shortcut=lambda s:(called.append(s) or {'executed_os_input':True})
        result=f(h,'EXAMPLE',target_window='WRONG')
        self.assertEqual(called,[]);self.assertEqual(result['status'],'blocked_target_focus');self.assertFalse(result['executed_os_input'])

    def test_no_target_still_pastes(self):
        called=[]
        f=methods(CANDIDATE,['paste_via_clipboard'])['paste_via_clipboard']
        h=FakeHands();h.set_clipboard=lambda s:(called.append('clipboard') or {'provenance':'memory'})
        h.press_shortcut=lambda s:(called.append(s) or {'executed_os_input':True})
        result=f(h,'EXAMPLE')
        self.assertEqual(called,['clipboard','ctrl+v']);self.assertEqual(result['status'],'completed')

    def test_invalid_button_rejected_without_events(self):
        events=[]
        f=methods(CANDIDATE,['move_and_click'],lambda flags,*a,**kw:events.append(flags) or True)['move_and_click']
        with self.assertRaises(ValueError):f(FakeHands(),5,5,button='bogus')
        self.assertEqual(events,[])

    def test_valid_left_click_unchanged(self):
        events=[]
        f=methods(CANDIDATE,['move_and_click'],lambda flags,*a,**kw:events.append(flags) or True)['move_and_click']
        result=f(FakeHands(),5,5,button='left')
        self.assertEqual(events,[0x8001,0x0002,0x0004]);self.assertEqual(result['status'],'completed')

    def test_nonwindows_drag_stays_simulated(self):
        events=[]
        f=methods(CANDIDATE,['drag'],lambda flags,*a,**kw:events.append(flags) or True,windows=False)['drag']
        self.assertEqual(f(FakeHands(),5,5,10,10)['status'],'simulated_dry_run');self.assertEqual(events,[])

if __name__=='__main__':
    diff=''.join(difflib.unified_diff(ORIGINAL.splitlines(keepends=True),CANDIDATE.splitlines(keepends=True),
                                     fromfile='a/spider/hands.py',tofile='b/spider/hands.py'))
    if not diff:raise RuntimeError('No patch produced')
    # Print a bounded diff rather than writing into Spider source.
    Path(__file__).with_name('HANDS_REPAIR_CANDIDATE.diff').write_text(diff,encoding='utf-8')
    unittest.main(verbosity=2)