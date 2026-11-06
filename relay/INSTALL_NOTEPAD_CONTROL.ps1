# Owner-run one-time installer. No Git dependency. Does not request or print credentials.
$ErrorActionPreference = 'Stop'
$repo = 'whoiwts110217-creator/CF-0'
$root = Join-Path $env:LOCALAPPDATA 'CavemanFocus\CF0Desktop'
$relay = Join-Path $root 'relay'
$state = Join-Path $env:LOCALAPPDATA 'CavemanFocus\CF0Relay'
New-Item -ItemType Directory -Force -Path $relay,$state | Out-Null
foreach ($name in @('cf_public_relay.py','cf_public_relay_rw.ps1')) {
    $url = "https://raw.githubusercontent.com/$repo/main/relay/$name"
    Invoke-WebRequest -Uri $url -OutFile (Join-Path $relay $name) -UseBasicParsing
}
$flag = Join-Path $state 'allow_notepad.flag'
Set-Content -LiteralPath $flag -Value 'owner_opt_in_notepad_only' -Encoding ASCII
Write-Host 'NOTEPAD_ACTION=INSTALLED_AND_OPTED_IN'
$task = Get-ScheduledTask -TaskName 'CavemanFocusCF0Relay' -ErrorAction SilentlyContinue
if ($null -eq $task) {
    Write-Host 'SCHEDULE=MISSING; existing relay task needs setup before remote actions work.'
    exit 0
}
Write-Host ('SCHEDULE='+$task.State)
Write-Host ('LOGON_TYPE='+$task.Principal.LogonType)
# Redirect the existing task to the updated wrapper; retain its triggers and settings.
$script = Join-Path $relay 'cf_public_relay_rw.ps1'
$arg = '-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "'+$script+'" -Mode once'
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $arg -WorkingDirectory $root
Set-ScheduledTask -TaskName 'CavemanFocusCF0Relay' -Action $action | Out-Null
Write-Host 'RELAY_UPDATED=TRUE'
Write-Host 'Note: Notepad appears only if the scheduled task runs in the signed-in interactive user session.'
Write-Host 'If LOGON_TYPE is Password or S4U, GUI visibility may fail; change task to Run only when user is logged on.'
Write-Host 'A public command must still be issued and its receipt checked.'
