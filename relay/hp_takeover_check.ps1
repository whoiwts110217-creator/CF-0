# cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
# Owner-operated, non-admin check for the existing public-safe HP relay.
# This does NOT grant ChatGPT arbitrary Windows access or reveal credentials.
param([switch]$RunPoll, [switch]$OfflineOnly, [switch]$MaintenanceAudit)
$ErrorActionPreference = 'Stop'
# Dedicated maintenance path: no Python, network, relay work, task changes,
# credential reads, local database access, or public writes.
if ($MaintenanceAudit) {
    if ($RunPoll -or $OfflineOnly) {
        Write-Host 'MAINTENANCE_AUDIT=INVALID_COMBINED_MODE'
        exit 2
    }
    Write-Host 'MAINTENANCE_AUDIT=READ_ONLY'
    $allDisabled = $true
    $observed = 0
    $tasks = @(
        @{Name='CavemanFocusCF0Relay'; Label='RELAY'},
        @{Name='CavemanFocusCF0FastLane'; Label='FAST_LANE'},
        @{Name='CavemanFocusSupervisor'; Label='SUPERVISOR'}
    )
    foreach ($entry in $tasks) {
        $state = 'NOT_VISIBLE'
        try {
            $task = Get-ScheduledTask -TaskName $entry.Name -ErrorAction Stop
            if ($null -ne $task) {
                $state = [string]$task.State
                $observed++
            }
        } catch {
            # Missing/denied enumeration is not evidence a task is disabled.
        }
        if ($state -ne 'Disabled') { $allDisabled = $false }
        Write-Host ('TASK_' + $entry.Label + '=' + $state.ToUpperInvariant())
    }
    if ($allDisabled -and $observed -eq 3) {
        Write-Host 'NAMED_TASKS_PAUSED=OBSERVED'
    } else {
        Write-Host 'NAMED_TASKS_PAUSED=NOT_ESTABLISHED'
    }
    # Only size, no drive letter, user, path, process/command line or token.
    $freeMB = $null
    try {
        $driveRoot = [System.IO.Path]::GetPathRoot($env:LOCALAPPDATA)
        if ([string]::IsNullOrWhiteSpace($driveRoot)) { throw 'No local profile drive' }
        $drive = [System.IO.DriveInfo]::new($driveRoot)
        if ($drive.IsReady) {
            $freeMB = [int64][math]::Floor($drive.AvailableFreeSpace / 1MB)
        }
    } catch {
        # Unknown must remain unknown; never imply the drive is safe to install.
    }
    if ($null -eq $freeMB) {
        Write-Host 'LOCAL_DISK_FREE_MB=UNAVAILABLE'
        Write-Host 'LOCAL_DISK_BELOW_2GIB=UNKNOWN'
    } else {
        Write-Host ('LOCAL_DISK_FREE_MB=' + $freeMB)
        Write-Host ('LOCAL_DISK_BELOW_2GIB=' + $(if ($freeMB -lt 2048) { 'YES' } else { 'NO' }))
    }
    Write-Host 'NOTE=2GIB_IS_A_CAUTION_THRESHOLD_NOT_A_DEPLOYMENT_REQUIREMENT'
    Write-Host 'HP_ORIGIN_PROOF=NOT_ESTABLISHED'
    Write-Host 'SCHEDULER_TO_RECEIPT_PROOF=NOT_ESTABLISHED'
    Write-Host 'TASK_OR_PROCESS_CHANGES=NONE'
    Write-Host 'NEXT=Keep maintenance pause until the owner separately approves restart after preserving recovery data.'
    exit 0
}

$taskName = 'CavemanFocusCF0Relay'
$repoRoot = Split-Path -Parent $PSScriptRoot
$worker = Join-Path $PSScriptRoot 'cf_public_relay.py'
$writeback = Join-Path $env:LOCALAPPDATA 'CavemanFocus\CF0Relay\write_token.dpapi'
$rwScript = Join-Path $PSScriptRoot 'cf_public_relay_rw.ps1'

Write-Host '=== Caveman Focus: HP Connection Check ==='
Write-Host 'Mode: existing allowlisted relay only; no arbitrary remote commands.'
if ($OfflineOnly -and $RunPoll) {
    Write-Error 'OfflineOnly and RunPoll cannot be combined.'
    exit 2
}
if (-not (Test-Path -LiteralPath $worker)) {
    Write-Host 'PYTHON_RELAY=MISSING'
    Write-Host 'NEXT=Download or extract the complete CF-0 repository before using this launcher.'
    exit 1
}
$py = Get-Command py.exe -ErrorAction SilentlyContinue
if ($null -eq $py) {
    Write-Host 'PYTHON_LAUNCHER=MISSING'
    Write-Host 'NEXT=Restore the Python 3 launcher on this HP; no paid service is required.'
    exit 1
}
& $py.Source -3 $worker ping-demo
if ($LASTEXITCODE -ne 0) {
    Write-Host 'OFFLINE_PING=FAILED'
    exit 1
}
Write-Host 'OFFLINE_PING=PASSED'
if ($OfflineOnly) {
    Write-Host 'OFFLINE_CHECK=COMPLETE (not evidence of an actual HP connection)'
    exit 0
}

# Scheduler query is read-only; this command never creates/modifies a schedule.
$scheduled = $null
try { $scheduled = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue }
catch { Write-Host 'SCHEDULE_STATUS=UNAVAILABLE' }
if ($null -eq $scheduled) {
    Write-Host 'SCHEDULE=NOT_INSTALLED_OR_NOT_VISIBLE'
} else {
    Write-Host ('SCHEDULE=' + $scheduled.State)
    try {
        $detail = Get-ScheduledTaskInfo -TaskName $taskName -ErrorAction Stop
        Write-Host ('LAST_TASK_RESULT=' + $detail.LastTaskResult)
        if ($detail.LastTaskResult -eq 0) {
            Write-Host 'NOTE=Task exit code zero does not prove an authenticated HP receipt.'
        }
    } catch { Write-Host 'LAST_TASK_RESULT=UNAVAILABLE' }
}
$hasWriteback = Test-Path -LiteralPath $writeback
Write-Host ('WRITEBACK_CONFIGURED=' + $hasWriteback)
if ($RunPoll) {
    Write-Host 'POLL=STARTING (approved public-safe actions only)'
    if ($hasWriteback) {
        & powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $rwScript once
    } else {
        & $py.Source -3 $worker once
    }
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'POLL=FAILED (check HTTPS and local setup; no receipt assumed)'
        exit 1
    }
    Write-Host 'POLL=COMPLETED (verify matching GitHub receipt separately)'
}
if ($null -eq $scheduled) {
    Write-Host 'NEXT=Double-click INSTALL_CF0_RELAY.bat to enable five-minute polling while signed in.'
} elseif (-not $hasWriteback) {
    Write-Host 'NEXT=Double-click ENABLE_CF0_READ_WRITE.bat to activate return receipts with a locally entered GitHub fine-grained token.'
} else {
    Write-Host 'NEXT=Look for a fresh matching receipt in CF-0/command_queue/receipts/.'
}
Write-Host '=== Check complete. No existing data or credentials changed. ==='
exit 0
