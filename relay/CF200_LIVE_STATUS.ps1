# Caveman Focus CF-200 owner-local live status window (opt-in).
# No credentials, local commands from GitHub, or remote HP control.
# Run on the HP under the owner's Windows account: powershell.exe -NoProfile -File .\relay\CF200_LIVE_STATUS.ps1
param([ValidateRange(15,300)][int]$RefreshSeconds=30)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$base='https://raw.githubusercontent.com/whoiwts110217-creator/CF-0/main'
$api='https://api.github.com/repos/whoiwts110217-creator/CF-0'
$state=Join-Path $env:LOCALAPPDATA 'CavemanFocus\CF200Status'
New-Item -ItemType Directory -Path $state -Force | Out-Null
$file=Join-Path $state 'CF200_LIVE_STATUS.txt'
$form=New-Object Windows.Forms.Form
$form.Text='Caveman Focus CF-200 - live status (owner-local)'
$form.Width=850
$form.Height=580
$view=New-Object Windows.Forms.TextBox
$view.Multiline=$true
$view.ReadOnly=$true
$view.ScrollBars='Both'
$view.WordWrap=$false
$view.Dock='Fill'
$view.Font=New-Object Drawing.Font('Consolas',11)
$form.Controls.Add($view)
$timer=New-Object Windows.Forms.Timer
$timer.Interval=$RefreshSeconds*1000
$refresh={
  $lines=New-Object System.Collections.Generic.List[string]
  $lines.Add('CAVEMAN FOCUS - CF-200 LIVE STATUS')
  $lines.Add('Owner: Kiara Lynn Rose Smith')
  $lines.Add('Local refresh: '+(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'))
  $lines.Add('Source: public CF-0 GitHub; NOT physical HP scheduler proof')
  $lines.Add('')
  try {
    $registry=Invoke-RestMethod -Uri ($base+'/automation_200/registry.json') -TimeoutSec 12
    $lines.Add(('Verified tasks: {0} / {1}' -f $registry.completed,$registry.target))
    $commit=Invoke-RestMethod -Uri ($api+'/commits/main') -Headers @{'User-Agent'='CF200-Owner-Status'} -TimeoutSec 12
    $lines.Add('Latest public commit: '+$commit.sha.Substring(0,12))
    $lines.Add('Commit message: '+(($commit.commit.message -split "`n")[0]))
    $lines.Add('Commit URL: '+$commit.html_url)
    $runs=Invoke-RestMethod -Uri ($api+'/actions/runs?per_page=5') -Headers @{'User-Agent'='CF200-Owner-Status'} -TimeoutSec 12
    foreach($run in @($runs.workflow_runs) | Select-Object -First 3) {
      $lines.Add(('CI: {0} | {1} | {2}' -f $run.name,$run.status,$run.conclusion))
    }
    $probe='1bd3a644-9b80-4d05-8cb1-7043c7853d54'
    try {
      $receipt=Invoke-RestMethod -Uri ($base+'/command_queue/receipts/'+$probe+'.json') -TimeoutSec 10
      $lines.Add(('Scheduled-probe public receipt: {0} (HP schedule unverified)' -f $receipt.status))
    } catch {
      $lines.Add('Scheduled-probe public receipt: not found or unreachable')
    }
    $lines.Add('Next: verify scheduled HP task independently; continue safe CF-200 work')
  } catch {
    $lines.Add('Public GitHub fetch unavailable; showing last local refresh attempt.')
    $lines.Add('Check network connectivity and retry automatically.')
  }
  $txt=$lines -join [Environment]::NewLine
  $view.Text=$txt
  [IO.File]::WriteAllText($file,$txt,[Text.Encoding]::UTF8)
}
$timer.Add_Tick($refresh)
$form.Add_Shown({ & $refresh; $timer.Start() })
$form.Add_FormClosed({ $timer.Stop();$timer.Dispose() })
[void]$form.ShowDialog()
