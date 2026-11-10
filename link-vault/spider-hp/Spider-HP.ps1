<#
CF-SPIDER-001: free, owner-local Windows UI Automation navigator.
No downloads, external models/APIs, remote listener, startup task, scheduler,
public relay changes, credential access, or arbitrary PowerShell command runner.
Validated local task plans only. Dry-run by default. Interactive owner opt-in.
Requires Windows PowerShell 5.1 and the .NET UIAutomation assemblies bundled
with Windows. Real HP behavior is NOT established by source-only tests.
#>
[CmdletBinding()]
param(
 [ValidateSet('Preflight','Validate','Inspect','Run','Stop','ResetStop')]
 [string]$Mode = 'Preflight',
 [string]$PlanPath = '',
 [ValidateSet('notepad','calculator')]
 [string]$App = 'notepad',
 [switch]$Execute,
 [switch]$OwnerOptIn
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$StopRoot=Join-Path $env:LOCALAPPDATA 'CavemanFocus\Spider'
$StopPath=Join-Path $StopRoot 'STOP'
$Schema='cf0.spider.hp_plan.v1'
$AllowedOps=@('launch','inspect','wait','read','invoke','type_safe','assert_contains')
$AllowedTypes=@('Document','Edit','Button','Text','Pane','Window')
$ForbiddenName='(?i)\b(?:delete|remove|purchase|buy|send|submit|publish|pay|erase|format|sign.out|log.out|grant|permission|password|transfer|clear.history)\b'
function Fail([string]$Reason) { throw $Reason }
function CheckStop {
 if(Test-Path -LiteralPath $StopPath -PathType Leaf) { Fail 'SPIDER_STOP_REQUESTED' }
}
function ValidText([object]$Text,[int]$Max=160) {
 return $Text -is [string] -and $Text.Length -ge 1 -and $Text.Length -le $Max -and
     $Text -match '^[a-zA-Z0-9 _.,:-]+$'
}
function CheckStep($step) {
 if($null -eq $step -or $step -isnot [pscustomobject]){Fail 'INVALID_STEP'}
 $props=@($step.PSObject.Properties.Name)
 if(-not ($props -contains 'op') -or $step.op -notin $AllowedOps) { Fail 'UNSUPPORTED_OPERATION' }
 $allowed=@('op','selector','text','timeout_ms')
 if(@($props|Where-Object {$_ -notin $allowed}).Count -gt 0){Fail 'UNKNOWN_STEP_FIELD'}
 if($step.op -in @('read','invoke','type_safe','assert_contains','wait')){
   if(-not ($props -contains 'selector') -or $step.selector -isnot [pscustomobject]){
      Fail 'MISSING_EXACT_UIA_SELECTOR'
   }
   $sel=$step.selector
   $selProps=@($sel.PSObject.Properties.Name)
   if(@($selProps|Where-Object {$_ -notin @('name','automation_id','control_type')}).Count -gt 0){
     Fail 'UNSUPPORTED_SELECTOR'
   }
   if($selProps.Count -eq 0){Fail 'EMPTY_SELECTOR'}
   $hasExact=($selProps -contains 'name') -or ($selProps -contains 'automation_id')
   if(-not $hasExact -and $step.op -in @('invoke','type_safe','assert_contains')){
      # a type-only selector can match an unexpected control
      Fail 'EXACT_UIA_SELECTOR_REQUIRED'
   }
   foreach($p in $selProps){
     $v=$sel.$p
     if($p -eq 'control_type'){
       if($v -notin $AllowedTypes){Fail 'UNKNOWN_CONTROL_TYPE'}
     }elseif(-not (ValidText $v 110)){Fail 'UNSAFE_SELECTOR_TEXT'}
   }
   if($step.op -eq 'invoke' -and $selProps -contains 'name' -and $sel.name -match $ForbiddenName){
      Fail 'UNSAFE_INVOKE_NAME'
   }
 }
 if($step.op -in @('type_safe','assert_contains')){
  if(-not ($props -contains 'text') -or -not (ValidText $step.text 120)){
     Fail 'UNSAFE_OR_EMPTY_TEXT'
  }
 }
 if($step.op -eq 'type_safe'){
   if($step.selector.control_type -notin @('Edit','Document')){
      Fail 'TYPE_REQUIRES_EDIT_OR_DOCUMENT'
   }
 }
 if($props -contains 'timeout_ms'){
   if($step.timeout_ms -isnot [int] -or $step.timeout_ms -lt 100 -or $step.timeout_ms -gt 10000){
     Fail 'INVALID_WAIT_TIMEOUT'
   }
 }
}
function ReadPlan([string]$Path) {
 if([string]::IsNullOrWhiteSpace($Path)){Fail 'PLAN_PATH_REQUIRED'}
 $full=[System.IO.Path]::GetFullPath($Path)
 if(-not [System.IO.File]::Exists($full)){Fail 'PLAN_NOT_FOUND'}
 if((Get-Item -LiteralPath $full).Length -gt 16000){Fail 'PLAN_TOO_LARGE'}
 $raw=[System.IO.File]::ReadAllText($full,[System.Text.Encoding]::UTF8)
 $p=ConvertFrom-Json -InputObject $raw
 if($null -eq $p -or $p -isnot [pscustomobject]){Fail 'INVALID_PLAN'}
 $fields=@($p.PSObject.Properties.Name)
 if(@($fields|Where-Object {$_ -notin @('schema','app','steps')}).Count -gt 0){
   Fail 'UNKNOWN_PLAN_FIELD'
 }
 if($p.schema -cne $Schema){Fail 'PLAN_SCHEMA_MISMATCH'}
 if($p.app -notin @('notepad','calculator')){Fail 'APP_NOT_ALLOWLISTED'}
 if($p.steps -isnot [array] -or $p.steps.Count -lt 1 -or $p.steps.Count -gt 12){
   Fail 'STEP_COUNT_OUT_OF_RANGE'
 }
 foreach($step in $p.steps){CheckStep $step}
 return $p
}
function GetTarget([string]$TargetApp){
 $names=if($TargetApp -eq 'notepad'){@('Notepad','notepad')}else{@('CalculatorApp','Calculator')}
 $processes=@(Get-Process -ErrorAction SilentlyContinue|Where-Object {
    $names -contains $_.ProcessName -and $_.MainWindowHandle -ne 0
 })
 if($processes.Count -ne 1){Fail ('TARGET_WINDOW_COUNT_'+$processes.Count)}
 return [System.Windows.Automation.AutomationElement]::FromHandle(
    [IntPtr]$processes[0].MainWindowHandle)
}
function ReadyUIA {
 Add-Type -AssemblyName 'UIAutomationClient' -ErrorAction Stop
 Add-Type -AssemblyName 'UIAutomationTypes' -ErrorAction Stop
}
function SelectControl($root,$sel) {
 $conds=New-Object 'System.Collections.Generic.List[System.Windows.Automation.Condition]'
 if($sel.PSObject.Properties.Name -contains 'name'){
   $conds.Add((New-Object System.Windows.Automation.PropertyCondition(
     [System.Windows.Automation.AutomationElement]::NameProperty,[string]$sel.name)))
 }
 if($sel.PSObject.Properties.Name -contains 'automation_id'){
   $conds.Add((New-Object System.Windows.Automation.PropertyCondition(
     [System.Windows.Automation.AutomationElement]::AutomationIdProperty,[string]$sel.automation_id)))
 }
 if($sel.PSObject.Properties.Name -contains 'control_type'){
   $kind=[System.Windows.Automation.ControlType]::($sel.control_type)
   $conds.Add((New-Object System.Windows.Automation.PropertyCondition(
     [System.Windows.Automation.AutomationElement]::ControlTypeProperty,$kind)))
 }
 if($conds.Count -eq 0){Fail 'EMPTY_SELECTOR'}
 $condition=if($conds.Count -eq 1){$conds[0]}else{
   New-Object System.Windows.Automation.AndCondition -ArgumentList (,[System.Windows.Automation.Condition[]]$conds.ToArray())
 }
 $all=$root.FindAll([System.Windows.Automation.TreeScope]::Descendants,$condition)
 if($all.Count -ne 1){Fail ('SELECTOR_COUNT_'+$all.Count)}
 return $all.Item(0)
}
function ReadValue($el) {
 $pat=$null
 if($el.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern,[ref]$pat)){
   return [string]([System.Windows.Automation.ValuePattern]$pat).Current.Value
 }
 if($el.TryGetCurrentPattern([System.Windows.Automation.TextPattern]::Pattern,[ref]$pat)){
   return [string]([System.Windows.Automation.TextPattern]$pat).DocumentRange.GetText(1000)
 }
 Fail 'CONTROL_TEXT_NOT_READABLE'
}
function WaitControl($root,$sel,[int]$Timeout=3500){
 $until=[DateTime]::UtcNow.AddMilliseconds($Timeout)
 do{
   CheckStop
   try{return SelectControl $root $sel}catch{
     if($_.Exception.Message -notmatch '^SELECTOR_COUNT_0$'){throw}
   }
   Start-Sleep -Milliseconds 200
 }while([DateTime]::UtcNow -lt $until)
 Fail 'WAIT_FOR_CONTROL_TIMEOUT'
}
function InspectApp($root){
 $all=$root.FindAll([System.Windows.Automation.TreeScope]::Descendants,
   [System.Windows.Automation.Condition]::TrueCondition)
 $max=[Math]::Min($all.Count,40)
 for($i=0;$i -lt $max;$i++){
   $el=$all.Item($i)
   try {
     # Names may be private user data: print locally ONLY, never transmit/store.
     $name=[string]$el.Current.Name
     $kind=[string]$el.Current.ControlType.ProgrammaticName
     $aid=[string]$el.Current.AutomationId
     Write-Output ("UIA[{0}] Type={1} Id={2} Name={3}" -f $i,$kind,$aid,$name)
   }catch{ Write-Output ('UIA[{0}] stale_element' -f $i) }
 }
 Write-Output ('INSPECTED_UIA_ELEMENTS='+$max)
}
function Run($plan){
 CheckStop
 $launched=$false
 $target=$null
 for($i=0;$i -lt $plan.steps.Count;$i++){
   CheckStop
   $step=$plan.steps[$i];$op=[string]$step.op
   Write-Output ('STEP_START='+$i+':'+$op)
   switch($op){
     launch {
       if($launched){Fail 'DUPLICATE_LAUNCH'}
       # Launch only an existing, built-in application. No extra args or files.
       if($plan.app -eq 'notepad') {
         Start-Process -FilePath 'notepad.exe' -ErrorAction Stop|Out-Null
       }else{
         Start-Process -FilePath 'calc.exe' -ErrorAction Stop|Out-Null
       }
       Start-Sleep -Milliseconds 1000
       $launched=$true
       $target=GetTarget $plan.app
     }
     default {
       if($null -eq $target){$target=GetTarget $plan.app}
       switch($op){
         inspect {InspectApp $target}
         wait {$timeout=if($step.PSObject.Properties.Name -contains 'timeout_ms'){$step.timeout_ms}else{3500};$null=WaitControl $target $step.selector $timeout}
         read { $el=SelectControl $target $step.selector;Write-Output ('CONTROL_TEXT_LENGTH='+(ReadValue $el).Length) }
         assert_contains {
           $el=SelectControl $target $step.selector
           if((ReadValue $el).IndexOf([string]$step.text,[StringComparison]::Ordinal) -lt 0){
             Fail 'TEXT_ASSERTION_FAILED'
           }
         }
         invoke {
           $el=SelectControl $target $step.selector
           $pattern=$null
           if(-not $el.TryGetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern,[ref]$pattern)){
             Fail 'INVOKE_PATTERN_NOT_AVAILABLE'
           }
           ([System.Windows.Automation.InvokePattern]$pattern).Invoke()
         }
         type_safe {
           if($plan.app -ne 'notepad'){Fail 'TYPE_RESTRICTED_TO_NOTEPAD'}
           $el=SelectControl $target $step.selector
           if(-not [string]::IsNullOrWhiteSpace((ReadValue $el))){
             Fail 'REFUSE_TO_OVERWRITE_NONEMPTY_NOTEPAD'
           }
           $el.SetFocus()
           Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
           # ValidText excludes SendKeys special tokens; no Enter or modifiers.
           [System.Windows.Forms.SendKeys]::SendWait([string]$step.text)
         }
         default {Fail 'UNSUPPORTED_OPERATION'}
       }
     }
   }
   Write-Output ('STEP_DONE='+$i+':'+$op)
 }
 Write-Output 'SPIDER_PLAN=OWNER_LOCAL_STEPS_FINISHED_NOT_REMOTE_ATTESTED'
}
try {
 switch($Mode) {
   Preflight {
     Write-Output 'SPIDER_ENGINE=WINDOWS_BUILTIN_UIA_POWERSHELL_5_1'
     Write-Output 'SUBSCRIPTIONS=NONE'
     Write-Output 'PAID_APIS=NONE'
     Write-Output 'MODEL_DOWNLOAD=NONE'
     Write-Output 'NETWORK_LISTENER=NONE'
     Write-Output 'HP_LOCAL_ACTIONS=NOT_STARTED'
     Write-Output ('STOP_PENDING='+[bool](Test-Path -LiteralPath $StopPath))
   }
   Stop {
     if(-not (Test-Path -LiteralPath $StopRoot)){New-Item -ItemType Directory -Path $StopRoot -Force|Out-Null}
     [System.IO.File]::WriteAllText($StopPath,'STOP', [System.Text.Encoding]::ASCII)
     Write-Output 'SPIDER_STOP=REQUESTED_LOCAL'
   }
   ResetStop {
     if(-not $OwnerOptIn){Fail 'OWNER_OPT_IN_REQUIRED_TO_RESET_STOP'}
     Remove-Item -LiteralPath $StopPath -ErrorAction SilentlyContinue
     Write-Output 'SPIDER_STOP=RESET_BY_OWNER'
   }
   Validate {
     $plan=ReadPlan $PlanPath
     Write-Output ('SPIDER_PLAN_VALID=TRUE; APP='+$plan.app+'; STEPS='+$plan.steps.Count)
     Write-Output 'SIDE_EFFECTS=NONE'
   }
   Inspect {
     if(-not ($Execute -and $OwnerOptIn)){Fail 'INSPECT_REQUIRES_EXPLICIT_LOCAL_OPT_IN'}
     CheckStop;ReadyUIA
     $target=GetTarget $App
     InspectApp $target
   }
   Run {
     $plan=ReadPlan $PlanPath
     if(-not ($Execute -and $OwnerOptIn)){
       Write-Output ('SPIDER_PLAN_VALID=TRUE; APP='+$plan.app+'; STEPS='+$plan.steps.Count)
       Write-Output 'DRY_RUN=NO_UI_ACTIONS'
     }else{
       CheckStop;ReadyUIA
       Run $plan
     }
   }
 }
}catch{
 Write-Error ('SPIDER_REFUSED_OR_FAILED='+$_.Exception.Message) -ErrorAction Continue
 exit 2
}
