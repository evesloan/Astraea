param([string]$Script,[string]$RunName,[int]$Limit=90)
$ErrorActionPreference='Stop'
$base=Split-Path $PSScriptRoot
$project=Join-Path $base 'Astraea-construction-6c52b7a8\Game'
$engine=Join-Path $base 'astraea-e3af0334-inspection-20261022\engine\Godot_v4.6.3-stable_win64.exe'
if($Script -notlike 'res://visible_resource_budget_20261026/*'){throw 'Wrong focused scope'}
if($RunName -notmatch '^performance-[a-z0-9-]+$'){throw 'Wrong output name'}
if(@(Get-CimInstance Win32_Process|Where-Object {$_.Name -match 'godot|astraea|blender|msbuild|ninja'}).Count){throw 'Competing process'}
if((Get-FileHash -LiteralPath $engine).Hash -ne 'EF90E929BA1A6A4322860285D97F40F4AA349C90329A91B0E8B55B8DF0F4CB00'){throw 'Engine hash'}
if((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB -lt 8){throw 'Starting RAM headroom'}
$run=Join-Path $PSScriptRoot $RunName
if(Test-Path -LiteralPath $run){throw 'Prior outcome must be inspected'}
New-Item -ItemType Directory -Path $run|Out-Null
$proc=Start-Process -FilePath $engine -WorkingDirectory $project -WindowStyle Hidden -PassThru -ArgumentList @('--path',('"'+$project+'"'),'--script',$Script,'--',('--output="'+$run+'\result.json"')) -RedirectStandardOutput ($run+'\stdout.log') -RedirectStandardError ($run+'\stderr.log')
$proc.Id|Set-Content -LiteralPath ($run+'\pid.txt');$start=[DateTime]::UtcNow;$reason='exit';$peak=0
while(-not $proc.HasExited){
 $proc.Refresh();$free=(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB;$peak=[Math]::Max($peak,$proc.PrivateMemorySize64)
 if($free -lt 5 -or $proc.PrivateMemorySize64 -gt 4GB -or ([DateTime]::UtcNow-$start).TotalSeconds -gt $Limit){$reason='safety_stop';Stop-Process -Id $proc.Id;break}
 $errorText=Get-Content -LiteralPath ($run+'\stderr.log') -Raw -ErrorAction SilentlyContinue
 if($errorText -match 'SCRIPT ERROR|Element limit reached|Assertion failed'){$reason='engine_error';Stop-Process -Id $proc.Id;break}
 Start-Sleep -Milliseconds 500
}
$proc.WaitForExit()
@{reason=$reason;exit_code=$proc.ExitCode;elapsed=([DateTime]::UtcNow-$start).TotalSeconds;peak_private_bytes=$peak}|ConvertTo-Json|Set-Content -LiteralPath ($run+'\monitor.json')
Get-Content -LiteralPath ($run+'\monitor.json')
Get-Content -LiteralPath ($run+'\stderr.log')
if(Test-Path -LiteralPath ($run+'\result.json')){Get-Content -LiteralPath ($run+'\result.json')}
