# CF-0 owner-facing Notepad install gate -- currently intentionally fail-closed.
# The older installer downloaded mutable main-branch scripts, changed the
# scheduler and printed INSTALLED_AND_OPTED_IN despite a missing open_notepad
# relay action. Its original content remains available through Git history.
#
# Until a reviewed, owner-approved, version-pinned Notepad handler exists,
# this command MUST NOT write local flags, replace scripts or change tasks.
# Do not interpret this refusal as evidence that a former Notepad feature
# was never present; its regression remains open in the capability contract.
$ErrorActionPreference = 'Stop'
Write-Output 'NOTEPAD_ACTION=BLOCKED_NOT_SUPPORTED'
Write-Output 'REASON=Current public relay does not implement the owner-approved open_notepad action.'
Write-Output 'LOCAL_CHANGES=NONE'
Write-Output 'RESTORE_GATE=Reviewed handler, owner approval, pinned package, local opt-in, interactive HP receipt.'
exit 2
