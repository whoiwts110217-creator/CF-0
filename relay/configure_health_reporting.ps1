# CF-0 owner-local health reporting activation. No task creation or remote commands.
# Owner: Kiara Lynn Rose Smith's Caveman Focus
param([ValidateSet('enable','disable','status')][string]$Mode='status')
$ErrorActionPreference='Stop'
$TaskName='CavemanFocusCF0Relay'
$StateDir=Join-Path $env:LOCALAPPDATA 'CavemanFocus\CF0Relay'
$HealthFlag=Join-Path $StateDir 'allow_health_report.flag'
$SecretFile=Join-Path $StateDir 'write_token.dpapi'
$ExpectedWrapper=Join-Path $PSScriptRoot 'cf_public_relay_rw.ps1'
$Snapshot=Join-Path $PSScriptRoot 'cf_hp_health_snapshot.py'
$Publisher=Join-Path $PSScriptRoot 'cf_hp_health_publish.py'

function Get-LocalReadiness {
    $task=Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    $usesThisCheckout=$false
    if ($null -ne $task) {
        # An old checkout's scheduled wrapper must not masquerade as this version.
        $pattern='*'+[Management.Automation.WildcardPattern]::Escape($ExpectedWrapper)+'*'
        $usesThisCheckout=@($task.Actions | Where-Object { $_.Arguments -like $pattern }).Count -gt 0
    }
    return @{
        task_present=($null -ne $task)
        wrapper_current=$usesThisCheckout
        token_file_present=(Test-Path -LiteralPath $SecretFile)
        publisher_present=(Test-Path -LiteralPath $Publisher)
        snapshot_present=(Test-Path -LiteralPath $Snapshot)
        enabled=(Test-Path -LiteralPath $HealthFlag)
    }
}

if ($Mode -eq 'disable') {
    if (Test-Path -LiteralPath $HealthFlag) {
        Remove-Item -LiteralPath $HealthFlag -Force
    }
    Write-Host 'HEALTH_REPORT=DISABLED; relay schedule and saved receipts untouched.'
    exit 0
}
$ready=Get-LocalReadiness
if ($Mode -eq 'status') {
    Write-Host ('HEALTH_REPORT_ENABLED='+$ready.enabled)
    Write-Host ('EXISTING_TASK_PRESENT='+$ready.task_present)
    Write-Host ('CURRENT_CHECKOUT_WRAPPER='+$ready.wrapper_current)
    Write-Host ('WRITEBACK_CONFIGURED='+$ready.token_file_present)
    Write-Host ('HEALTH_SCRIPTS_PRESENT='+($ready.publisher_present -and $ready.snapshot_present))
    Write-Host 'An enabled flag is not proof that the HP published a report.'
    exit 0
}
if (-not $ready.task_present) { throw 'Existing CF-0 Windows relay task not found. No change made.' }
if (-not $ready.wrapper_current) { throw 'Scheduled relay is not using this checkout; update the existing wrapper before opting in. No change made.' }
if (-not $ready.token_file_present) { throw 'Existing encrypted GitHub writeback is not configured. No change made.' }
if (-not ($ready.publisher_present -and $ready.snapshot_present)) { throw 'Health scripts missing. No change made.' }

# The read-only collector is checked before enabling publication. No network,
# credentials, scheduler settings, or private receipt payloads are printed.
$py=Get-Command py.exe -ErrorAction Stop
$raw=& $py.Source -3 -B $Snapshot 2>$null
if ($LASTEXITCODE -ne 0) { throw 'Local read-only health collector failed. No change made.' }
try {
    $report=($raw -join "`n") | ConvertFrom-Json -ErrorAction Stop
    if ($report.schema -cne 'cf0.hp_health.v1') { throw 'version mismatch' }
    $fields=@($report.PSObject.Properties.Name)
    if ($fields.Count -ne 7) { throw 'unexpected report fields' }
}
catch { throw 'Local collector returned invalid or unexpected data. No change made.' }
New-Item -ItemType Directory -Path $StateDir -Force | Out-Null
Set-Content -LiteralPath $HealthFlag -Value 'owner-opt-in' -Encoding ASCII
Write-Host 'HEALTH_REPORT=OPTED_IN for the existing five-minute scheduled relay.'
Write-Host 'No HP report is claimed until relay/health/latest.json is observed in GitHub.'
Write-Host 'Rollback: double-click DISABLE_CF0_HEALTH_REPORT.bat. No schedule or token was changed.'
