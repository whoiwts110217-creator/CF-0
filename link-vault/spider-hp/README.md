# CF-SPIDER-001 — Free HP Walker (Windows-native Spider)

**Parent:** [existing Spider/Sphere](../README.md), [AUTO-08](../../automation_200/continuation_chrome/README.md), Mission Control, CF-200, UCC-001. This is an **owner-local tool adapter**, not a second dashboard, archive, scheduler or new public HP remote command. The explicit target is the owner's HP Windows machine, and **no paid subscription/API/model/GPU**.

## Cost and capability

[Spider-HP.ps1](Spider-HP.ps1) relies on built-in Windows PowerShell 5.1, .NET UI Automation and Windows Forms. No added package, API, account, paid service, AI model, internet connection, Docker, GPU or local model download is required for its bounded routes. It is free, tiny and offline; real support for a given Windows desktop app depends on its accessibility implementation.

The source can launch **Notepad or Calculator only**, enumerate an application's UI Automation tree, wait for controls, read value lengths (not copy private text into a log), invoke explicitly named controls, type a harmless line into a **uniquely identified, empty and foreground Notepad** field, assert the result, and stop between steps when the local STOP file exists. The plan holds 1–12 reviewed steps, not arbitrary code. Ambiguous selectors, missing window, inaccessible content, unsupported operations, unexpected foreground, nonempty Notepad, sensitive invocation labels and unknown app names are refused. No cursor coordinates are needed.

**Boundary:** it can independently execute and verify a fixed route on the live HP after local owner opt-in. It is not yet an unrestricted natural-language agent deciding arbitrary work, reading private accounts, performing internet postings, spending money or operating when the computer is off. No cloud/chat connection to the HP is created here.

## First owner-side test — no install

Use the existing reviewed CF-0 checkout on the HP. Open Windows PowerShell in the checkout directory. First run the free, no-action preflight and validate the provided plan:

~~~powershell
powershell.exe -NoProfile -File .\link-vault\spider-hp\Spider-HP.ps1 -Mode Preflight
powershell.exe -NoProfile -File .\link-vault\spider-hp\Spider-HP.ps1 -Mode NativeProbe
powershell.exe -NoProfile -File .\link-vault\spider-hp\Spider-HP.ps1 -Mode Validate -PlanPath .\link-vault\spider-hp\notepad-inspect.json
powershell.exe -NoProfile -File .\link-vault\spider-hp\Spider-HP.ps1 -Mode Run -PlanPath .\link-vault\spider-hp\notepad-inspect.json
~~~

Then, on your **unlocked interactive HP**, if you choose, the **one local opt-in** below launches Notepad and reads its accessibility control tree. It does **not** save or transmit a document:

~~~powershell
powershell.exe -NoProfile -File .\link-vault\spider-hp\Spider-HP.ps1 -Mode Run -PlanPath .\link-vault\spider-hp\notepad-inspect.json -Execute -OwnerOptIn
~~~

To request a stop between steps from a second PowerShell window:

~~~powershell
powershell.exe -NoProfile -File .\link-vault\spider-hp\Spider-HP.ps1 -Mode Stop
~~~

STOP persists; you have to inspect and intentionally rearm a later run:

~~~powershell
powershell.exe -NoProfile -File .\link-vault\spider-hp\Spider-HP.ps1 -Mode ResetStop -OwnerOptIn
~~~

A second example plan, [calculator-inspect.json](calculator-inspect.json), launches Calculator and inspects its UI. An optional [notepad-type-safe.json](notepad-type-safe.json) attempts to type a fixed safe test phrase and verify it, **only** when a unique empty Document control exposes readable text and the window is foreground. Newer Notepad builds may refuse; that is a safe outcome, not permission to guess coordinates. We have not run the commands on the owner's HP. Keep sensitive documents closed for the first test. To stop a single long Windows UI Automation call that has stalled, terminate the local PowerShell process: STOP is checked only between operations.

## Multi-app chain: the Spider handles a sequence by itself

The separate [Spider-Multi.ps1](Spider-Multi.ps1) is **not a second operating system**. It composes the same reviewed [Spider-HP.ps1](Spider-HP.ps1) driver with a tiny bounded [default queue](spider-multi-demo.json): launch/inspect Notepad, then launch/inspect Calculator. It validates **all** bundled steps before any live actions, and stops the sequence after an error or STOP. The demo requires no additional software and performs no file writes beyond the owner's explicit STOP flag. Repeated plan names, arbitrary paths, unknown plans and unreviewed app commands are rejected.

