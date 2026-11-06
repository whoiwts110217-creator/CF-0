# CF-0 Fast Lane installer - separate from existing relay schedule.
# Run as the Windows user who configured the existing CF-0 read/write relay.
$ErrorActionPreference='Stop'
$taskName='CavemanFocusCF0FastLane'
$root=Join-Path $env:LOCALAPPDATA 'CavemanFocus\CF0Desktop\relay'
$wrapper=Join-Path $root 'cf_public_relay_rw.ps1'
$worker=Join-Path $root 'cf_public_relay.py'
$state=Join-Path $env:LOCALAPPDATA 'CavemanFocus\CF0Relay'
$secret=Join-Path $state 'write_token.dpapi'
if (-not (Test-Path $wrapper) -or -not (Test-Path $worker)) { throw 'Existing CF-0 Desktop relay is missing; original task left unchanged.' }
if (-not (Test-Path $secret)) { throw 'Encrypted writeback credential missing; original task left unchanged.' }
if (-not (Test-Path (Join-Path $state 'allow_notepad.flag'))) { throw 'Notepad local opt-in missing; original task left unchanged.' }
$py=Get-Command py.exe -ErrorAction Stop
$fast=Join-Path $root 'cf_fast_lane.ps1'
# The fast lane calls the EXISTING wrapper; it never stores or reads plaintext credentials.
$body=@'
$ErrorActionPreference='Continue'
$wrapper=Join-Path $PSScriptRoot 'cf_public_relay_rw.ps1'
$mutex=New-Object System.Threading.Mutex($false,'Local\CF0FastLaneSingleInstance')
$held=$false
try {
  try { $held=$mutex.WaitOne(0) } catch [System.Threading.AbandonedMutexException] { $held=$true }
  if (-not $held) { exit 0 }
  while ($true) {
    try {
      & powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $wrapper once *> $null
    } catch { }
    Start-Sleep -Seconds 30
  }
} finally {
  if ($held) { $mutex.ReleaseMutex() }
  $mutex.Dispose()
}
'@
Set-Content -LiteralPath $fast -Value $body -Encoding UTF8
$action=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument ('-NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File "'+$fast+'"') -WorkingDirectory $root
$trigger=New-ScheduledTaskTrigger -AtLogOn -User ([Security.Principal.WindowsIdentity]::GetCurrent().Name)
$settings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Seconds 0) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -MultipleInstances IgnoreNew -StartWhenAvailable
$principal=New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$existing=Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) {
  Set-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal | Out-Null
} else {
  Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description 'CF-0 fast lane, checks every 30 seconds; original relay unchanged' | Out-Null
}
Start-ScheduledTask -TaskName $taskName
Write-Host 'FAST_LANE=INSTALLED_AND_STARTED'
Write-Host 'INTERVAL_SECONDS=30'
Write-Host 'AUTO_START=AT_WINDOWS_SIGN_IN'
Write-Host 'ORIGINAL_RELAY=UNCHANGED'
Write-Host 'NOTE=Fast lane runs only while this user is signed in and HP is awake.'
Write-Host 'NOTE=Check task status and GitHub receipts to verify unattended execution.'
