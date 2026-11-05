# cf.attr.v1=Q0FWRU1BTiBGT0NVU3xLSUFSQSBMWU5OLVJPU0UuIFNNSVRI
# Caveman Focus HP Bridge — Windows account-bound credential setup and scheduler.
# Store token via Windows DPAPI for this Windows user only; no secrets in repo or logs.
param(
    [ValidateSet('configure','doctor','once','install','status','remove')]
    [string] $Mode = 'configure'
)
$ErrorActionPreference = 'Stop'
$StateDir = Join-Path $env:LOCALAPPDATA 'CavemanFocus\HPBridge'
$ConfigPath = Join-Path $StateDir 'config.json'
$SecretPath = Join-Path $StateDir 'token.dpapi'
$BridgeScript = Join-Path $PSScriptRoot 'cf_hp_bridge.py'
$TaskName = 'CavemanFocusHPBridge'

function Read-Config {
    if (-not (Test-Path -LiteralPath $ConfigPath) -or -not (Test-Path -LiteralPath $SecretPath)) {
        throw 'HP bridge is not configured. Run SETUP_HP_BRIDGE_WINDOWS.bat first.'
    }
    $config = Get-Content -LiteralPath $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($config.repo -notmatch '^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$') {
        throw 'Stored private mailbox name is invalid.'
    }
    return $config
}
function Invoke-Bridge([string] $Command) {
    $config = Read-Config
    $secret = Get-Content -LiteralPath $SecretPath -Raw -Encoding UTF8 | ConvertTo-SecureString
    $bstr = [IntPtr]::Zero
    try {
        $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
        $env:CF_BRIDGE_TOKEN = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
        $env:CF_BRIDGE_REPO = [string]$config.repo
        $bridgeArgs = @($BridgeScript, $Command, '--state-dir', $StateDir)
        if ($config.sidecar) { $bridgeArgs += @('--sidecar', [string]$config.sidecar) }
        & py -3 @bridgeArgs
        if ($LASTEXITCODE -ne 0) { throw "Bridge $Command failed (exit $LASTEXITCODE)." }
    }
    finally {
        Remove-Item Env:CF_BRIDGE_TOKEN -ErrorAction SilentlyContinue
        Remove-Item Env:CF_BRIDGE_REPO -ErrorAction SilentlyContinue
        if ($bstr -ne [IntPtr]::Zero) {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
        }
    }
}

switch ($Mode) {
    'configure' {
        New-Item -ItemType Directory -Path $StateDir -Force | Out-Null
        Write-Host 'Use a separate PRIVATE GitHub repository, not public CF-0.'
        $repo = Read-Host 'Private repository (owner/repo)'
        if ($repo -notmatch '^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$') { throw 'Invalid owner/repo.' }
        $token = Read-Host 'Fine-grained token scoped ONLY to this private repo (Contents Read/Write)' -AsSecureString
        if ($token.Length -lt 8) { throw 'Token missing or too short.' }
        # Test the CANDIDATE credential before replacing a working local setup.
        # The token is never written to console, CLI arguments, GitHub or config.
        $bstr = [IntPtr]::Zero
        try {
            $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($token)
            $env:CF_BRIDGE_TOKEN = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
            $env:CF_BRIDGE_REPO = $repo
            & py -3 $BridgeScript doctor --repo $repo --state-dir $StateDir
            if ($LASTEXITCODE -ne 0) { throw 'Private repository connection failed. Prior saved configuration was preserved.' }
        }
        finally {
            Remove-Item Env:CF_BRIDGE_TOKEN -ErrorAction SilentlyContinue
            Remove-Item Env:CF_BRIDGE_REPO -ErrorAction SilentlyContinue
            if ($bstr -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }
        }
        $sidecar = Read-Host 'Optional original Sidecar folder containing domino.py (Enter to skip)'
        if ($sidecar) {
            $sidecar = [string](Resolve-Path -LiteralPath $sidecar -ErrorAction Stop)
            if (-not (Test-Path -LiteralPath (Join-Path $sidecar 'domino.py') -PathType Leaf)) {
                throw 'Sidecar path does not contain domino.py. Prior configuration preserved.'
            }
        }
        # Save only after repository privacy, token access and optional local path
        # have all been validated. DPAPI encryption is bound to this Windows user.
        $token | ConvertFrom-SecureString | Set-Content -LiteralPath $SecretPath -Encoding UTF8
        @{repo=$repo; sidecar=$sidecar; version=2} | ConvertTo-Json | Set-Content -LiteralPath $ConfigPath -Encoding UTF8
        Write-Host 'Private connection validated. Encrypted token saved for this Windows user.'
    }
    'doctor' { Invoke-Bridge 'doctor' }
    'once' { Invoke-Bridge 'once' }
    'install' {
        Invoke-Bridge 'doctor'
        # Interactive Windows-user context is necessary to decrypt the user-bound DPAPI token.
        # Runs periodically while that Windows user is logged in, even if PowerShell is closed.
        $user = [Security.Principal.WindowsIdentity]::GetCurrent().Name
        $quotedScript = '"' + $PSCommandPath.Replace('"','') + '"'
        $argument = '-NoProfile -NonInteractive -ExecutionPolicy Bypass -File ' + $quotedScript + ' once'
        $action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $argument -WorkingDirectory $PSScriptRoot
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 15) -RepetitionDuration (New-TimeSpan -Days 365)
        $principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
        $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 3) -MultipleInstances IgnoreNew -StartWhenAvailable
        Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
        Get-ScheduledTask -TaskName $TaskName | Select-Object TaskName,State | Format-List
        Write-Host 'Schedule added for current signed-in Windows user only. Actual scheduled execution still needs verification.'
    }
    'status' {
        if (Test-Path -LiteralPath $ConfigPath) {
            $config = Get-Content -LiteralPath $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
            Write-Host ('Configured private mailbox: ' + $config.repo)
        }
        else { Write-Host 'No local mailbox configuration.' }
        Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue |
            Select-Object TaskName,State | Format-List
        Get-ScheduledTaskInfo -TaskName $TaskName -ErrorAction SilentlyContinue |
            Select-Object LastRunTime,LastTaskResult,NextRunTime | Format-List
    }
    'remove' {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
        Write-Host 'Scheduled task removed. Your private credential and historical local ledger were left intact.'
    }
}
