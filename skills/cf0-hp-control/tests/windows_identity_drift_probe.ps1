# CF-0 config-pin verification: disposable Windows runner ONLY.
# No real HP task, private file or network command is used.
$ErrorActionPreference = 'Stop'
$taskPath = '\'
$taskName = 'CF0_HP_CI_Pin_' + ([guid]::NewGuid().ToString('N'))
$created = $false

function Assert-True([bool]$ok, [string]$why) { if (-not $ok) { throw $why } }
function Snapshot {
    # One deterministic canonical task-configuration fingerprint.
    # Independently assert exact action/principal/trigger values below;
    # do NOT pretend two identical hash routines are independent validation.
    $t = Get-ScheduledTask -TaskPath $taskPath -TaskName $taskName -ErrorAction Stop
    Assert-True ($t.TaskPath -eq $taskPath -and $t.TaskName -eq $taskName) 'Unexpected task locator'
    Assert-True ($t.Actions.Count -eq 1) 'Unexpected action count'
    Assert-True ([string]$t.Principal.RunLevel -eq 'Limited') 'Unexpected task runlevel'
    $fingerprint = [ordered]@{
        name = [string]$t.TaskName
        path = [string]$t.TaskPath
        principal = [string]$t.Principal.UserId
        logon = [string]$t.Principal.LogonType
        runlevel = [string]$t.Principal.RunLevel
        actions = @($t.Actions | ForEach-Object {
          [ordered]@{execute=[string]$_.Execute;arguments=[string]$_.Arguments;working_directory=[string]$_.WorkingDirectory}
        })
        triggers = @($t.Triggers | ForEach-Object { $_ | ConvertTo-Json -Depth 5 -Compress })
    }
    $encoded = ConvertTo-Json -InputObject $fingerprint -Depth 10 -Compress
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { $digest = [BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($encoded))).Replace('-','').ToLowerInvariant() }
    finally { $sha.Dispose() }
    return @{state=[string]$t.State;digest=$digest;action=[string]$t.Actions[0].Arguments}
}

try {
    $user = [Security.Principal.WindowsIdentity]::GetCurrent()
    $exe = Join-Path $env:SystemRoot 'System32\cmd.exe'
    $original = New-ScheduledTaskAction -Execute $exe -Argument '/c exit 0'
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddHours(8)
    $principal = New-ScheduledTaskPrincipal -UserId $user.Name -LogonType Interactive -RunLevel Limited
    Register-ScheduledTask -TaskPath $taskPath -TaskName $taskName -Action $original -Trigger $trigger -Principal $principal | Out-Null
    $created = $true

    $before = Snapshot
    $review = Snapshot
    Assert-True ($before.digest -eq $review.digest) 'Repeated readback changed task identity'
    Assert-True ($before.action -eq '/c exit 0') 'Unexpected original command'

    # Simulate a changed command without ever launching it.
    $changedAction = New-ScheduledTaskAction -Execute $exe -Argument '/c exit 1'
    Set-ScheduledTask -TaskPath $taskPath -TaskName $taskName -Action $changedAction | Out-Null
    $different = Snapshot
    Assert-True ($different.action -eq '/c exit 1') 'Test action did not change'
    Assert-True ($different.digest -ne $before.digest) 'Changing task command did not invalidate identity pin'
    $differentReview = Snapshot
    Assert-True ($different.digest -eq $differentReview.digest) 'Changed configuration did not stabilize across readbacks'

    # Restore original action, verify original identity, then delete disposable task.
    Set-ScheduledTask -TaskPath $taskPath -TaskName $taskName -Action $original | Out-Null
    $restored = Snapshot
    Assert-True ($restored.digest -eq $before.digest) 'Restored task identity did not match original'
    Write-Output 'WINDOWS_CONFIG_PIN_DRIFT=PASSED'
    Write-Output 'REAL_HP_DEPLOYMENT=NOT_TESTED'
} finally {
    if ($created) {
        Unregister-ScheduledTask -TaskPath $taskPath -TaskName $taskName -Confirm:$false -ErrorAction Stop
        Assert-True ($null -eq (Get-ScheduledTask -TaskPath $taskPath -TaskName $taskName -ErrorAction SilentlyContinue)) 'Disposable task cleanup failed'
    }
}
