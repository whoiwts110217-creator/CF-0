# CF-0 HP control — disposable Windows Task Scheduler primitive probe.
# Only creates one uniquely named harmless task on the ephemeral CI machine.
# No CF-0 relay, bridge, Fast Lane, Supervisor, credential, or user task is touched.
$ErrorActionPreference = 'Stop'
$taskPath = '\'
$taskName = 'CF0_HP_CI_Disposable_' + ([guid]::NewGuid().ToString('N'))
$created = $false

function Assert-True([bool]$condition, [string]$message) {
    if (-not $condition) { throw $message }
}
function Snapshot {
    $t = Get-ScheduledTask -TaskPath $taskPath -TaskName $taskName -ErrorAction Stop
    Assert-True ($t.TaskPath -eq $taskPath) 'Wrong task path'
    Assert-True ($t.TaskName -eq $taskName) 'Wrong task name'
    Assert-True ($t.Principal.RunLevel.ToString() -eq 'Limited') 'Elevated task detected'
    $current = [Security.Principal.WindowsIdentity]::GetCurrent()
    $taskUser = [string]$t.Principal.UserId
    Assert-True (($taskUser -ieq $current.Name) -or ($taskUser -ieq $current.User.Value)) 'Wrong task principal'
    Assert-True ($t.Actions.Count -eq 1) 'Unexpected task actions'
    $expected = Join-Path $env:SystemRoot 'System32\cmd.exe'
    Assert-True ($t.Actions[0].Execute -ieq $expected) 'Unexpected executable'
    Assert-True ($t.Actions[0].Arguments -eq '/c exit 0') 'Unexpected arguments'
    $identity = [ordered]@{
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
    $encoded = ConvertTo-Json -InputObject $identity -Depth 10 -Compress
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $digest = [BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($encoded))).Replace('-','').ToLowerInvariant()
    } finally { $sha.Dispose() }
    return @{state=[string]$t.State;digest=$digest;task=$t}
}
function Wait-State([string[]]$allowed) {
    for ($i=0; $i -lt 12; $i++) {
        $snap = Snapshot
        if ($allowed -contains $snap.state) { return $snap }
        Start-Sleep -Milliseconds 250
    }
    throw ('Task state did not match expected: ' + ($allowed -join ','))
}

try {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $action = New-ScheduledTaskAction -Execute (Join-Path $env:SystemRoot 'System32\cmd.exe') -Argument '/c exit 0'
    # Scheduled far in the future: the task MUST NOT run during this test.
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddHours(8)
    $principal = New-ScheduledTaskPrincipal -UserId $identity.Name -LogonType Interactive -RunLevel Limited
    Register-ScheduledTask -TaskPath $taskPath -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal | Out-Null
    $created = $true
    $initial = Wait-State @('Ready', 'Queued')
    $second = Snapshot
    Assert-True ($second.digest -eq $initial.digest) 'Identity changed between two readbacks'
    Disable-ScheduledTask -TaskPath $taskPath -TaskName $taskName -ErrorAction Stop | Out-Null
    $disabled = Wait-State @('Disabled')
    Assert-True ($disabled.digest -eq $initial.digest) 'Identity changed when disabling'
    Enable-ScheduledTask -TaskPath $taskPath -TaskName $taskName -ErrorAction Stop | Out-Null
    $enabled = Wait-State @('Ready', 'Queued')
    Assert-True ($enabled.digest -eq $initial.digest) 'Identity changed when enabling'
    Write-Output 'WINDOWS_DISPOSABLE_TASK_PROBE=PASSED'
    Write-Output 'SCOPE=ephemeral_ci_only'
    Write-Output 'REAL_HP_DEPLOYMENT=NOT_TESTED'
} finally {
    if ($created) {
        Unregister-ScheduledTask -TaskPath $taskPath -TaskName $taskName -Confirm:$false -ErrorAction Stop
        $left = Get-ScheduledTask -TaskPath $taskPath -TaskName $taskName -ErrorAction SilentlyContinue
        Assert-True ($null -eq $left) 'Disposable task cleanup failed'
    }
}
