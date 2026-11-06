# cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
# CF-0 READ/WRITE: use the existing public-safe relay, no new command interpreter.
# A private fine-grained GitHub token is DPAPI-encrypted for this Windows user.
param([ValidateSet('enable','once','status','disable','selftest')][string]$Mode='enable')
$ErrorActionPreference='Stop'
$RepoName='whoiwts110217-creator/CF-0'
$TaskName='CavemanFocusCF0Relay'
$StateDir=Join-Path $env:LOCALAPPDATA 'CavemanFocus\CF0Relay'
$SecretFile=Join-Path $StateDir 'write_token.dpapi'
$Worker=Join-Path $PSScriptRoot 'cf_public_relay.py'
$Root=Split-Path -Parent $PSScriptRoot

function Plaintext([Security.SecureString] $Secret) {
    $ptr=[IntPtr]::Zero
    try {
        $ptr=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($Secret)
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    }
    finally {
        if ($ptr -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
    }
}
# Set-Content adds a line ending to the encrypted DPAPI text. Passing the
# -Raw value directly to ConvertTo-SecureString can raise FormatException.
# Normalize file-text line endings; never trim or log the decrypted token.
function Unprotect-TokenFromFile([string] $Path) {
    $encryptedText=(Get-Content -LiteralPath $Path -Raw -Encoding UTF8).Trim()
    if ([string]::IsNullOrWhiteSpace($encryptedText)) {
        throw 'Saved encrypted GitHub token is empty. Re-run ENABLE_CF0_READ_WRITE.bat under the same Windows account.'
    }
    try {
        return ConvertTo-SecureString -String $encryptedText -ErrorAction Stop
    }
    catch {
        throw 'Saved encrypted GitHub token cannot be decrypted by this Windows account. Re-run ENABLE_CF0_READ_WRITE.bat locally; never share the token.'
    }
}

function New-WriteProbe([Security.SecureString] $Secret) {
    $plain=Plaintext $Secret
    try {
        $headers=@{
            'Authorization'='Bearer '+$plain
            'Accept'='application/vnd.github+json'
            'X-GitHub-Api-Version'='2022-11-28'
            'User-Agent'='CF0-HP-ReadWrite-Setup/1.0'
        }
        $meta=Invoke-RestMethod -Method Get -Uri ('https://api.github.com/repos/'+$RepoName) -Headers $headers -TimeoutSec 20
        if ($meta.full_name -cne $RepoName) { throw 'wrong_repository' }
        $id=[guid]::NewGuid().ToString()
        $receipt=@{
            v=1; id=$id; kind='cf0_hp_writeback_probe'; status='received'
            result=@{ public_safe=$true; note='CF-0 writeback verified; no device or user metadata' }
        } | ConvertTo-Json -Depth 5 -Compress
        $contents=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($receipt))
        $body=@{message=('CF-0 HP return-channel proof '+$id);branch='main';content=$contents} | ConvertTo-Json -Compress
        $url='https://api.github.com/repos/'+$RepoName+'/contents/command_queue/receipts/'+$id+'.json'
        $null=Invoke-RestMethod -Method Put -Uri $url -Headers $headers -Body $body -ContentType 'application/json' -TimeoutSec 25
        return $id
    }
    catch {
        # Do not print error response bodies or request headers; they may contain secrets.
        throw 'GitHub authorization or test receipt failed. Existing schedule/credentials unchanged.'
    }
    finally { $plain=$null; $headers=$null }
}
function Invoke-Worker {
    if (-not (Test-Path -LiteralPath $SecretFile)) {
        throw 'Writeback not configured. Run ENABLE_CF0_READ_WRITE.bat first.'
    }
    if (-not (Test-Path -LiteralPath $Worker)) { throw 'Missing Python relay.' }
    $stored=Unprotect-TokenFromFile $SecretFile
    $plain=Plaintext $stored
    try {
        $env:CF_RELAY_GITHUB_TOKEN=$plain
        $notepadOptIn=Join-Path $StateDir 'allow_notepad.flag'
        if (Test-Path -LiteralPath $notepadOptIn) { $env:CF_ALLOW_NOTEPAD='1' }
        $py=Get-Command py.exe -ErrorAction Stop
        & $py.Source -3 $Worker once
        if ($LASTEXITCODE -ne 0) { throw 'Relay process failed.' }
    }
    finally {
        Remove-Item Env:CF_RELAY_GITHUB_TOKEN -ErrorAction SilentlyContinue
        Remove-Item Env:CF_ALLOW_NOTEPAD -ErrorAction SilentlyContinue
        $plain=$null
    }
}
# Self-test is fully offline and uses a disposable dummy string.
# It exercises the same DPAPI save/read path used by the scheduled worker.
if ($Mode -eq 'selftest') {
    $testPath=Join-Path ([IO.Path]::GetTempPath()) ('cf0-secret-roundtrip-'+[guid]::NewGuid().ToString('N')+'.txt')
    try {
        $dummy=ConvertTo-SecureString 'CF0DummySecretForOfflineRoundTrip' -AsPlainText -Force
        $cipher=$dummy | ConvertFrom-SecureString
        Set-Content -LiteralPath $testPath -Value $cipher -Encoding UTF8
        $readBack=Unprotect-TokenFromFile $testPath
        if ((Plaintext $readBack) -cne 'CF0DummySecretForOfflineRoundTrip') {
            throw 'Encrypted credential round-trip returned unexpected data.'
        }
        Write-Host 'DPAPI_TOKEN_ROUNDTRIP=PASSED (offline test with disposable dummy data)'
    }
    finally {
        if (Test-Path -LiteralPath $testPath) { Remove-Item -LiteralPath $testPath -Force }
    }
    exit 0
}
if ($Mode -eq 'status') {
    $task=Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    $configured=(Test-Path -LiteralPath $SecretFile)
    $usingWrapper=$false
    if ($null -ne $task) {
        $usingWrapper=($task.Actions | Where-Object { $_.Arguments -like '*cf_public_relay_rw.ps1*' }).Count -gt 0
    }
    Write-Host ('Encrypted writeback token present: '+$configured)
    Write-Host ('Scheduled read/write wrapper active: '+$usingWrapper)
    if ($null -ne $task) {
        $task | Select-Object TaskName,State | Format-List
        Get-ScheduledTaskInfo -TaskName $TaskName | Select-Object LastRunTime,LastTaskResult,NextRunTime | Format-List
    }
    exit 0
}
if ($Mode -eq 'once') { Invoke-Worker; exit 0 }
$task=Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
$py=Get-Command py.exe -ErrorAction Stop
if ($Mode -eq 'disable') {
    # Restore original read-only polling action. Do not delete the local ledger.
    $action=New-ScheduledTaskAction -Execute $py.Source -Argument ('-3 "'+$Worker+'" once') -WorkingDirectory $Root
    Set-ScheduledTask -TaskName $TaskName -Action $action | Out-Null
    if (Test-Path -LiteralPath $SecretFile) { Remove-Item -LiteralPath $SecretFile -Force }
    Write-Host 'Writeback disabled. Existing tokenless read-only schedule and local history preserved.'
    exit 0
}
if (-not (Test-Path -LiteralPath $Worker)) { throw 'Missing Python relay.' }
Write-Host 'Enable public-safe READ/WRITE for the existing CF-0 task. No new schedule is created.'
Write-Host 'Create a GitHub fine-grained token restricted to CF-0: Contents Read and write.'
Write-Host 'Warning: GitHub Contents permissions apply to the repository, not just the receipts folder.'
Write-Host 'Never paste your token into ChatGPT or any GitHub file/issue.'
$secret=Read-Host 'GitHub fine-grained token (input hidden)' -AsSecureString
if ($null -eq $secret -or $secret.Length -lt 12) { throw 'Token missing or too short.' }
# A real PUT proves authenticated GitHub write access BEFORE changing the Windows schedule.
$probeId=New-WriteProbe $secret
New-Item -ItemType Directory -Path $StateDir -Force | Out-Null
$previous=$null
if (Test-Path -LiteralPath $SecretFile) { $previous=Get-Content -LiteralPath $SecretFile -Raw -Encoding UTF8 }
try {
    # Windows DPAPI: encrypted at rest for this account on this computer.
    $encrypted=$secret | ConvertFrom-SecureString
    Set-Content -LiteralPath $SecretFile -Value $encrypted -Encoding UTF8
    $quoted='"'+$PSCommandPath.Replace('"','')+'"'
    $args='-NoProfile -NonInteractive -ExecutionPolicy Bypass -File '+$quoted+' once'
    $action=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $args -WorkingDirectory $Root
    Set-ScheduledTask -TaskName $TaskName -Action $action | Out-Null
}
catch {
    if ($null -ne $previous) { Set-Content -LiteralPath $SecretFile -Value $previous -Encoding UTF8 }
    elseif (Test-Path -LiteralPath $SecretFile) { Remove-Item -LiteralPath $SecretFile -Force }
    throw 'Credential/schedule update failed; previous credential restored if present.'
}
Write-Host ('Public GitHub HP write proof: https://github.com/'+$RepoName+'/blob/main/command_queue/receipts/'+$probeId+'.json')
Write-Host 'Existing five-minute task upgraded. Logs and original local SQLite history retained.'
Write-Host 'A future scheduled poll will publish allowed local receipts. Task Scheduler execution remains to be verified.'
