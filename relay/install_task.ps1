# cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
# CF-0 tokenless public-inbox polling, signed-in Windows user only.
param([ValidateSet('install','status','remove')][string]$Mode='install')
$ErrorActionPreference='Stop'
$task='CavemanFocusCF0Relay'
$root=Split-Path -Parent $PSScriptRoot
$python=Join-Path $PSScriptRoot 'cf_public_relay.py'
if ($Mode -eq 'remove') {
    Unregister-ScheduledTask -TaskName $task -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host 'Removed CF-0 relay schedule; no local history deleted.'
    exit 0
}
if ($Mode -eq 'status') {
    Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue | Select-Object TaskName,State | Format-List
    Get-ScheduledTaskInfo -TaskName $task -ErrorAction SilentlyContinue | Select-Object LastRunTime,LastTaskResult,NextRunTime | Format-List
    exit 0
}
if (-not (Test-Path -LiteralPath $python)) { throw 'Missing relay source.' }
$py=Get-Command py.exe -ErrorAction Stop
# Check Python and source syntax before scheduling. Does not contact GitHub.
& $py.Source -3 $python ping-demo
if ($LASTEXITCODE -ne 0) { throw 'Offline relay preflight failed.' }
$user=[Security.Principal.WindowsIdentity]::GetCurrent().Name
$arguments='-3 "'+$python+'" once'
$action=New-ScheduledTaskAction -Execute $py.Source -Argument $arguments -WorkingDirectory $root
$trigger=New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 365)
$principal=New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
$settings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 3) -MultipleInstances IgnoreNew -StartWhenAvailable
Register-ScheduledTask -TaskName $task -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Write-Host 'Scheduled CF-0 public relay every 5 min while signed in. Still requires live HP verification.'
Get-ScheduledTask -TaskName $task | Select-Object TaskName,State | Format-List
