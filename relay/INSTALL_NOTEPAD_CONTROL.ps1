# CF-0 owner-facing Notepad install gate.
# The public relay can launch notepad.exe on Windows with no caller arguments.
# This script still does not install anything, change a scheduled task, or
# claim that Notepad works. A real run on the HP PC is unverified.
# Do not write local flags, replace scripts, or download mutable branch files.
$ErrorActionPreference = 'Stop'
Write-Output 'NOTEPAD_ACTION=BLOCKED_NOT_SUPPORTED'
Write-Output 'REASON=Relay source includes open_notepad, but this installer does not launch Notepad, change the HP, or claim a verified run. A real run on the HP PC is unverified.'
Write-Output 'LOCAL_CHANGES=NONE'
Write-Output 'HP_VERIFIED=NO'
exit 2