First inspect without changing the desktop:

~~~powershell
powershell.exe -NoProfile -File .\link-vault\spider-hp\Spider-Multi.ps1 -Mode Validate
powershell.exe -NoProfile -File .\link-vault\spider-hp\Spider-Multi.ps1 -Mode Run
~~~

Then, only after reviewing the queue and being physically at the unlocked HP, run the two-app sequence:

~~~powershell
powershell.exe -NoProfile -File .\link-vault\spider-hp\Spider-Multi.ps1 -Mode Run -Execute -OwnerOptIn
~~~

To stop, run the same [Spider-HP.ps1](Spider-HP.ps1) STOP command; the master checks the same local file before and between operations. It never starts a Windows service or background task. This is **actual deterministic multi-app navigation code**, but owner-device acceptance and richer adaptive capabilities remain unverified.

## How to grow it into a real multitool Spider

The machine-readable plan schema is cf0.spider.hp_plan.v1 with one explicit allowlisted app and 1–12 steps: launch, inspect, wait, read, invoke, type_safe, assert_contains. Controls are selected using exact UIA AutomationId / Name and optionally ControlType; actions fail on multiple matches. The runner uses no shell-command field, network endpoint or provider keys. This enables deterministic HP tasks without paying for a reasoning model. Expanding to the owner's other applications requires reviewed selector recipes and separate owner-approved allowlisting, not a silent public relay change.

We can optionally substitute [Microsoft WinApp CLI](https://learn.microsoft.com/windows/apps/dev-tools/winapp-cli/) for the low-level UIA layer later. It is free, MIT-licensed, public preview and has richer cross-framework inspection, selection, action, screenshot and verification tooling. The user would install it through the official Microsoft WinGet source only after reviewing resource needs; it is **not** a required dependency now. [Windows UI Automation](https://learn.microsoft.com/windows/win32/winauto/uiauto-controlpatternsoverview) is Microsoft's existing platform-level interface.

Other verified **free software** candidates: [AutoHotkey](https://github.com/AutoHotkey/AutoHotkey) (small keyboard-first scripting, already used in historical HP tests), [pywinauto](https://github.com/pywinauto/pywinauto) (Python Win32/UIA control, extra install), [Robot Framework](https://robotframework.org/) (free workflow automation, extra packages) and [OpenRPA](https://github.com/open-rpa/openrpa). Their **software** can be free; they do not supply a zero-cost unlimited general AI brain by themselves. [OpenClaw](https://docs.openclaw.ai/install) has a fuller agent architecture and experimental Windows computer use, but its model/provider, runtime and low-memory HP affordability are not proven free end-to-end. [UI-TARS Desktop](https://github.com/bytedance/UI-TARS-desktop) is more vision-oriented but local inference is not shown feasible on a constrained 4 GB HP.

## Verify / don't accidentally grant new authority

The existing [Sphere](https://whoiwts110217-creator.github.io/CF-0/link-vault/#owner-actions) will link to this owner-local tool without implying the web page directly controls the HP. The existing AUTO-08 Chrome extension handles authorized one-tab ChatGPT continuation separately: do not duplicate its sends or violate its STOP/unknown-outcome guards. The previously existing public HP relay remains on its existing allowlist and its maintenance hold. The old [Notepad relay installer](../../relay/INSTALL_NOTEPAD_CONTROL.ps1) continues to refuse because it is not currently supported by the public relay. This **separate** locally opted-in navigator is not a restoration of that old remote command.

The existing Windows Actions workflow and source-only tests verify parser, dry run, schema and control guards. They **cannot** establish that the script worked on this specific HP, that windows can be focused, or that Notepad exposes compatible UIA. No personal files, contacts, chat exports, API keys, receipt archives or usernames should enter public GitHub. A script with the STOP file present refuses live action; all native action and inspection is done in the owner's local interactive session. Nothing is auto-started, scheduled or exposed to the network. Rollback: stop and remove this folder; no installed service or edited Windows settings remain. If your local PowerShell execution policy blocks the file, review its exact source and policy rather than broadly disabling machine security.
