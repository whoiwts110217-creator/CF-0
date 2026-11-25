# cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
# One Windows setup for the CF-0 public relay. Safe to run again.
# The five-minute signed-in task is created by relay/install_task.ps1.
# Receipt posting uses the same DPAPI file as relay/cf_public_relay_rw.ps1.
param([switch]$Uninstall)
$ErrorActionPreference = 'Stop'

$TaskName = 'CavemanFocusCF0Relay'
$RepoName = 'whoiwts110217-creator/CF-0'
$RepoId = '1444521490'
$RepoBranch = 'main'
$CloneUrl = 'https://github.com/whoiwts110217-creator/CF-0.git'
$InstallDir = Join-Path $env:USERPROFILE 'CavemanFocus\CF-0'
$StateDir = Join-Path $env:LOCALAPPDATA 'CavemanFocus\CF0Relay'
$SecretFile = Join-Path $StateDir 'write_token.dpapi'
$MinimumPython = [version]'3.10'
$script:PythonExe = $null
$script:TokenJustSaved = $false
$script:Steps = [ordered]@{}
$script:Overall = 'FAIL'

function Set-SetupStep([string]$Name, [string]$Status, [string]$Detail) {
    $script:Steps[$Name] = @{ Status = $Status; Detail = $Detail }
    Write-Host ($Name + ': ' + $Status)
    if ($Detail) { Write-Host ('  ' + $Detail) }
}

function Write-SetupSummary {
    Write-Host ''
    Write-Host 'CF-0 setup summary'
    Write-Host '------------------'
    foreach ($name in $script:Steps.Keys) {
        $row = $script:Steps[$name]
        Write-Host ('{0,-22} {1}' -f $name, $row.Status)
        if ($row.Detail) { Write-Host ('  ' + $row.Detail) }
    }
    $overall = 'PASS'
    foreach ($row in $script:Steps.Values) {
        if ($row.Status -eq 'FAIL') { $overall = 'FAIL' }
    }
    if ($script:Steps.Count -eq 0) { $overall = 'FAIL' }
    $script:Overall = $overall
    Write-Host ('{0,-22} {1}' -f 'OVERALL', $overall)
}

