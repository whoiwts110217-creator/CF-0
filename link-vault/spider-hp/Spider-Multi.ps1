<#
CF-SPIDER-001: bounded free multi-app task chain for existing Spider HP walker.
No models/services/downloads, no arbitrary shell, no network, no schedule.
Runs ONLY bundled reviewed plans in a fixed order, local opt-in only.
#>
[CmdletBinding()]
param(
 [ValidateSet('Preflight','Validate','Run','Stop')]
 [string]$Mode='Preflight',
 [string]$QueuePath='',
 [switch]$Execute,
 [switch]$OwnerOptIn
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$engine=Join-Path $PSScriptRoot 'Spider-HP.ps1'
$sample=Join-Path $PSScriptRoot 'spider-multi-demo.json'
$plans=@('notepad-inspect.json','calculator-inspect.json','notepad-type-safe.json')
function Refuse([string]$why){throw $why}
function GetQueue {
 $path=if($QueuePath){[System.IO.Path]::GetFullPath($QueuePath)}else{$sample}
 if(-not [System.IO.File]::Exists($path)){Refuse 'QUEUE_NOT_FOUND'}
 if((Get-Item -LiteralPath $path).Length -gt 4096){Refuse 'QUEUE_OVERSIZE'}
 $p=ConvertFrom-Json -InputObject ([System.IO.File]::ReadAllText($path))
 if($p.schema -cne 'cf0.spider.hp_queue.v1'){Refuse 'INVALID_QUEUE_SCHEMA'}
 $names=@($p.PSObject.Properties.Name)
 if(@($names|Where-Object {$_ -notin @('schema','plans')}).Count -gt 0){Refuse 'UNKNOWN_QUEUE_FIELD'}
 if($p.plans -isnot [array] -or $p.plans.Count -lt 1 -or $p.plans.Count -gt 5){
   Refuse 'QUEUE_COUNT_OUT_OF_RANGE'
 }
 foreach($name in $p.plans){
   if($name -isnot [string] -or $name -cnotin $plans){Refuse 'PLAN_NOT_ALLOWLISTED'}
 }
 return $p
}
try{
 if($Mode -eq 'Stop'){
   & powershell.exe -NoProfile -NonInteractive -File $engine -Mode Stop
   if($LASTEXITCODE -ne 0){Refuse 'STOP_COMMAND_FAILED'}
   exit 0
 }
 if($Mode -eq 'Preflight'){
   Write-Output 'SPIDER_MULTI=FREE_WINDOWS_NATIVE'
   Write-Output 'SCHEDULE=NONE'
   Write-Output 'MODEL_COST=ZERO'
   Write-Output 'HP_LOCAL_ACTIONS=NOT_STARTED'
   exit 0
 }
 $queue=GetQueue
 foreach($name in $queue.plans){
   $plan=Join-Path $PSScriptRoot $name
   & powershell.exe -NoProfile -NonInteractive -File $engine -Mode Validate -PlanPath $plan
   if($LASTEXITCODE -ne 0){Refuse ('INVALID_BUNDLED_PLAN_'+$name)}
 }
 Write-Output ('QUEUE_VALID=TRUE; PLANS='+$queue.plans.Count)
 if($Mode -eq 'Validate'){Write-Output 'SIDE_EFFECTS=NONE';exit 0}
 if(-not ($Execute -and $OwnerOptIn)){
   Write-Output 'DRY_RUN=NO_UI_ACTIONS';exit 0
 }
 foreach($name in $queue.plans){
   # Reuse the same native UIA engine/STOP gate; never reimplement a second driver.
   $plan=Join-Path $PSScriptRoot $name
   Write-Output ('RUNNING_REVIEWED_PLAN='+$name)
   & powershell.exe -NoProfile -File $engine -Mode Run -PlanPath $plan -Execute -OwnerOptIn
   if($LASTEXITCODE -ne 0){Refuse ('PLAN_FAILED_STOP_CHAIN_'+$name)}
   Write-Output ('REVIEWED_PLAN_FINISHED='+$name)
 }
 Write-Output 'MULTI_PLAN_FINISHED=OWNER_LOCAL_NOT_REMOTE_ATTESTED'
}catch{
 Write-Error ('SPIDER_MULTI_REFUSED_OR_FAILED='+$_.Exception.Message) -ErrorAction Continue
 exit 2
}
