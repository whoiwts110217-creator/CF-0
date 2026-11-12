# CF-0 Spider — Cross-version source recovery audit (2026-11-12)

**Scope:** public-safe derived technical evidence from the owner's private Spider archive collection. **Creator/developer:** David Smith. **Designated intended owner/beneficiary:** Kiara Lynn Rose Smith; this is not evidence of completed legal transfer. No private ZIP, user path, screenshot, credential, contacts, payment data, or transcript is published here.

## Important correction

**Version numbers do not form one linear release sequence.** Desktop 0.1–0.15, Unified Fresh/WholePC 1.1–1.3, Unified System 2.0 and Unified System 3.3.x are distinct branches. The later Integrated 1.3.1 window pilot is **not a successor to Unified System 3.3.x**. Do not discard the broad 3.3 branch on the basis of the 1.3.1 label.

**Archive inventory:** 70 Spider ZIP Library entries across 55 distinct filenames; 45 distinct-filename Library ZIPs materialized and inspected plus one accessible 3.3.3 conversation ZIP. All 46 inspected ZIPs passed archive CRC checks and they represent 40 different binary contents. Ten named Library ZIPs could not be materialized because raw access was unavailable; those exact historical bytes remain uninspected. The owner has a separate private machine-readable 46-archive SHA/duplicate index. An actual **3.3.4 archive was not recovered**, despite an earlier Gemini-reported test count.

## Independently rerun source tests

| Branch | Container test outcome | Device limit |
| --- | --- | --- |
| Unified System **3.3.3 Canonical** | 245/245 Python tests, 78/78 manifest hashes, 66 compilation checks | No physical Windows/Chrome acceptance |
| Unified System **3.3.1 Windows repair candidate** | 228/228 tests, 74 manifest hashes | No physical Windows 3.15 acceptance |
| Unified System **3.3 Canonical** | 215/215 tests using simulated Xvfb display | Initial headless GUI test required display; GUI-backed rerun passed |
| WholePC **1.3.4 PATCHED** | 185/185 tests, 66 hashes, 42 compilation checks | Windows UIA and native input not observed on HP |
| Integrated **1.3.1 Window Pilot** | 132/132 tests, 57 hashes, 41 compilation checks | Native Win32 minimize/animation simulated |
| Desktop **0.15** | 168 tests passed; 3 skipped | No signed-in Chrome / HP |
| Desktop **0.15 AIReview** | 182 tests passed | Tests include local fixtures, not live external navigation |
| Unified System **2.0** | 19 tests passed | Does not authorize its HTTP control interface |
| Experimental **3.3.3 + sensitive-control fix** | 248/248 tests, 79 hashes, 67 compilation checks | Isolated **candidate**, not a released/installed version |

## What is worth recovering

| Reference | Useful source | Decision |
| --- | --- | --- |
| **3.3.3** | `spider/self_prompter.py`, `hands.py`, `eyes.py`, `learning.py`, `desktop_perception.py`, `http_guard.py`, GUI and live-browser adapters | **Best architectural base candidate**, but not permission to run unrestricted autopilot |
| **WholePC 1.3.4** | Improved `desktop_perception.py`: selected-window HWND/PID/title pinning, exact post-restore verification, password-field checks, native Edit/RichEdit discovery when UIA returns only panes | **Selective port into 3.3.3**, preserve regression tests |
| **Integrated 1.3.1** | `spider/window_pilot.py`: selected window geometry, visible spider walk toward titlebar, owner-approved minimize, fresh `IsIconic` result | **Port as optional GUI skill**; do not overwrite more complete backend |
| **Desktop 0.15** | Chrome pairing/heartbeat, STOP-race regression tests, bounded projects/skills and screenshot support | **Reuse selected adapters/tests**; do not launch two Chrome writers |
| **Desktop 0.15 AIReview** | `spider_exchange.py`, `spider_web_bridge.py`, `spider_web_crawler.py` | Valuable candidate modules; isolate, audit scope and respect public-host restrictions |
| **Unified Fresh/WholePC older releases** | Browser reentry, send recovery, private Screen Eyes, source patch lab and rollback | Many already in 3.3.3; diff before cherry-picking |
| **Unified System 2.0** | Offline Sphere presentation and portions of learning/eye algorithms | **Reject old permissive HTTP control route**, preserve only non-actuating components |

## Reproduced hazards and boundaries

1. **Sensitive field identification defect in 3.3.3:** `safe_control` checks the nonblank visible control name **instead of also checking** its `automation_id`. A synthetic Edit with visible name `Continue` and internal ID `passwordInput` was wrongly accepted for typing; a payment-field ID was also accepted when masked by an ordinary visible name. WholePC 1.3.4 already checks both. A private **isolated minimal correction** plus three additional regression tests passed **248/248**, but is **not installed or released** and does not solve the other issues below.
2. **Generated Python/shell risk in 3.3.3:** `spider/self_prompter.py` can dispatch generated code, shell commands, file writes and whole-PC input. `spider/hands.py` executes supplied Python in a subprocess **without per-action approval in that function**, and shell approval relies on a small blacklist of suspicious strings, not a safe command capability set. A subprocess is **not a secure sandbox**. Do not enable unsupervised full-PC command execution until owner-scoped approval, trusted workspace bounds and explicit code-review gates exist.
3. **Older 2.0 HTTP design:** `spider/gui_desktop.py` returns `Access-Control-Allow-Origin: *` and offers POST controls such as `/api/execute`, `/api/resume` and `/api/pc-action`. Do not reuse this as an unauthenticated browser-callable control interface. Use later guarded designs.
4. **Vision truth:** Screenshot capture, accessibility metadata, DOM summaries, motion hashes and clipboard shortcuts exist; **general semantic screenshot interpretation and universal site-specific keyboard verification are not established**. Control-tree availability varies with app and minimization state.
5. **Autonomy truth:** 3.3.3 has SQLite learning and a self-prompt loop, but without active external browser/model response it uses a **locally hardcoded fallback reply**. That exercises the pipeline; it is not evidence ChatGPT/Gemini answered or that source repaired itself.
6. **Acceptance truth:** passing isolated source tests is not live HP mouse/keyboard success, signed-in browser operation, autonomous three-provider communication, verified income or production deployment. No such claims are made.

## One-app next integration order

1. Preserve original 3.3.3 as immutable rollback/reference. No wholesale replacement of the installed Spider or private state.
2. Integrate WholePC 1.3.4's sensitive metadata, window identity, minimized restoration and real native editor handling; add safety regression tests, rehash, rerun tests.
3. Integrate 1.3.1 window-walk animation with exact target, consent and native minimize postcondition. One Tk GUI, not a second Spider.
4. Reuse Desktop 0.15 Chrome pairing/STOP and peer-review/crawler components only where they do not introduce duplicate browser controllers or remote control.
5. Disable GPT-generated arbitrary Python/shell and dangerous OS actions by default; require specific owner approval and bounded action scopes.
6. Add private screenshot-to-clipboard handling, semantic-interpretation bridge and post-action checks separately, then perform owner-supervised Windows HP acceptance.

**Evidence status:** source recovery, archive comparison, isolated tests and a targeted safety experiment completed. **Not done:** combined production release, HP installation, live three-assistant execution or financial receipts. Keep any private artifacts private and add dated evidence rather than changing historical test claims.