function Update-SessionPath {
    $machine = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $user = [Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = (@($machine, $user, $env:Path) | Where-Object { $_ }) -join ';'
}

function Test-Cf0Origin([string]$Url) {
    if ([string]::IsNullOrWhiteSpace($Url)) { return $false }
    $normalized = $Url.Trim().TrimEnd('/') -replace '\.git$', ''
    $normalized = $normalized -replace '^git@github\.com:', 'https://github.com/'
    $normalized = $normalized -replace '^ssh://git@github\.com/', 'https://github.com/'
    $normalized = $normalized -replace '^https://github\.com/', ''
    return ($normalized -ceq $RepoName)
}

# Same removal as relay/install_task.ps1 remove: the scheduled task only.
function Remove-Cf0RelayTask {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    $still = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($null -ne $still) { throw 'The scheduled task is still present. No files were deleted.' }
    Write-Host 'Removed CF-0 relay schedule; no local history deleted.'
}
# end Remove-Cf0RelayTask

function Install-WithWinget([string]$Id, [string]$Label) {
    $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
    if ($null -eq $winget) {
        throw "Windows Package Manager (winget) is not available, so $Label was not installed automatically."
    }
    Write-Host "Installing $Label ($Id) with winget. This can take a few minutes. You do not need to buy anything."
    & $winget.Source install --id $Id -e --scope user --accept-package-agreements --accept-source-agreements --disable-interactivity | Out-Host
    $userScope = $LASTEXITCODE
    Update-SessionPath
    if ($userScope -eq 0) { return }
    Write-Host "The user-scope install did not finish (exit $userScope). Trying the normal winget install."
    & $winget.Source install --id $Id -e --accept-package-agreements --accept-source-agreements --disable-interactivity | Out-Host
    Update-SessionPath
}

function Find-PyExe {
    $cmd = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($null -ne $cmd) { return $cmd.Source }
    $candidates = @(
        (Join-Path $env:LocalAppData 'Programs\Python\Launcher\py.exe'),
        (Join-Path $env:WINDIR 'py.exe'),
        'C:\Windows\py.exe'
    )
    foreach ($path in $candidates) {
        if (Test-Path -LiteralPath $path) {
            $env:Path = (Split-Path -Parent $path) + ';' + $env:Path
            return $path
        }
    }
    return $null
}

function Find-GitExe {
    $cmd = Get-Command git.exe -ErrorAction SilentlyContinue
    if ($null -ne $cmd) { return $cmd.Source }
    $candidates = @(
        'C:\Program Files\Git\cmd\git.exe',
        (Join-Path $env:LocalAppData 'Programs\Git\cmd\git.exe')
    )
    foreach ($path in $candidates) {
        if (Test-Path -LiteralPath $path) {
            $env:Path = (Split-Path -Parent $path) + ';' + $env:Path
            return $path
        }
    }
    return $null
}

function Get-PythonVersion([string]$Exe) {
    $text = (& $Exe -3 -c "import sys; print(sys.version.split()[0])" | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($text)) { return $null }
    $line = ($text -split '\r?\n' | Where-Object { $_ }) | Select-Object -Last 1
    try { return [version]$line } catch { return $null }
}

function Ensure-Python {
    try {
        $exe = Find-PyExe
        $version = $null
        if ($exe) { $version = Get-PythonVersion $exe }
        if (-not $exe -or $null -eq $version -or $version -lt $MinimumPython) {
            $found = 'Python 3.10 or newer was not found (the py launcher is required).'
            if ($version) { $found = "Found Python $version. The relay needs Python 3.10 or newer." }
            Write-Host $found
            Write-Host 'Setup will try to install Python 3.13, the version used by CF-0 tests.'
            Install-WithWinget 'Python.Python.3.13' 'Python 3.13'
            $exe = Find-PyExe
            if ($exe) { $version = Get-PythonVersion $exe }
        }
        if (-not $exe -or $null -eq $version -or $version -lt $MinimumPython) {
            throw @"
Python 3.10 or newer is still missing. Nothing was deleted.
Install it from https://www.python.org/downloads/windows/ and include the py launcher, then run SETUP_CF0.bat again.
"@
        }
        $script:PythonExe = $exe
        Set-SetupStep 'Python' 'PASS' "Python $version via py.exe. The relay needs Python 3.10 or newer and no extra packages."
        return $true
    }
    catch {
        Set-SetupStep 'Python' 'FAIL' $_.Exception.Message
        return $false
    }
}

function Ensure-Git {
    try {
        $git = Find-GitExe
        if (-not $git) {
            Write-Host 'Git was not found. Setup needs it to download and update CF-0.'
            Install-WithWinget 'Git.Git' 'Git'
            $git = Find-GitExe
        }
        if (-not $git) {
            throw @"
Git is still missing. Nothing was deleted.
Install it from https://git-scm.com/download/win and run SETUP_CF0.bat again.
"@
        }
        $versionText = (& $git --version | Out-String).Trim()
        Set-SetupStep 'Git' 'PASS' $versionText
        return $true
    }
    catch {
        Set-SetupStep 'Git' 'FAIL' $_.Exception.Message
        return $false
    }
}

function Update-Cf0Repository {
    try {
        $env:GIT_TERMINAL_PROMPT = '0'
        if (-not (Test-Path -LiteralPath $InstallDir)) {
            $parent = Split-Path -Parent $InstallDir
            New-Item -ItemType Directory -Path $parent -Force | Out-Null
            Write-Host "Downloading CF-0 into $InstallDir"
            & git clone --branch $RepoBranch --single-branch $CloneUrl $InstallDir | Out-Host
            if ($LASTEXITCODE -ne 0) { throw 'git clone failed. Nothing was deleted.' }
        }
        elseif (-not (Test-Path -LiteralPath (Join-Path $InstallDir '.git'))) {
            throw "The folder $InstallDir already exists and is not a CF-0 git checkout. Nothing was deleted. Move that folder aside and run setup again."
        }
        else {
            $origin = (& git -C $InstallDir remote get-url origin | Out-String).Trim()
            if ($LASTEXITCODE -ne 0 -or -not (Test-Cf0Origin $origin)) {
                throw "The folder $InstallDir is not a checkout of $RepoName. Nothing was deleted."
            }
            Write-Host "Updating $InstallDir from GitHub $RepoBranch."
            & git -C $InstallDir fetch origin $RepoBranch | Out-Host
            if ($LASTEXITCODE -ne 0) { throw 'git fetch failed. The existing folder was left as-is. Nothing was deleted.' }
            $branch = (& git -C $InstallDir rev-parse --abbrev-ref HEAD | Out-String).Trim()
            if ($branch -cne $RepoBranch) {
                & git -C $InstallDir checkout $RepoBranch | Out-Host
                if ($LASTEXITCODE -ne 0) {
                    throw "Could not switch $InstallDir to $RepoBranch. Local changes were kept. Nothing was deleted."
                }
            }
            & git -C $InstallDir pull --ff-only origin $RepoBranch | Out-Host
            if ($LASTEXITCODE -ne 0) {
                throw "Could not fast-forward $InstallDir to $RepoBranch. Local changes were kept. Nothing was deleted."
            }
        }
        $worker = Join-Path $InstallDir 'relay\cf_public_relay.py'
        if (-not (Test-Path -LiteralPath $worker)) { throw 'The checkout does not contain relay\cf_public_relay.py.' }
        Set-SetupStep 'Repository' 'PASS' $InstallDir
        return $true
    }
    catch {
        Set-SetupStep 'Repository' 'FAIL' $_.Exception.Message
        return $false
    }
}

function Initialize-RelayDatabase {
    try {
        $worker = Join-Path $InstallDir 'relay\cf_public_relay.py'
        & $script:PythonExe -3 $worker status | Out-Host
        if ($LASTEXITCODE -ne 0) { throw 'The relay status command failed, so the local database was not confirmed.' }
        if ($env:CF_RELAY_HOME) { $dbDir = $env:CF_RELAY_HOME } else { $dbDir = Join-Path $env:USERPROFILE '.caveman_focus_relay' }
        $db = Join-Path $dbDir 'relay.sqlite3'
        if (-not (Test-Path -LiteralPath $db)) { throw "The relay did not create $db" }
        Set-SetupStep 'Local database' 'PASS' $db
        return $true
    }
    catch {
        Set-SetupStep 'Local database' 'FAIL' $_.Exception.Message
        return $false
    }
}

function Assert-RepositoryIdentity([object]$Metadata) {
    if ($null -eq $Metadata -or
        [string]$Metadata.full_name -cne $RepoName -or
        [string]$Metadata.id -cne $RepoId -or
        [string]$Metadata.default_branch -cne $RepoBranch) {
        throw 'wrong_repository'
    }
}

function ConvertTo-Plaintext([Security.SecureString]$Secret) {
    $ptr = [IntPtr]::Zero
    try {
        $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($Secret)
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    }
    finally {
        if ($ptr -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
    }
}

# Same GitHub check as relay/cf_public_relay_rw.ps1: identity, then one public
# write proof. Errors are not printed; response bodies can contain secrets.
function New-WriteProbe([Security.SecureString]$Secret) {
    $plain = ConvertTo-Plaintext $Secret
    try {
        $headers = @{
            'Authorization' = 'Bearer ' + $plain
            'Accept' = 'application/vnd.github+json'
            'X-GitHub-Api-Version' = '2022-11-28'
            'User-Agent' = 'CF0-HP-ReadWrite-Setup/1.0'
        }
        $meta = Invoke-RestMethod -Method Get -Uri ('https://api.github.com/repos/' + $RepoName) -Headers $headers -TimeoutSec 20
        Assert-RepositoryIdentity $meta
        $id = [guid]::NewGuid().ToString()
        $receipt = @{
            v = 1; id = $id; kind = 'cf0_hp_writeback_probe'; status = 'received'
            result = @{ public_safe = $true; note = 'CF-0 writeback verified; no device or user metadata' }
        } | ConvertTo-Json -Depth 5 -Compress
        $contents = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($receipt))
        $body = @{ message = ('CF-0 HP return-channel proof ' + $id); branch = $RepoBranch; content = $contents } | ConvertTo-Json -Compress
        $url = 'https://api.github.com/repos/' + $RepoName + '/contents/command_queue/receipts/' + $id + '.json'
        $null = Invoke-RestMethod -Method Put -Uri $url -Headers $headers -Body $body -ContentType 'application/json' -TimeoutSec 25
        return $id
    }
    catch {
        throw 'GitHub authorization or test receipt failed. Existing schedule and saved token were left unchanged.'
    }
    finally { $plain = $null; $headers = $null }
}

function Save-DpapiToken([Security.SecureString]$Secret) {
    New-Item -ItemType Directory -Path $StateDir -Force | Out-Null
    $encrypted = $Secret | ConvertFrom-SecureString
    Set-Content -LiteralPath $SecretFile -Value $encrypted -Encoding UTF8
}

function Read-OptionalToken {
    Write-Host ''
    Write-Host 'Posting receipts back to GitHub needs a fine-grained personal access token.'
    Write-Host 'Create one at https://github.com/settings/personal-access-tokens/new'
    Write-Host "Give it access to this repository only: $RepoName."
    Write-Host 'Permission: Contents, Read and write.'
    Write-Host 'GitHub applies that permission to the whole repository, not only the receipts folder.'
    Write-Host 'Do not grant any other repository. Do not paste the token into chat or into a file in this repo.'
    Write-Host 'Setup stores it with Windows DPAPI for this Windows user, in the file the relay already decrypts.'
    Write-Host 'It is not stored in the repository and it is not stored in plain text.'
    Write-Host 'Press Enter with nothing typed to skip. The relay will still poll, and receipts stay on this PC.'
    for ($attempt = 1; $attempt -le 2; $attempt++) {
        $secret = Read-Host 'GitHub fine-grained token (input hidden; press Enter to skip)' -AsSecureString
        if ($null -eq $secret -or $secret.Length -eq 0) { return $null }
        if ($secret.Length -ge 12) { return $secret }
        Write-Host 'That token is too short. Paste the token again, or press Enter to skip.'
    }
    throw 'Token missing or too short. Nothing was saved.'
}

function Initialize-ReceiptToken {
    try {
        if (Test-Path -LiteralPath $SecretFile) {
            Set-SetupStep 'Receipt token' 'PASS' 'Using the token already saved for this Windows user (DPAPI). It was not printed.'
            return
        }
        $secret = Read-OptionalToken
        if ($null -eq $secret) {
            Set-SetupStep 'Receipt token' 'SKIPPED' 'Receipts stay on this PC until you run setup again and enter a token.'
            return
        }
        $probeId = New-WriteProbe $secret
        Save-DpapiToken $secret
        $script:TokenJustSaved = $true
        $proof = 'https://github.com/' + $RepoName + '/blob/main/command_queue/receipts/' + $probeId + '.json'
        Set-SetupStep 'Receipt token' 'PASS' ('Saved with Windows DPAPI for this user. Public write check: ' + $proof)
    }
    catch {
        Set-SetupStep 'Receipt token' 'FAIL' $_.Exception.Message
    }
}

function Switch-RelayTaskToWriteback {
    $rw = Join-Path $InstallDir 'relay\cf_public_relay_rw.ps1'
    if (-not (Test-Path -LiteralPath $rw)) { throw 'The read/write wrapper is missing from the CF-0 folder.' }
    $quoted = '"' + ($rw.Replace('"', '')) + '"'
    $argument = '-NoProfile -NonInteractive -ExecutionPolicy Bypass -File ' + $quoted + ' once'
    $action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $argument -WorkingDirectory $InstallDir
    Set-ScheduledTask -TaskName $TaskName -Action $action | Out-Null
}

function Install-RelaySchedule {
    try {
        $installer = Join-Path $InstallDir 'relay\install_task.ps1'
        if (-not (Test-Path -LiteralPath $installer)) { throw 'relay\install_task.ps1 is missing from the CF-0 folder.' }
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $installer install | Out-Host
        if ($LASTEXITCODE -ne 0) { throw 'The existing five-minute installer did not finish. Nothing was deleted.' }
        if (Test-Path -LiteralPath $SecretFile) {
            try {
                Switch-RelayTaskToWriteback
            }
            catch {
                if ($script:TokenJustSaved -and (Test-Path -LiteralPath $SecretFile)) {
                    Remove-Item -LiteralPath $SecretFile -Force
                    $script:TokenJustSaved = $false
                    Set-SetupStep 'Receipt token' 'FAIL' 'The token was not kept because the scheduled task could not be pointed at the read/write wrapper. Run setup again.'
                    throw 'The scheduled task was left polling without a saved token. Nothing else was deleted.'
                }
                throw 'The saved token is still there, but the task is polling without posting receipts. Run setup again. Nothing was deleted.'
            }
        }
        $mode = 'Tokenless polling. Receipts stay on this PC.'
        if (Test-Path -LiteralPath $SecretFile) { $mode = 'Receipt posting is on, using the saved DPAPI token.' }
        Set-SetupStep 'Scheduled task' 'PASS' ("CavemanFocusCF0Relay every 5 minutes while you are signed in. " + $mode)
    }
    catch {
        Set-SetupStep 'Scheduled task' 'FAIL' $_.Exception.Message
    }
}

function Invoke-HpStatusCheck {
    $checker = Join-Path ([IO.Path]::GetTempPath()) ('cf0-hp-status-' + [guid]::NewGuid().ToString('N') + '.py')
    $code = @'
import json, sys
sys.path.insert(0, sys.argv[1])
import cf_public_relay as relay
job = relay.make_job("hp_status")
relay.validate(job, job["id"] + ".json")
result = relay.execute(job)
print(json.dumps(result, sort_keys=True))
commands = result.get("commands") or []
ok = (
    result.get("worker") == "online"
    and result.get("policy") == "public-safe"
    and "hp_status" in commands
    and "ping" in commands
    and "open_notepad" in commands
)
raise SystemExit(0 if ok else 1)
'@
    try {
        $utf8 = New-Object System.Text.UTF8Encoding $false
        [System.IO.File]::WriteAllText($checker, $code, $utf8)
        $relayDir = Join-Path $InstallDir 'relay'
        & $script:PythonExe -3 $checker $relayDir | Out-Host
        if ($LASTEXITCODE -ne 0) { throw 'hp_status did not report the relay online.' }
        Set-SetupStep 'hp_status' 'PASS' 'Local self-check passed. Notepad was not opened.'
    }
    catch {
        Set-SetupStep 'hp_status' 'FAIL' $_.Exception.Message
    }
    finally {
        if (Test-Path -LiteralPath $checker) { Remove-Item -LiteralPath $checker -Force -ErrorAction SilentlyContinue }
    }
}

Write-Host 'CF-0 relay setup'
Write-Host 'This is safe to run again. It does not delete your database, token, or files.'
if ($Uninstall) {
    try {
        Remove-Cf0RelayTask
        Set-SetupStep 'Scheduled task' 'PASS' 'CavemanFocusCF0Relay was removed. The database, token, and repository folder were kept.'
        Set-SetupStep 'Local database' 'KEPT' 'The SQLite ledger was not deleted.'
        Set-SetupStep 'Receipt token' 'KEPT' 'The encrypted token file was not deleted.'
        Set-SetupStep 'Repository folder' 'KEPT' $InstallDir
    }
    catch {
        Set-SetupStep 'Scheduled task' 'FAIL' $_.Exception.Message
    }
    Write-SetupSummary
    if ($script:Overall -ne 'PASS') { exit 1 }
    exit 0
}

$ready = $true
if (-not (Ensure-Python)) { $ready = $false }
elseif (-not (Ensure-Git)) { $ready = $false }
elseif (-not (Update-Cf0Repository)) { $ready = $false }
elseif (-not (Initialize-RelayDatabase)) { $ready = $false }
if ($ready) {
    Initialize-ReceiptToken
    Install-RelaySchedule
    Invoke-HpStatusCheck
}
Write-SetupSummary
if ($script:Overall -ne 'PASS') { exit 1 }
exit 0
